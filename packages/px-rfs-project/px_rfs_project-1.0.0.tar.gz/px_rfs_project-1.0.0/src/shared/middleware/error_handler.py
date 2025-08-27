"""
에러 처리 미들웨어
"""

import logging
import traceback
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    전역 에러 처리 미들웨어
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            # 비즈니스 로직 에러
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Bad Request",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
        except PermissionError as e:
            # 권한 에러
            logger.warning(f"Permission denied: {str(e)}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Forbidden",
                    "message": "You don't have permission to access this resource",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
        except Exception as e:
            # 예상치 못한 에러
            error_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"Unhandled exception",
                extra={
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "request_id": error_id,
                    "path": request.url.path,
                },
            )

            # 개발 환경에서는 상세 에러 표시
            if settings.debug:
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "message": str(e),
                        "type": type(e).__name__,
                        "traceback": traceback.format_exc().split("\n"),
                        "request_id": error_id,
                    },
                )
            else:
                # 프로덕션에서는 일반적인 메시지만
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred",
                        "request_id": error_id,
                    },
                )
