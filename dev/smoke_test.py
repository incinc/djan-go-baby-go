"""Exercise the running Compose stack through nginx (no extra dependencies).

Run: docker compose exec web python dev/smoke_test.py
Optional first argument: base URL (defaults to http://proxy).
"""

import asyncio
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

import httpx2 as httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus


async def main(base_url, token):
    # Connect using Compose DNS, but present the same Host/Origin as a browser.
    headers = {"Host": "localhost:8888"}
    async with httpx.AsyncClient(headers=headers, timeout=10, trust_env=False) as http:
        for path in ("/", "/vue/test", "/admin/login/"):
            response = await http.get(base_url + path, follow_redirects=True)
            response.raise_for_status()
            assert response.status_code == 200, (path, response.status_code)
        # Vue page must render actual bundle URLs, and nginx must serve them.
        import re

        assets = re.findall(
            r'(?:src|href)="(/webpack-dist/[^" ]+)"',
            (await http.get(base_url + "/vue/test")).text,
        )
        assert assets, "Vue page has no bundled assets"
        for asset in assets:
            (await http.get(base_url + asset)).raise_for_status()
        challenge = await http.get(base_url + "/mcp")
        assert challenge.status_code == 401
        assert "resource_metadata=" in challenge.headers["www-authenticate"]
        http.headers["Authorization"] = f"Bearer {token}"
        async with streamable_http_client(
            base_url + "/mcp", http_client=http
        ) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                names = {tool.name for tool in (await session.list_tools()).tools}
                assert names == {"hello", "user_count"}, names
                hello = await session.call_tool("hello", {"name": "smoke"})
                assert not hello.is_error and "Hello, smoke!" in hello.content[0].text
                count = await session.call_tool("user_count")
                assert not count.is_error and int(count.content[0].text) >= 0
        denied = await http.post(
            base_url + "/mcp", headers={"Host": "untrusted.invalid"}, json={}
        )
        assert denied.status_code == 421, denied.status_code
        denied = await http.post(
            base_url + "/mcp", headers={"Origin": "https://untrusted.invalid"}, json={}
        )
        assert denied.status_code == 403, denied.status_code

    address = urlsplit(base_url)
    ws_url = (
        f"{'wss' if address.scheme == 'https' else 'ws'}://{address.netloc}/ws/echo"
    )
    async with connect(ws_url, origin="http://localhost:8888", proxy=None) as first:
        async with connect(
            ws_url, origin="http://localhost:8888", proxy=None
        ) as second:
            for socket in (first, second):
                assert "connected as" in json.loads(await socket.recv())["text"]
            await first.send(json.dumps({"text": "broadcast smoke"}))
            for socket in (first, second):
                assert json.loads(await socket.recv()) == {"text": "broadcast smoke"}
    try:
        async with connect(ws_url, origin="https://untrusted.invalid", proxy=None):
            raise AssertionError("Untrusted WebSocket origin was accepted")
    except InvalidStatus as exc:
        assert exc.response.status_code == 403
    print(
        "PASS: Django, Vue assets, MCP initialize/list/tools, Redis broadcast, origin rejection"
    )


if __name__ == "__main__":
    # This check creates and removes a temporary user/client. Use a disposable DB.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.development")
    import django

    django.setup()
    from oauth_smoke import oauth_token

    base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://proxy"
    with oauth_token(base_url) as token:
        asyncio.run(asyncio.wait_for(main(base_url, token), 60))
    print("PASS: OAuth discovery, DCR, login redirect, CSRF consent, PKCE, revocation")
