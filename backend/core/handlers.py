import importlib

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

try:
    Ratelimited = importlib.import_module("django_ratelimit.exceptions").Ratelimited
except ModuleNotFoundError:  # pragma: no cover
    Ratelimited = None


def custom_exception_handler(exc, context):
    if Ratelimited is not None and isinstance(exc, Ratelimited):
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Trop de requêtes. Réessayez plus tard.",
                    "details": {"detail": "Trop de requêtes. Réessayez plus tard."},
                },
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    response = exception_handler(exc, context)
    if response is None:
        return response

    detail = response.data
    message = detail
    if isinstance(detail, dict) and "detail" in detail:
        message = detail["detail"]

    response.data = {
        "success": False,
        "error": {
            "message": message,
            "details": detail,
        },
    }
    return response
