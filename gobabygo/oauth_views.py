"""Limit open registration to MCP authorization-code clients and safe callbacks."""

import json
from urllib.parse import urlsplit

from django.http import JsonResponse
from oauth2_provider.views import (
    DynamicClientRegistrationManagementView,
    DynamicClientRegistrationView,
)


class MCPRegistrationPolicy:
    def validate_metadata(self, request):
        try:
            data = json.loads(request.body)
        except (ValueError, UnicodeDecodeError):
            return None  # Let Toolkit return its standard malformed-body error.
        if not isinstance(data, dict):
            return None
        grants = data.get("grant_types", ["authorization_code"])
        if not isinstance(grants, list) or any(
            grant not in ("authorization_code", "refresh_token") for grant in grants
        ):
            return JsonResponse(
                {
                    "error": "invalid_client_metadata",
                    "error_description": "Use authorization_code with optional refresh_token.",
                },
                status=400,
            )
        redirects = data.get("redirect_uris", [])
        if not isinstance(redirects, list):
            return None
        for redirect in redirects:
            if not isinstance(redirect, str):
                return None
            try:
                uri = urlsplit(redirect)
                allowed = (
                    not uri.username
                    and not uri.password
                    and (
                        uri.scheme == "https"
                        or (
                            uri.scheme == "http"
                            and uri.hostname in ("localhost", "127.0.0.1", "::1")
                        )
                    )
                )
            except ValueError:
                allowed = False
            if not allowed:
                return JsonResponse(
                    {
                        "error": "invalid_redirect_uri",
                        "error_description": "Use HTTPS or an HTTP loopback callback.",
                    },
                    status=400,
                )
        return None

    def post(self, request, *args, **kwargs):
        error = self.validate_metadata(request)
        return error if error is not None else super().post(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        error = self.validate_metadata(request)
        return error if error is not None else super().put(request, *args, **kwargs)


class MCPRegistrationView(MCPRegistrationPolicy, DynamicClientRegistrationView):
    pass


class MCPRegistrationManagementView(
    MCPRegistrationPolicy, DynamicClientRegistrationManagementView
):
    pass
