"""
프로덕션 환경 설정
"""

from src.config.settings import Settings, Environment, LogLevel


class ProductionSettings(Settings):
    """프로덕션 환경 전용 설정"""

    # 프로덕션 환경 기본값 오버라이드
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    log_level: LogLevel = LogLevel.WARNING

    # 프로덕션 Redis 설정
    use_redis: bool = True
    redis_cache_ttl: int = 3600  # 1시간
    redis_max_connections: int = 100

    # 프로덕션 CORS 설정 (실제 도메인으로 변경 필요)
    cors_origins: str = "https://your-domain.com"

    # 프로덕션 로깅 설정
    log_all: bool = False
    log_api_request: bool = False
    log_ai_usage: bool = True  # AI 사용량 모니터링
    log_cache: bool = False
    log_error: bool = True  # 에러만 로깅

    # 프로덕션 성능 설정
    workers: int = 4
    timeout: int = 300  # 5분

    # 프로덕션 보안 설정
    access_token_expire_minutes: int = 15  # 짧은 토큰 만료 시간

    # 모니터링
    health_check: bool = True
    metrics: bool = True

    class Config:
        env_file = ".env.production"
        env_file_encoding = "utf-8"
