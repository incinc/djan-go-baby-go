import os

from app.settings.common import *

sentry_sdk.init(dsn=SENTRY_DSN, environment="prd")

DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=True)

ENVIRONMENT = "prd"

SECRET_KEY = os.environ["SECRET_KEY"]

SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = [
    # PRE_DEPLOY_PRD
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "ERROR"),
        },
    },
}

WEBPACK_LOADER["DEFAULT"].update(
    {
        "BUNDLE_DIR_NAME": "dist/",
    }
)
