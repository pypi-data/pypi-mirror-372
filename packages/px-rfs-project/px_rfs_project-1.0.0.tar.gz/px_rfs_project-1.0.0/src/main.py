"""
메인 애플리케이션 엔트리 포인트
RFS Framework 패턴 적용
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncContextManager, AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.config.dependencies import initialize_dependencies, cleanup_dependencies
from src.config.dependency_container_improved import (
    initialize_improved_dependencies,
    cleanup_improved_dependencies,
)
from src.shared.hof import pipe, when, tap, safe_pipe, result_chain
from src.shared.kernel import Result, Success, Failure
from src.api.rest.v1.routes import health, api_router
from src.api.controllers import text_extraction_router
from src.shared.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
)


# 설정 로드
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    애플리케이션 라이프사이클 관리 - RFS HOF 패턴 적용
    시작 시 초기화, 종료 시 정리
    """
    # Startup - RFS HOF 패턴으로 시작 로직 구성
    startup_pipeline = pipe(
        tap(
            lambda _: print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
        ),
        tap(lambda _: print(f"📝 Environment: {settings.environment}")),
        tap(lambda _: print(f"🔧 Debug mode: {settings.debug}")),
    )
    startup_pipeline(None)

    # 설정 검증 - RFS Result 패턴 사용
    config_result = settings.validate_config()
    if config_result.is_failure():
        print(f"❌ 설정 오류: {config_result.get_error()}")
        # 프로덕션 환경에서는 예외 발생
        if settings.is_production():
            raise RuntimeError(config_result.get_error())

    # 의존성 초기화 - RFS 체이닝 패턴
    initialization_result = await _initialize_dependencies_chain()
    if initialization_result.is_failure() and settings.is_production():
        raise RuntimeError(initialization_result.get_error() or "Initialization failed")

    yield

    # Shutdown - RFS HOF 패턴으로 정리 로직 구성
    await _cleanup_dependencies_chain()
    print("👋 애플리케이션 종료 완료")


async def _initialize_dependencies_chain() -> Result[str, str]:
    """의존성 초기화 체이닝 - RFS Result 패턴"""
    print("🔧 개선된 의존성 주입 컨테이너 초기화 중...")

    # RFS Result 체이닝을 사용한 의존성 초기화
    async def try_improved_init() -> Result[str, str]:
        result = await initialize_improved_dependencies()
        if result.is_success():
            return Success("✅ 개선된 의존성 컨테이너 초기화 성공")
        return Failure(result.get_error() or "Improved initialization failed")

    async def fallback_init() -> Result[str, str]:
        print("🔄 기존 의존성 초기화로 폴백...")
        result = await initialize_dependencies()
        if result.is_success():
            return Success("✅ 기존 의존성 초기화 성공")
        return Failure(f"❌ 폴백 의존성 초기화 실패: {result.get_error()}")

    # 개선된 초기화 시도
    improved_result = await try_improved_init()
    if improved_result.is_success():
        print(improved_result.get_or_none())
        return improved_result

    # 폴백 초기화 시도
    print(f"⚠️ 개선된 의존성 초기화 실패: {improved_result.get_error()}")
    fallback_result = await fallback_init()
    print(
        fallback_result.get_or_none()
        if fallback_result.is_success()
        else fallback_result.get_error()
    )

    return fallback_result


async def _cleanup_dependencies_chain() -> None:
    """의존성 정리 체이닝 - RFS HOF 패턴"""
    print("🔄 애플리케이션 종료 중...")

    # 정리 작업 파이프라인
    cleanup_tasks = [
        (cleanup_improved_dependencies, "개선된 의존성 정리"),
        (cleanup_dependencies, "기존 의존성 정리"),
    ]

    # 각 정리 작업 실행
    for cleanup_fn, description in cleanup_tasks:
        result = await cleanup_fn()
        if result.is_failure():
            print(f"⚠️ {description} 실패: {result.get_error()}")


def create_application() -> FastAPI:
    """
    FastAPI 애플리케이션 팩토리
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="RFS Framework 기반 엔터프라이즈 서버",
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,  # 프로덕션에서는 문서 숨김
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # CORS 미들웨어
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gzip 압축 미들웨어
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 커스텀 미들웨어 (순서 중요: 아래에서 위로 실행)
    if settings.is_production():
        app.add_middleware(RateLimitMiddleware)

    app.add_middleware(ErrorHandlingMiddleware)

    if settings.log_api_request:
        app.add_middleware(RequestLoggingMiddleware)

    # 라우트 등록
    app.include_router(health.router, tags=["Health"])
    app.include_router(api_router, prefix=settings.api_prefix, tags=["API"])
    app.include_router(text_extraction_router, tags=["텍스트 추출"])

    # 기본 루트 경로
    @app.get("/", include_in_schema=False)
    async def root():
        """루트 경로 - 서비스 정보 반환"""
        return JSONResponse(
            content={
                "service": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment.value,
                "status": "running",
                "api_docs": f"/docs" if settings.debug else "disabled",
                "api_prefix": settings.api_prefix,
            }
        )

    # 404 핸들러
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        """404 에러 핸들러"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"The requested path '{request.url.path}' was not found",
                "path": request.url.path,
            },
        )

    return app


# 애플리케이션 인스턴스 생성
app = create_application()


if __name__ == "__main__":
    """
    직접 실행 시 (개발 모드)
    프로덕션에서는 gunicorn 또는 uvicorn 직접 사용
    """
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,  # 개발 모드에서만 자동 리로드
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.value.lower(),
        access_log=settings.log_api_request,
        use_colors=True,
        reload_dirs=["src"] if settings.debug else None,
    )
