"""OAuth setup for the disposable-stack smoke test; never use on a shared DB."""

import base64
from contextlib import contextmanager
import hashlib
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import httpx
from django.conf import settings
from django.test import Client

from gobabygo.models import User


class HiddenInputs(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.values = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "input" and attrs.get("type") == "hidden" and "name" in attrs:
            self.values[attrs["name"]] = attrs.get("value", "")


@contextmanager
def oauth_token(base_url):
    user = User.objects.create_user(
        username=f"smoke-{uuid4().hex}", email=f"{uuid4().hex}@example.test"
    )
    client = Client()
    client.force_login(user)
    registration = None
    try:
        with httpx.Client(
            base_url=base_url,
            headers={"Host": "localhost:8888"},
            trust_env=False,
            timeout=10,
        ) as http:
            discovery = http.get("/.well-known/oauth-authorization-server")
            discovery.raise_for_status()
            assert discovery.json()["issuer"] == settings.BASE_URL
            metadata = http.get("/.well-known/oauth-protected-resource/mcp").json()
            assert metadata["resource"] == settings.MCP_RESOURCE_URL
            response = http.post(
                "/o/register/",
                json={
                    "client_name": "Disposable smoke test",
                    "redirect_uris": ["http://127.0.0.1:43210/callback"],
                    "grant_types": ["authorization_code", "refresh_token"],
                    "response_types": ["code"],
                    "token_endpoint_auth_method": "none",
                },
            )
            assert response.status_code == 201, response.text
            registration = response.json()
            verifier = "v" * 64
            challenge = (
                base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
                .rstrip(b"=")
                .decode()
            )
            params = {
                "client_id": registration["client_id"],
                "response_type": "code",
                "redirect_uri": registration["redirect_uris"][0],
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                "scope": "mcp",
                "resource": settings.MCP_RESOURCE_URL,
                "state": uuid4().hex,
            }
            login = http.get("/o/authorize/", params=params)
            assert (
                login.status_code == 302
                and "/account/login/" in login.headers["location"]
            )
            # Seed a Django session for the temporary user; consent and CSRF still
            # go through the live HTTP server, rather than Django's test client.
            http.cookies.set(
                settings.SESSION_COOKIE_NAME,
                client.cookies[settings.SESSION_COOKIE_NAME].value,
            )
            consent = http.get("/o/authorize/", params=params)
            assert consent.status_code == 200, consent.text
            fields = HiddenInputs(consent.text).values
            assert "csrfmiddlewaretoken" in fields
            authorized = http.post(
                "/o/authorize/", data={**fields, "allow": "Authorize"}
            )
            assert authorized.status_code == 302, authorized.text
            query = parse_qs(urlsplit(authorized.headers["location"]).query)
            assert query["state"] == [params["state"]]
            response = http.post(
                "/o/token/",
                data={
                    "grant_type": "authorization_code",
                    "code": query["code"][0],
                    "client_id": registration["client_id"],
                    "code_verifier": verifier,
                    "redirect_uri": params["redirect_uri"],
                    "resource": settings.MCP_RESOURCE_URL,
                },
            )
            assert response.status_code == 200, response.text
            raw = response.json()["access_token"]
            yield raw
            revoked = http.post(
                "/o/revoke_token/",
                data={"token": raw, "client_id": registration["client_id"]},
            )
            assert revoked.status_code == 200
            denied = http.get("/mcp", headers={"Authorization": f"Bearer {raw}"})
            assert denied.status_code == 401, denied.text
    finally:
        if registration:
            with httpx.Client(
                base_url=base_url, headers={"Host": "localhost:8888"}, trust_env=False
            ) as http:
                http.delete(
                    f'/o/register/{registration["client_id"]}/',
                    headers={
                        "Authorization": f'Bearer {registration["registration_access_token"]}',
                    },
                ).raise_for_status()
        client.logout()
        user.delete()
