"""
Global exception handlers
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from .models import CustomHTTPException

logger = logging.getLogger(__name__)


async def custom_http_exception_handler(
    request: Request, exc: CustomHTTPException
) -> JSONResponse:
    """Handle custom HTTP exceptions"""
    error_response = {
        "detail": exc.detail,
        "error_code": exc.error_code,
        "status_code": exc.status_code,
    }

    if exc.context:
        error_response["context"] = exc.context

    logger.error(
        f"Custom HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={"error_code": exc.error_code, "context": exc.context},
    )

    return JSONResponse(status_code=exc.status_code, content=error_response)


async def validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    error_details = []
    for error in exc.errors():
        error_details.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    error_response = {
        "detail": "Validation error",
        "error_code": "VALIDATION_ERROR",
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "errors": error_details,
    }

    logger.warning(
        f"Validation Error: {len(error_details)} field(s) failed validation",
        extra={"errors": error_details},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}", exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers"""

    # Custom HTTP exceptions
    app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)

    # Pydantic validation errors
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)

    # General exceptions (should be last)
    app.add_exception_handler(Exception, general_exception_handler)
