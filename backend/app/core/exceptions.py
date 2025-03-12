"""
Custom exceptions and exception handlers for the application.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger

class APIException(Exception):
    """Base API exception class"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(detail)

class NotFoundError(APIException):
    """Resource not found exception"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")

class AuthenticationError(APIException):
    """Authentication failed exception"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail, error_code="UNAUTHORIZED")

class AuthorizationError(APIException):
    """Authorization failed exception"""
    def __init__(self, detail: str = "Not authorized to access this resource"):
        super().__init__(status_code=403, detail=detail, error_code="FORBIDDEN")

class ValidationError(APIException):
    """Validation error exception"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")

class DatabaseError(APIException):
    """Database error exception"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=500, detail=detail, error_code="DATABASE_ERROR")

class LLMError(APIException):
    """LLM service error exception"""
    def __init__(self, detail: str = "Language model service error"):
        super().__init__(status_code=503, detail=detail, error_code="LLM_ERROR")

class RateLimitError(APIException):
    """Rate limit exceeded exception"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail, error_code="RATE_LIMIT")

def setup_exception_handlers(app: FastAPI) -> None:
    """
    Setup exception handlers for the application.
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle APIException instances"""
        logger.error(
            f"API Exception: {exc.error_code} - {exc.detail}",
            extra={"path": request.url.path, "method": request.method}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail,
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle RequestValidationError"""
        logger.error(
            f"Validation Error: {exc.errors()}",
            extra={"path": request.url.path, "method": request.method}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Validation error",
                    "details": exc.errors(),
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Handle unhandled exceptions"""
        logger.exception(
            f"Unhandled exception: {str(exc)}",
            extra={"path": request.url.path, "method": request.method}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )