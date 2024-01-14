FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1
WORKDIR /opt

RUN apt-get update && apt-get install -y build-essential libpq-dev

RUN groupadd -r appuser -g 1000 \
  && useradd --no-log-init -m -r -g 1000 -u 1000 appuser \
  && chown -R root:appuser /opt/ \
  && chmod g+w /opt/

USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

COPY --chown=appuser:appuser requirements.txt /opt/requirements.txt

RUN pip install -r /opt/requirements.txt

COPY --chown=appuser:appuser . /opt/src/

WORKDIR /opt/src

RUN bash -c 'SECRET_KEY=dummy DJANGO_SETTINGS_MODULE=app.settings.production python manage.py collectstatic --no-input'
