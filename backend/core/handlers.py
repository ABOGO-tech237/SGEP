from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
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
