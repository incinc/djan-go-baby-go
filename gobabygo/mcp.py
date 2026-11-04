from channels.db import database_sync_to_async
from django.conf import settings
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

from gobabygo.models import User
from gobabygo.oauth import DjangoTokenVerifier

# DNS rebinding protection: the transport validates Host/Origin headers, so
# reuse Django's ALLOWED_HOSTS. (The MCP matcher doesn't understand Django's
# ".domain" wildcard entries — list hosts explicitly if you use those.)
_hosts = [h for h in settings.ALLOWED_HOSTS if not h.startswith(".")] or [
    "localhost",
    "127.0.0.1",
]
transport_security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=[pattern for h in _hosts for pattern in (h, f"{h}:*")],
    allowed_origins=[
        origin
        for h in _hosts
        for origin in (f"http://{h}", f"http://{h}:*", f"https://{h}", f"https://{h}:*")
    ],
)

# The MCP server is mounted at /mcp by app/asgi.py, alongside Django itself.
# Tools are plain (optionally async) functions, the same way API endpoints are
# declared in gobabygo/api.py — schemas are generated from type hints.
#
# By default sessions are stateful, which enables the full MCP feature set
# (server->client notifications, sampling, elicitation). Session state lives in
# process memory: if you scale to multiple web workers, either enable sticky
# routing or pass stateless_http=True to streamable_http_app() in app/asgi.py.
mcp_server = MCPServer(
    "gobabygo",
    instructions="Development quickstart MCP server for the gobabygo app.",
    token_verifier=DjangoTokenVerifier(),
    auth=AuthSettings(
        issuer_url=settings.BASE_URL,
        resource_server_url=settings.MCP_RESOURCE_URL,
        required_scopes=["mcp"],
        validate_token_resource=True,
    ),
)


@mcp_server.tool()
def hello(name: str = "world") -> str:
    """Say hello, proving the MCP server is wired up."""
    return f"Hello, {name}! This is the gobabygo MCP server."


@mcp_server.tool()
async def user_count() -> int:
    """Count registered users, demonstrating safe database access from an async tool."""
    # MCP bypasses Django's request lifecycle. Close ORM connections after
    # each call, including failures, rather than retaining them in SDK threads.
    return await database_sync_to_async(User.objects.count)()
