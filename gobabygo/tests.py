import base64
import hashlib
from datetime import timedelta
from urllib.parse import parse_qs, urlsplit

from asgiref.sync import async_to_sync
from django.conf import settings
from django.test import TransactionTestCase
from django.utils import timezone
from oauth2_provider.models import get_access_token_model

from gobabygo.models import User
from gobabygo.oauth import DjangoTokenVerifier


class OAuthTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="oauth-test", email="oauth@example.test", password="test-password"
        )
        response = self.client.post(
            "/o/register/",
            {
                "client_name": "Test MCP client",
                "redirect_uris": ["http://127.0.0.1:43210/callback"],
                "grant_types": ["authorization_code", "refresh_token"],
                "response_types": ["code"],
                "token_endpoint_auth_method": "none",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.registration = response.json()
        self.verifier = "v" * 64
        self.challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(self.verifier.encode()).digest())
            .rstrip(b"=")
            .decode()
        )

    def authorize(self, **overrides):
        params = {
            "client_id": self.registration["client_id"],
            "redirect_uri": self.registration["redirect_uris"][0],
            "response_type": "code",
            "scope": "mcp",
            "state": "test-state",
            "code_challenge": self.challenge,
            "code_challenge_method": "S256",
            "resource": settings.MCP_RESOURCE_URL,
        }
        params.update(overrides)
        self.client.force_login(self.user)
        consent = self.client.get("/o/authorize/", params)
        self.assertEqual(consent.status_code, 200, consent.content)
        self.assertContains(consent, "Use the MCP tools")
        response = self.client.post("/o/authorize/", {**params, "allow": "Authorize"})
        self.assertEqual(response.status_code, 302, response.content)
        query = parse_qs(urlsplit(response.url).query)
        self.assertEqual(query["state"], ["test-state"])
        return query["code"][0]

    def exchange(self, code, **overrides):
        params = {
            "grant_type": "authorization_code",
            "client_id": self.registration["client_id"],
            "code": code,
            "code_verifier": self.verifier,
            "redirect_uri": self.registration["redirect_uris"][0],
            "resource": settings.MCP_RESOURCE_URL,
        }
        params.update(overrides)
        return self.client.post("/o/token/", params)

    def verify(self, raw):
        return async_to_sync(DjangoTokenVerifier().verify_token)(raw)

    def test_discovery(self):
        metadata = self.client.get("/.well-known/oauth-authorization-server").json()
        self.assertEqual(metadata["issuer"], settings.BASE_URL)
        self.assertTrue(metadata["registration_endpoint"].endswith("/o/register/"))
        self.assertEqual(metadata["code_challenge_methods_supported"], ["S256"])
        resource = self.client.get("/.well-known/oauth-protected-resource/mcp").json()
        self.assertEqual(resource["resource"], settings.MCP_RESOURCE_URL)
        self.assertEqual(resource["authorization_servers"], [settings.BASE_URL])

    def test_pkce_consent_refresh_and_revocation(self):
        code = self.authorize()
        response = self.exchange(code)
        self.assertEqual(response.status_code, 200, response.content)
        tokens = response.json()
        access = self.verify(tokens["access_token"])
        self.assertIsNotNone(access)
        self.assertEqual(access.subject, str(self.user.pk))
        self.assertEqual(access.scopes, ["mcp"])
        stored = get_access_token_model().objects.get(
            token_checksum=hashlib.sha256(tokens["access_token"].encode()).hexdigest()
        )
        self.assertEqual(stored.token, "")  # Tokens are hashed at rest.
        self.assertEqual(self.exchange(code).status_code, 400)  # One-use codes.
        refreshed = self.client.post(
            "/o/token/",
            {
                "grant_type": "refresh_token",
                "client_id": self.registration["client_id"],
                "refresh_token": tokens["refresh_token"],
                "resource": settings.MCP_RESOURCE_URL,
            },
        )
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        raw = refreshed.json()["access_token"]
        self.assertIsNotNone(self.verify(raw))
        self.assertEqual(
            self.client.post(
                "/o/revoke_token/",
                {
                    "client_id": self.registration["client_id"],
                    "token": raw,
                },
            ).status_code,
            200,
        )
        self.assertIsNone(self.verify(raw))

    def test_wrong_pkce_verifier(self):
        self.assertEqual(
            self.exchange(self.authorize(), code_verifier="x" * 64).status_code, 400
        )

    def test_wrong_resource_and_expired_or_disabled_user(self):
        raw = self.exchange(self.authorize()).json()["access_token"]
        stored = get_access_token_model().objects.get(
            token_checksum=hashlib.sha256(raw.encode()).hexdigest()
        )
        for resources in ([], [settings.BASE_URL + "/other"]):
            stored.resource = resources
            stored.save()
            self.assertIsNone(self.verify(raw))
        stored.resource = [settings.MCP_RESOURCE_URL]
        stored.expires = timezone.now() - timedelta(seconds=1)
        stored.save()
        self.assertIsNone(self.verify(raw))
        stored.expires = timezone.now() + timedelta(hours=1)
        stored.save()
        self.user.is_active = False
        self.user.save()
        self.assertIsNone(self.verify(raw))

    def test_registration_token_is_not_an_mcp_token(self):
        self.assertIsNone(self.verify(self.registration["registration_access_token"]))
        self.assertIsNone(self.verify("invalid"))

    def test_mcp_rejects_missing_scope_and_cookie_only_auth(self):
        import httpx2 as httpx
        from app.asgi import application

        raw = self.exchange(self.authorize()).json()["access_token"]
        get_access_token_model().objects.filter(
            token_checksum=hashlib.sha256(raw.encode()).hexdigest()
        ).update(scope="other")

        async def request(headers):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=application),
                base_url="http://localhost",
            ) as client:
                return await client.get("/mcp", headers=headers)

        denied = async_to_sync(request)({"Authorization": f"Bearer {raw}"})
        self.assertEqual(denied.status_code, 403)
        cookie = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        denied = async_to_sync(request)(
            {"Cookie": f"{settings.SESSION_COOKIE_NAME}={cookie}"}
        )
        self.assertEqual(denied.status_code, 401)
        self.assertIn("resource_metadata=", denied.headers["www-authenticate"])

    def test_missing_or_plain_pkce_is_rejected(self):
        self.client.force_login(self.user)
        params = {
            "client_id": self.registration["client_id"],
            "response_type": "code",
            "redirect_uri": self.registration["redirect_uris"][0],
            "scope": "mcp",
            "resource": settings.MCP_RESOURCE_URL,
        }
        for extra in (
            {},
            {"code_challenge": self.verifier, "code_challenge_method": "plain"},
        ):
            response = self.client.get("/o/authorize/", {**params, **extra})
            # DOT rejects plain PKCE when saving the grant, after consent.
            if response.status_code == 200:
                response = self.client.post(
                    "/o/authorize/", {**params, **extra, "allow": "Authorize"}
                )
            self.assertEqual(response.status_code, 302)
            self.assertIn("error=invalid_request", response.url)

    def test_dcr_rejects_invalid_redirect_and_management_requires_credential(self):
        response = self.client.post(
            "/o/register/",
            {
                "redirect_uris": ["javascript:alert(1)"],
                "token_endpoint_auth_method": "none",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        uri = f'/o/register/{self.registration["client_id"]}/'
        self.assertEqual(self.client.delete(uri).status_code, 401)
        response = self.client.delete(
            uri,
            headers={
                "Authorization": f'Bearer {self.registration["registration_access_token"]}',
            },
        )
        self.assertEqual(response.status_code, 204)

    def test_open_registration_policy(self):
        for metadata in (
            {"redirect_uris": ["http://remote.example/callback"]},
            {"grant_types": ["client_credentials"]},
            {"redirect_uris": ["https://user:password@example.com/callback"]},
        ):
            response = self.client.post(
                "/o/register/", metadata, content_type="application/json"
            )
            self.assertEqual(response.status_code, 400)
        uri = f'/o/register/{self.registration["client_id"]}/'
        response = self.client.put(
            uri,
            {"redirect_uris": ["http://remote.example/callback"]},
            content_type="application/json",
            headers={
                "Authorization": f'Bearer {self.registration["registration_access_token"]}'
            },
        )
        self.assertEqual(response.status_code, 400)
