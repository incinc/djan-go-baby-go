from django.http import JsonResponse
from django.views.decorators.http import require_safe


@require_safe
def health(request):
    """Liveness only: database and Redis are checked separately during deployment."""
    return JsonResponse({"status": "ok"})
