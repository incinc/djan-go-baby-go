"""Keep Toolkit's routes, replacing only the open-registration policy."""

from django.urls import path
from oauth2_provider.urls import urlpatterns as toolkit_patterns

from gobabygo.oauth_views import MCPRegistrationManagementView, MCPRegistrationView

app_name = "oauth2_provider"
urlpatterns = [
    path("register/", MCPRegistrationView.as_view(), name="dcr-register"),
    path(
        "register/<str:client_id>/",
        MCPRegistrationManagementView.as_view(),
        name="dcr-register-management",
    ),
] + [
    pattern
    for pattern in toolkit_patterns
    if pattern.name not in {"dcr-register", "dcr-register-management"}
]
