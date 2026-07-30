class AppError(Exception):
    """Base application exception with safe user-facing details."""

    error_code = "application_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValidationError(AppError):
    """Raised when validated data violates business rules."""

    error_code = "validation_error"


class AuthenticationError(AppError):
    """Raised when authentication is required or invalid."""

    error_code = "authentication_error"


class PermissionDeniedError(AppError):
    """Raised when an authenticated user lacks permission."""

    error_code = "permission_denied"


class ResourceNotFoundError(AppError):
    """Raised when a requested resource cannot be found."""

    error_code = "resource_not_found"


class ConflictError(AppError):
    """Raised when a request conflicts with existing data."""

    error_code = "conflict_error"


class DatabaseError(AppError):
    """Raised for database operation failures."""

    error_code = "database_error"


class ExternalServiceError(AppError):
    """Raised when an external service call fails."""

    error_code = "external_service_error"

