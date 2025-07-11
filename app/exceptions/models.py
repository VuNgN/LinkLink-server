"""
Custom exception models
"""

from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Custom HTTP exception with additional context"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        context: dict = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


class ValidationError(CustomHTTPException):
    """Validation error exception"""

    def __init__(self, detail: str, field: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context={"field": field} if field else None,
        )


class AuthenticationError(CustomHTTPException):
    """Authentication error exception"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(CustomHTTPException):
    """Authorization error exception"""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
        )


class NotFoundError(CustomHTTPException):
    """Not found error exception"""

    def __init__(self, resource: str, resource_id: str = None):
        detail = f"{resource} not found"
        if resource_id:
            detail += f" with id: {resource_id}"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND_ERROR",
            context={"resource": resource, "resource_id": resource_id},
        )


class ConflictError(CustomHTTPException):
    """Conflict error exception"""

    def __init__(self, detail: str, resource: str = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT_ERROR",
            context={"resource": resource} if resource else None,
        )
