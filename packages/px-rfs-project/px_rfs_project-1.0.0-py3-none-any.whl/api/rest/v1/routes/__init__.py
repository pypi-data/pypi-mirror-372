"""
API 라우트 모듈
"""

from fastapi import APIRouter
from src.api.rest.v1.routes import health

# 메인 API 라우터
api_router = APIRouter()

# 추가 라우터들을 여기에 포함
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(files.router, prefix="/files", tags=["Files"])

__all__ = ["api_router", "health"]
