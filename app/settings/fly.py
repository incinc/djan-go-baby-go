"""Production settings for Fly's HTTPS proxy and private network."""

import os
from urllib.parse import urlsplit

# Set this before common.py constructs OAuth issuer and audience settings.
if not os.environ.get("BASE_URL") and os.environ.get("FLY_APP_NAME"):
    os.environ["BASE_URL"] = f"https://{os.environ['FLY_APP_NAME']}.fly.dev"

from app.settings.production import *  # noqa: E402,F403

origin = urlsplit(BASE_URL)
if (
    origin.scheme != "https"
    or not origin.hostname
    or origin.path
    or origin.query
    or origin.fragment
    or origin.username
    or origin.password
):
    raise ValueError("Fly BASE_URL must be an HTTPS origin, without a path")

ALLOWED_HOSTS = [origin.hostname, "localhost"]
# Fly terminates TLS; the application port is only reachable on its private network.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
CSRF_TRUSTED_ORIGINS = [BASE_URL]

# Let the connection URL choose TLS (the private singleton uses sslmode=disable).
DATABASES = {"default": dj_database_url.config(conn_max_age=0)}
# Also supports Managed Postgres's transaction-pooling endpoint.
DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
WEBPACK_LOADER["DEFAULT"]["CACHE"] = True
LOGGING["root"] = {"handlers": ["console"], "level": "INFO"}
