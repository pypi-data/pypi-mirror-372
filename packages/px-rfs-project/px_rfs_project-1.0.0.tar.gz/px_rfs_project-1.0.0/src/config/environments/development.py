"""
개발 환경 설정
"""

from src.config.settings import Settings, Environment, LogLevel


class DevelopmentSettings(Settings):
    """개발 환경 전용 설정"""

    # 개발 환경 기본값 오버라이드
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    log_level: LogLevel = LogLevel.DEBUG

    # 개발용 Redis 설정
    use_redis: bool = True
    redis_cache_ttl: int = 300  # 5분 (개발 시 짧은 캐시)

    # 개발용 CORS 설정
    cors_origins: str = (
        "http://localhost:3000,http://localhost:8080,http://localhost:5173"
    )

    # 개발용 로깅 설정
    log_all: bool = True
    log_api_request: bool = True
    log_ai_usage: bool = True
    log_cache: bool = True

    # 핫 리로드
    reload: bool = True

    # 워커 설정 (개발 시 단일 워커)
    workers: int = 1

    class Config:
        env_file = ".env.development"
        env_file_encoding = "utf-8"
