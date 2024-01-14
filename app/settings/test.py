import os

from app.settings.common import *

DEBUG = True

DATABASES["default"] = dj_database_url.config(conn_max_age=600, ssl_require=True)

SEND_NOTIFICATIONS = False
