"""One consistent error envelope for every API error.

    {"error": {"code": "...", "message": "...", "details": {...}}}

`details` is only present for validation errors (field -> messages), so the
frontend can show per-field errors without parsing strings.
"""
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:  # unhandled exception: let Django return a 500
        return None

    if isinstance(exc, ValidationError):
        error = {
            "code": "validation_error",
            "message": "Invalid input.",
            "details": response.data,
        }
    else:
        # DRF has already normalised Http404/PermissionDenied into {"detail": ErrorDetail}.
        detail = response.data.get("detail", "Request failed.")
        error = {"code": getattr(detail, "code", "error"), "message": str(detail)}
    response.data = {"error": error}
    return response
