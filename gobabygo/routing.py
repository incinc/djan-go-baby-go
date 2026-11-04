from django.urls import path

from gobabygo import consumers

# WebSocket URLs, routed by app/asgi.py (the /ws/ prefix is proxied to the web
# container by dev/nginx.conf).
websocket_urlpatterns = [
    path("ws/echo", consumers.EchoConsumer.as_asgi()),
]
