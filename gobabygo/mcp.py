from django.conf import settings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from gobabygo.models import User

# DNS rebinding protection: the transport validates Host/Origin headers, so
# reuse Django's ALLOWED_HOSTS. (The MCP matcher doesn't understand Django's
# ".domain" wildcard entries — list hosts explicitly if you use those.)
_hosts = [h for h in settings.ALLOWED_HOSTS if not h.startswith(".")] or [
    "localhost",
    "127.0.0.1",
]
_transport_security = TransportSecuritySettings(
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
# routing or pass stateless_http=True here.
mcp_server = FastMCP(
    "gobabygo",
    instructions="Development quickstart MCP server for the gobabygo app.",
    transport_security=_transport_security,
)


@mcp_server.tool()
def hello(name: str = "world") -> str:
    """Say hello, proving the MCP server is wired up."""
    return f"Hello, {name}! This is the gobabygo MCP server."


@mcp_server.tool()
async def user_count() -> int:
    """Count registered users, demonstrating async ORM access from a tool."""
    return await User.objects.acount()
