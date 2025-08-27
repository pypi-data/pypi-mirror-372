"""
Rate Limiting 미들웨어
"""

import time
import logging
from typing import Callable, Dict
from collections import defaultdict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    간단한 Rate Limiting 미들웨어
    프로덕션에서는 Redis 기반 구현 권장
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # IP별 요청 추적 (프로덕션에서는 Redis 사용)
        self.requests: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 클라이언트 IP 추출
        client_ip = request.client.host if request.client else "unknown"

        # 헬스체크는 rate limit 제외
        if request.url.path in ["/health", "/health/live", "/health/ready"]:
            return await call_next(request)

        current_time = time.time()

        # 오래된 요청 정리
        self.requests[client_ip] = [
            req_time
            for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]

        # Rate limit 체크
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.window_seconds)),
                },
            )

        # 요청 기록
        self.requests[client_ip].append(current_time)

        # 요청 처리
        response = await call_next(request)

        # Rate limit 헤더 추가
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_seconds)
        )

        return response
