# Working on this quickstart

## Purpose and layout

This repository is a Django + Vue project template. Keep the default path simple:
`./bootstrap.sh project_name -d` should produce a running app using Docker alone.
Bootstrap renames the `gobabygo` app, generates `.env`, builds Compose images,
and creates/applies migrations. Always test bootstrap in a disposable copy made
from tracked files; it edits source files and removes itself and the template license.
Do not copy local `.env`, `node_modules`, database files, or generated static assets.

- `app/settings/`: shared, development, staging, production, and test settings.
- `app/asgi.py`: Uvicorn entry point; Django HTTP, MCP HTTP at `/mcp`, Channels
  WebSockets, and the MCP session manager lifespan.
- `app/urls.py`: Django routes, Ninja API, admin, and two-factor authentication.
- `gobabygo/`: custom User/Profile models, views, Jinja templates, API, MCP tools,
  and WebSocket consumers/routing. `oauth.py` adapts OAuth Toolkit tokens to MCP. Preserve renameability of this package.
- `frontend/app/`: Vue 3, Router, Pinia, PrimeVue, and CSS; bundled by Webpack.
- `docker-compose.yaml`: development proxy, web, Celery worker/Beat, Webpack,
  PostgreSQL, and Redis. `dev/nginx.conf` proxies HTTP, SSE, and WebSocket upgrades.
- `app/Dockerfile` and `frontend/Dockerfile`: development images.
  Root `Dockerfile`: production image with bundled static files.

## Development and verification

Use Docker Compose in a bootstrapped copy for the supported environment (Python
3.15, Node 26, PostgreSQL 18, Redis 8). Do not assume host Python/Node match.

- `docker compose exec web python manage.py check`
- `docker compose exec web python manage.py test`
- `docker compose exec webpack npm run build`
- `docker compose exec web python dev/smoke_test.py` for live integration checks
  when that script is present.
- `docker build -t quickstart-production .` for the standalone production image.

Exercise the landing page, `/vue/test`, actual WebSocket broadcasts between two
clients, and an MCP initialize/list/call sequence through nginx. A successful
HTTP GET alone does not validate the async stack. Run relevant regression tests
when changing routing, bootstrap, or protocol handling. CI lives in
`.github/workflows/test.yml`. There is no configured npm test or lint script.

## Dependencies and conventions

Python dependencies are declared in `requirements.in` and pinned by pip-tools
in `requirements.txt`; use `./dev/requirements.sh recompile` in the Docker
environment. Keep `package.json` and `package-lock.json` consistent; use `npm ci`
for reproducible installs. Dependencies track stable releases, not LTS.

Keep sync Django views where appropriate; use async ORM methods in async MCP
handlers and consumers. Django must initialize before ASGI imports app models.
MCP sessions live in process memory, so keep one worker unless configuring
stateless transport or sticky routing. MCP bypasses Django middleware, including Django session authentication and CSRF
protection. Its SDK auth layer requires OAuth Toolkit tokens with the `mcp` scope
and explicit `BASE_URL + /mcp` audience. WebSocket broadcasts remain public. OAuth
discovery, DCR, login, consent, refresh, and revocation are served by Django. Keep
PKCE required and token checks database-backed; tests cover these boundaries.
Live smoke tests create/remove a temporary user/client and require a disposable DB.

Keep secrets out of source control. Preserve existing local `.env` and unrelated
work. Use isolated Compose project names/volumes for testing and clean up only
the resources created by your test run. Document any environment limitations
rather than claiming an unexecuted bootstrap or build passed.
