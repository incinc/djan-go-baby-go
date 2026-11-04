FROM node:26-trixie AS webpack

WORKDIR /opt

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci

COPY . /opt/src/

WORKDIR /opt/src
ENV PATH="/opt/node_modules/.bin:${PATH}"
RUN npm run build

## Python app

FROM python:3.15-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:${PATH}"
ENV DJANGO_SETTINGS_MODULE=app.settings.production
WORKDIR /opt

RUN apt-get update && apt-get install -y libpq-dev build-essential

ARG uid=1000
ARG gid=1000
RUN groupadd -r appuser -g $gid \
  && useradd --no-log-init -m -r -g $gid -u $uid appuser \
  && chown -R root:appuser /opt/ \
  && chmod g+w /opt/

# Install from the lock before copying source, so source edits reuse this layer.
# The venv stays outside /opt/src, which Compose replaces with a bind mount.
WORKDIR /opt/src
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev \
    && chown -R appuser:appuser /opt/venv /opt/src

USER appuser

COPY --chown=appuser:appuser . /opt/src/
COPY --chown=appuser:appuser --from=webpack /opt/src/static/dist/ /opt/src/static/dist
COPY --chown=appuser:appuser --from=webpack /opt/src/webpack-stats.json /opt/src/webpack-stats.json

WORKDIR /opt/src

RUN bash -c 'SECRET_KEY=dummy DJANGO_SETTINGS_MODULE=app.settings.production python manage.py collectstatic --no-input'

# Single worker: MCP sessions are stateful and held in process memory. To run
# more workers, set stateless_http=True in app/asgi.py or use sticky routing.
CMD ["uvicorn", "app.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
