"""
Global Exception Handlers for FastAPI.

Provides centralized error handling with structured responses and logging.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from loguru import logger
import traceback
from typing import Union

from .exceptions import APIException, ErrorCode, SystemInternalError


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle custom API exceptions.
    
    Args:
        request: FastAPI request
        exc: API exception
        
    Returns:
        JSON response with structured error
    """
    # Log the error
    logger.error(
        f"API Error: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            },
            "path": request.url.path,
            "method": request.method
        }
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation exception
        
    Returns:
        JSON response with validation errors
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {len(errors)} errors",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": ErrorCode.DATA_VALIDATION_ERROR,
                "message": "Request validation failed",
                "details": {
                    "validation_errors": errors
                }
            },
            "path": request.url.path,
            "method": request.method
        }
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle database errors.
    
    Args:
        request: FastAPI request
        exc: SQLAlchemy exception
        
    Returns:
        JSON response with database error
    """
    # Determine error code based on exception type
    if isinstance(exc, IntegrityError):
        error_code = ErrorCode.DB_CONSTRAINT_VIOLATION
        message = "Database constraint violation"
        status_code = status.HTTP_409_CONFLICT
    else:
        error_code = ErrorCode.DB_QUERY_ERROR
        message = "Database query failed"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Log the error with full traceback
    logger.error(
        f"Database Error: {type(exc).__name__}",
        extra={
            "error_code": error_code,
            "path": request.url.path,
            "method": request.method,
            "exception": str(exc)
        }
    )
    logger.debug(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": {
                    "type": type(exc).__name__
                }
            },
            "path": request.url.path,
            "method": request.method
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle all other unhandled exceptions.
    
    Args:
        request: FastAPI request
        exc: Generic exception
        
    Returns:
        JSON response with internal error
    """
    # Log the error with full traceback
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "error_code": ErrorCode.SYSTEM_INTERNAL_ERROR,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        }
    )
    logger.debug(f"Traceback: {traceback.format_exc()}")
    
    # Don't expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.SYSTEM_INTERNAL_ERROR,
                "message": "An internal server error occurred",
                "details": {
                    "type": type(exc).__name__
                    # In development, you might want to include: "message": str(exc)
                }
            },
            "path": request.url.path,
            "method": request.method
        }
    )


def setup_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    # Custom API exceptions
    app.add_exception_handler(APIException, api_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # Database errors
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    
    # Generic exceptions (catch-all)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Exception handlers registered")
