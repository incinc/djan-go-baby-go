import os

from app.settings.common import *


sentry_sdk.init(dsn=SENTRY_DSN, environment="stg")

ENVIRONMENT = "stg"

SECURE_SSL_REDIRECT = True

ALLOWED_HOSTS = [
    # PRE_DEPLOY_STG
]

DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=True)

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
