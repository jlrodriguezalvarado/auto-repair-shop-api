import logging
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

@require_GET
@never_cache
def liveness(request):
    return JsonResponse({"status": "ok"})

@require_GET
@never_cache
def readiness(request):
    ok = _database_is_ready()
    return JsonResponse(
        {
            "status": "ok" if ok else "unavailable",
            "checks": {"database": "ok" if ok else "unavailable"},
        },
        status=200 if ok else 503,
    )

def _database_is_ready():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True
    except Exception as exc:
        logger.warning("Readiness check failed for database (%s).", type(exc).__name__)
        return False
