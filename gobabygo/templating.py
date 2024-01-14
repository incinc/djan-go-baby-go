from django.templatetags.static import static
from django.urls import reverse
from django.conf import settings

from jinja2 import Environment


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "settings": {
                "ENVIRONMENT": settings.ENVIRONMENT,
            },
        }
    )
    return env
