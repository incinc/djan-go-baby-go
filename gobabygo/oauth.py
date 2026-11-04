"""Bridge Django OAuth Toolkit's stored tokens to the MCP resource server."""

import hashlib

from channels.db import database_sync_to_async
from django.conf import settings
from mcp.server.auth.provider import AccessToken
from oauth2_provider.models import get_access_token_model


class DjangoTokenVerifier:
    async def verify_token(self, token: str) -> AccessToken | None:
        return await self._verify(token)

    @database_sync_to_async
    def _verify(self, token: str) -> AccessToken | None:
        stored = (
            get_access_token_model()
            .objects.select_related("application", "user")
            .filter(token_checksum=hashlib.sha256(token.encode()).hexdigest())
            .first()
        )
        if (
            stored is None
            or not stored.is_valid()
            or stored.application is None
            or stored.user is None
            or not stored.user.is_active
            # MCP tokens must explicitly target this resource. DOT's generic
            # resource validator also allows unbound tokens; MCP must not.
            or settings.MCP_RESOURCE_URL not in stored.resource
        ):
            return None
        return AccessToken(
            token=token,
            client_id=stored.application.client_id,
            subject=str(stored.user_id),
            scopes=stored.scope.split(),
            expires_at=int(stored.expires.timestamp()),
            resource=settings.MCP_RESOURCE_URL,
        )
