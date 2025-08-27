"""
요청 로깅 미들웨어
"""

import time
import json
import logging
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청/응답 로깅 미들웨어
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 ID 생성
        request_id = str(uuid4())
        request.state.request_id = request_id

        # 시작 시간
        start_time = time.time()

        # 요청 정보 로깅
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "client": request.client.host if request.client else None,
            },
        )

        # 요청 처리
        response = await call_next(request)

        # 처리 시간 계산
        process_time = time.time() - start_time

        # 응답 정보 로깅
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            },
        )

        # 응답 헤더에 요청 ID와 처리 시간 추가
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response
