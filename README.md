# djan-go-baby-go
In less than three minutes this will set up a fully functional rapid application dev environment with Django and Vue.

The only requirement is [Docker](https://docs.docker.com/desktop/). Make a copy of this template repo, then run:

```bash
./bootstrap.sh myproject
```

Use a lowercase project name starting with a letter (letters, digits, and underscores only).
Pass `-d` to start Compose in the background. Bootstrap edits this copy in place.

The bootstrap script will:
- Rename everything in the project from `gobabygo` to your project name.
- Populate the `.env.tmpl` into `.env` with suitable starting values.
- Builds/pulls containers from the docker-compose file.
- Generates and applies initial Django migrations.

The final step of the bootstrap script runs `docker compose up`, check http://localhost:8888/ to find a running app.

The bootstrap process has been tested on Linux and MacOS, but not Windows (contributions welcome if it does not work in WSL).

### What this includes

This is an opinionated template that brings together a number of other tools and libraries I've enjoyed working with. Maybe you'll like them as well.

#### Foundation & Tooling
- [PostgreSQL](https://www.postgresql.org/docs/18/index.html)
- [Redis](https://redis.io/docs/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Webpack](https://webpack.js.org/concepts/)
- [Uvicorn](https://www.uvicorn.org/) (ASGI end-to-end)

#### Python Libraries
- [Django](https://docs.djangoproject.com/en/6.0/) with [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/)
- [Django Ninja](https://django-ninja.dev/)
- [Channels](https://channels.readthedocs.io/en/latest/) WebSockets, backed by the Redis channel layer
- [Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/) with PKCE, consent, and dynamic client registration
- [MCP server](https://modelcontextprotocol.io/) at `/mcp`, built on the [official python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) (with [Beat](https://django-celery-beat.readthedocs.io/en/latest/))
- [pytest](https://docs.pytest.org/en/7.4.x/)

#### Frontend
- [Vue 3](https://vuejs.org/guide/introduction.html)
  - [Vue Router](https://router.vuejs.org/guide/)
  - [Pinia](https://pinia.vuejs.org/core-concepts/)
- [PrimeVue](https://primevue.org/introduction/) component library

#### Services
- [Sentry](https://docs.sentry.io/platforms/python/integrations/django/)
- [Stripe](https://stripe.com/docs/api?lang=python)

### WebSockets and MCP

Open http://localhost:8888/ in two tabs to try the public WebSocket broadcast at
`/ws/echo`. Django session cookies identify logged-in users; the demo intentionally
allows anonymous users to send and receive messages in the same group.

The MCP endpoint is `http://localhost:8888/mcp`. It requires an OAuth bearer token
with the `mcp` scope and that exact URL as its resource/audience. Create a user for
the login and consent flow:

```bash
docker compose exec web python manage.py createsuperuser
```

Point an OAuth-capable MCP client at the endpoint, for example:

```bash
claude mcp add --transport http myproject http://localhost:8888/mcp
```

The client discovers the authorization server, registers itself, and opens Django's
login and consent pages. Approve access to the MCP tools, then try `hello` or
`user_count`. No client ID or secret needs to be copied from the admin. The landing
page checks the OAuth challenge; it does not store a token or bypass authorization.

The relevant endpoints are:

| Endpoint | Purpose |
| --- | --- |
| `/.well-known/oauth-protected-resource/mcp` | MCP resource and authorization server discovery |
| `/.well-known/oauth-authorization-server` | OAuth endpoints and PKCE capabilities |
| `/o/register/` | Dynamic client registration (RFC 7591) |
| `/o/authorize/` | Django login and user consent |
| `/o/token/` | Authorization-code exchange and refresh |
| `/o/revoke_token/` | Token revocation |
| `/o/authorized_tokens/` | User interface to revoke authorized tokens |

OAuth clients must use authorization code + S256 PKCE, request the `mcp` scope,
and include `resource=http://localhost:8888/mcp` in authorization/token requests.
Dynamic registration accepts authorization-code clients with HTTPS or HTTP loopback
callbacks only. Refresh tokens rotate. Access tokens expire after an hour, are stored as checksums,
and are checked against the database on each MCP request. Registration credentials,
expired/revoked tokens, inactive users, and tokens for other resources are rejected.
Django session cookies alone do not authorize MCP calls.

For deployment, set `BASE_URL` to the canonical public HTTPS origin and configure
explicit `ALLOWED_HOSTS` in the deployment settings. OAuth discovery and token
audiences depend on that origin; a client using a different host will not match it.
Configure the trusted reverse proxy/HTTPS settings for your deployment. MCP is a
separate ASGI app and does not pass through Django's security middleware.
Dynamic registration is open so clients can bootstrap without pre-issued credentials;
apply registration rate limits at your public proxy or change
`DCR_REGISTRATION_PERMISSION_CLASSES` for a restricted deployment. Registering a
client does not grant it a user's access. Use `cleartokens` periodically to remove
expired OAuth credentials.

MCP sessions are stateful and held in one web process. Keep one Uvicorn worker, or
switch to stateless MCP / sticky routing before scaling. The standalone production
image defaults to `app.settings.production`; the Compose stack explicitly uses the
development settings from `.env`.

### Testing and dependency updates

Run bootstrap in a disposable copy so the template remains intact. Once running:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py test --noinput
docker compose exec web python dev/smoke_test.py
docker build -t myproject-production .
```

The live smoke test creates and removes a temporary user and OAuth client; run it
against a disposable database. It exercises discovery, registration, consent, MCP
tools, revocation, frontend assets, two-client Redis broadcasts, and origin checks
through nginx. Bootstrap guard tests run before bootstrapping with
`python3 -m unittest discover -s dev -p 'test_*.py'`.

Edit `requirements.in` and run `./dev/requirements.sh recompile` to regenerate the
Python lock file. `pip<26` is pinned because pip-tools 7.x depends on the older pip
internal API. Frontend installs use `npm ci`; production assets use `npm run build`.

### Contributing

The goals of the template are that it remain:

- One-click to a running app
- "Available in any color, so long as it is black"
- Easy to maintain up-to-date dependencies
- Easy to understand the structure and layout

The intent of this template is to provide a starting point where things "just work" out of the box. Contributions should follow that as a guiding principle: if a change introduces something that requires extensive customization after running the boostrap script for it to work at all, it's probably not a great thing to include.

Secondary to that, the bootstrap script is intended to be a single path: it is not the intent to introduce an interactive or configurable process that produces a different result based on user choices, but instead produce one output that can be modified manually after the fact.

Dependencies *do not follow LTS releases*. The intent is that dependencies, including Django itself, are up to date with the latest stable release wherever possible. If an important dependency becomes unmaintained or there are significant benefits to be had from an alternative, it should be replaced.
