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
        error = {"code": getattr(exc, "default_code", "error"), "message": str(exc.detail)}
        if isinstance(exc.detail, list | dict):  # non-ValidationError with structured detail
            error["message"] = "Request failed."
    response.data = {"error": error}
    return response
