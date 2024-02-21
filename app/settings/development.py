from app.settings.common import *

# sentry_sdk.init(dsn=SENTRY_DSN, environment='dev')

DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=False)

ENVIRONMENT = "dev"

USE_X_FORWARDED_HOST = True

DEBUG = True

WEBPACK_LOADER["DEFAULT"]["STATS_FILE"] = os.path.join(
    BASE_DIR, "webpack-stats-dev.json"
)

ALLOWED_HOSTS = ["gobabygo-web-1", "localhost"]
