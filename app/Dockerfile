FROM python:3.15-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:${PATH}"
WORKDIR /opt

RUN apt-get update && apt-get install -y build-essential libpq-dev

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
    uv sync --locked \
    && chown -R appuser:appuser /opt/venv /opt/src

USER appuser

COPY --chown=appuser:appuser . /opt/src/

WORKDIR /opt/src

RUN bash -c 'SECRET_KEY=dummy DJANGO_SETTINGS_MODULE=app.settings.production python manage.py collectstatic --no-input'
