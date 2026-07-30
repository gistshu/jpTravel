import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    ConflictError,
    DatabaseError,
    ExternalServiceError,
    PermissionDeniedError,
    ResourceNotFoundError,
    ValidationError,
)
from app.schemas.common import ErrorItem

logger = logging.getLogger(__name__)

ERROR_STATUS_MAP: dict[type[AppError], int] = {
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    PermissionDeniedError: status.HTTP_403_FORBIDDEN,
    ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExternalServiceError: status.HTTP_502_BAD_GATEWAY,
}


def register_exception_handlers(application: FastAPI) -> None:
    """Register global exception handlers for consistent API responses."""

    @application.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        logger.info(
            "Application error occurred",
            extra={"path": request.url.path, "error_code": exc.error_code},
        )
        status_code = ERROR_STATUS_MAP.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": exc.message,
                "data": None,
                "errors": [
                    ErrorItem(code=exc.error_code, message=exc.message).model_dump()
                ],
            },
        )

    @application.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info(
            "Request validation failed",
            extra={"path": request.url.path},
        )
        errors = [
            ErrorItem(
                code="request_validation_error",
                message=str(error.get("msg", "Invalid request")),
                field=".".join(str(part) for part in error.get("loc", [])),
            ).model_dump()
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "資料驗證失敗",
                "data": None,
                "errors": errors,
            },
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unexpected application error",
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "系統內部錯誤",
                "data": None,
                "errors": [
                    ErrorItem(
                        code="internal_server_error",
                        message="系統內部錯誤",
                    ).model_dump()
                ],
            },
        )
