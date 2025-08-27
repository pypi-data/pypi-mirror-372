"""
API 컨트롤러 모듈
FastAPI 라우터 및 컨트롤러 정의
"""

from .text_extraction_controller import text_extraction_router

__all__ = ["text_extraction_router"]
