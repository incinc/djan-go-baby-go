"""
ASGI entrypoint, served by uvicorn.

Three things are composed here:
  - Django itself, handling ordinary HTTP requests
  - the MCP server (gobabygo/mcp.py), handling HTTP under /mcp
  - channels WebSocket consumers (gobabygo/routing.py)
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")

# Django must be set up before anything that imports models.
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from gobabygo.mcp import mcp_server  # noqa: E402
from gobabygo.routing import websocket_urlpatterns  # noqa: E402

# A Starlette app implementing the MCP streamable HTTP transport at /mcp.
mcp_asgi_app = mcp_server.streamable_http_app()


async def http_router(scope, receive, send):
    """Route /mcp to the MCP server, everything else to Django."""
    if scope["path"] == "/mcp" or scope["path"].startswith("/mcp/"):
        await mcp_asgi_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)


async def lifespan(scope, receive, send):
    """
    Keep the MCP session manager running for the lifetime of the server.
    (Its task group handles request streams; it must be started via lifespan
    because the MCP app is mounted rather than served standalone.)
    """
    message = await receive()
    assert message["type"] == "lifespan.startup"
    async with mcp_server.session_manager.run():
        await send({"type": "lifespan.startup.complete"})
        message = await receive()
        assert message["type"] == "lifespan.shutdown"
    await send({"type": "lifespan.shutdown.complete"})


application = ProtocolTypeRouter(
    {
        "http": http_router,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
        "lifespan": lifespan,
    }
)
