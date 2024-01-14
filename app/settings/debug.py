from app.settings.common import *
from app.settings.development import *

# This is just for running in a venv instead of docker to make it
# less janky to run with an interactive debugger attached.
#
# The db still needs to run in docker alongside it.

# python3 manage.py runserver localhost:8989 --noreload

DATABASES["default"]["HOST"] = "localhost"

INSTALLED_APPS.append("django_pdb")

MIDDLEWARE.append("django_pdb.middleware.PdbMiddleware")
