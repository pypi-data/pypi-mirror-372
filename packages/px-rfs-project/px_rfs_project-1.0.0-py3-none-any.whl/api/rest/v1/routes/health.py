"""
헬스체크 엔드포인트 - RFS Framework 패턴 적용
시스템 상태 모니터링 및 Kubernetes 프로브 지원
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any

from src.config import get_settings
from src.config.dependencies import get_container
from src.shared.hof import pipe, compact_map, partition
from src.shared.kernel import Result, Success, Failure

router = APIRouter()
settings = get_settings()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    헬스체크 엔드포인트
    서비스 상태와 기본 정보 반환
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment.value,
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe
    애플리케이션이 살아있는지 확인
    """
    return {"status": "alive"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_probe() -> JSONResponse:
    """
    Kubernetes 준비성 프로브 - RFS HOF 패턴 적용
    애플리케이션이 요청을 처리할 준비가 되었는지 확인
    함수형 체크 시스템으로 각 의존성 상태를 검증
    """
    container = get_container()

    # RFS HOF 패턴: 헬스체크 함수들을 정의
    health_checks = [
        ("redis", _check_redis_health),
        ("gcs", _check_gcs_health),
        ("ai_services", _check_ai_services_health),
    ]

    # 각 체크를 실행하고 결과를 수집 - 함수형 매핑
    check_results = {name: check_fn(container) for name, check_fn in health_checks}

    # 모든 체크가 통과했는지 확인 - RFS 함수형 검증
    all_ready = all(check_results.values())

    # 응답 생성 파이프라인
    response = pipe(
        lambda ready_status: {
            "status": "ready" if ready_status else "not_ready",
            "checks": check_results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )(all_ready)

    # 준비되지 않은 경우 503 상태 코드 반환
    if not all_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=response
        )

    return JSONResponse(content=response)


def _check_redis_health(container: Any) -> bool:
    """Redis 연결 상태 확인 - 함수형 헬스체크"""
    if not settings.use_redis:
        return True  # Redis 미사용 시 항상 정상

    if not container.redis:
        return False

    try:
        # 실제 Redis ping 체크 (향후 구현)
        # await container.redis.ping()
        return True
    except Exception:
        return False


def _check_gcs_health(container: Any) -> bool:
    """GCS 연결 상태 확인 - 함수형 헬스체크"""
    if not settings.gcs_bucket:
        return True  # GCS 미사용 시 항상 정상

    return bool(container.gcs)


def _check_ai_services_health(container: Any) -> bool:
    """AI 서비스 연결 상태 확인 - 함수형 헬스체크"""
    if not container.ai_clients:
        return False

    return len(container.ai_clients) > 0
