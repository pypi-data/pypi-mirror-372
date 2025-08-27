"""
Redis 설정 전용 클래스
RFS Framework 패턴 준수
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from urllib.parse import urlparse

from src.shared.kernel import Result, Success, Failure
from src.config.settings import Settings, Environment


@dataclass
class RedisConnectionInfo:
    """Redis 연결 정보"""

    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    db: int = 0
    ssl: bool = False


class RedisCloudConfig(BaseModel):
    """Redis Cloud 전용 설정 클래스"""

    # 연결 정보
    redis_url: str = Field(..., description="Redis Cloud 연결 URL")
    db: int = Field(0, ge=0, le=15, description="Redis 데이터베이스 번호")

    # 연결 풀 설정
    pool_max_size: int = Field(50, ge=1, le=100, description="최대 연결 수")
    pool_min_size: int = Field(1, ge=1, description="최소 연결 수")

    # 타임아웃 설정
    socket_timeout: int = Field(5, ge=1, le=60, description="소켓 타임아웃 (초)")
    socket_connect_timeout: int = Field(
        5, ge=1, le=60, description="연결 타임아웃 (초)"
    )

    # Redis Cloud 최적화 설정
    socket_keepalive: bool = Field(True, description="Keep-Alive 사용 여부")
    health_check_interval: int = Field(
        30, ge=10, le=300, description="헬스체크 간격 (초)"
    )

    # 보안 및 인코딩
    ssl: bool = Field(False, description="SSL/TLS 사용 여부")
    decode_responses: bool = Field(True, description="응답 자동 디코딩")

    # 캐시 설정
    default_ttl: int = Field(3600, ge=60, description="기본 캐시 TTL (초)")
    namespace: str = Field("px", min_length=1, description="캐시 네임스페이스")

    # 환경별 설정
    environment: Environment = Field(Environment.DEVELOPMENT, description="실행 환경")

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, v: str) -> str:
        """Redis URL 검증"""
        if not v.startswith("redis://"):
            raise ValueError("올바른 Redis URL이 아닙니다 (redis://로 시작해야 함)")

        try:
            parsed = urlparse(v)
            if not parsed.hostname:
                raise ValueError("Redis URL에 호스트가 없습니다")
            if not parsed.port:
                raise ValueError("Redis URL에 포트가 없습니다")
        except Exception as e:
            raise ValueError(f"Redis URL 파싱 실패: {str(e)}")

        return v

    @field_validator("namespace")
    @classmethod
    def validate_namespace(cls, v: str) -> str:
        """네임스페이스 검증"""
        if not v.isalnum():
            raise ValueError("네임스페이스는 영숫자만 허용됩니다")
        return v.lower()

    def parse_connection_info(self) -> Result[RedisConnectionInfo, str]:
        """Redis URL을 연결 정보로 파싱"""
        try:
            parsed = urlparse(self.redis_url)

            return Success(
                RedisConnectionInfo(
                    host=parsed.hostname or "localhost",
                    port=parsed.port or 6379,
                    username=parsed.username,
                    password=parsed.password,
                    db=self.db,
                    ssl=self.ssl,
                )
            )
        except Exception as e:
            return Failure(f"Redis URL 파싱 실패: {str(e)}")

    def get_connection_params(self) -> Dict[str, Any]:
        """aioredis 연결 매개변수 생성"""
        conn_info_result = self.parse_connection_info()
        if conn_info_result.is_failure():
            raise ValueError(conn_info_result.get_error() or "Connection failed")

        conn_info = conn_info_result.get_or_none()
        if conn_info is None:
            raise ValueError("Connection info is None")

        params = {
            "url": self.redis_url,
            "decode_responses": self.decode_responses,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "socket_keepalive": self.socket_keepalive,
            "max_connections": self.pool_max_size,
            "retry_on_timeout": True,
        }

        # 환경별 최적화
        if self.environment == Environment.PRODUCTION:
            params.update(
                {
                    "max_connections": min(self.pool_max_size, 100),
                    "socket_timeout": max(self.socket_timeout, 10),  # 최소 10초
                    "socket_keepalive": True,
                }
            )
        elif self.environment == Environment.DEVELOPMENT:
            params.update(
                {"max_connections": min(self.pool_max_size, 20), "socket_timeout": 5}
            )
        elif self.environment == Environment.TEST:
            params.update({"max_connections": 5, "socket_timeout": 3})

        return params

    def get_rfs_cache_config(self) -> Dict[str, Any]:
        """RFS Framework RedisCacheConfig 호환 설정"""
        conn_info_result = self.parse_connection_info()
        if conn_info_result.is_failure():
            raise ValueError(conn_info_result.get_error() or "Connection failed")

        conn_info = conn_info_result.get_or_none()
        if conn_info is None:
            raise ValueError("Connection info is None")

        config = {
            "redis_url": self.redis_url,
            "host": conn_info.host,
            "port": conn_info.port,
            "db": self.db,
            "default_ttl": self.default_ttl,
            "pool_max_size": self.pool_max_size,
            "pool_min_size": self.pool_min_size,
            "decode_responses": self.decode_responses,
            "ssl": self.ssl,
            "socket_timeout": self.socket_timeout,
            "socket_keepalive": self.socket_keepalive,
            "socket_keepalive_options": {},
            "health_check_interval": self.health_check_interval,
            "namespace": self.namespace,
        }

        # 환경별 최적화
        if self.environment == Environment.PRODUCTION:
            config.update(
                {
                    "pool_max_size": min(self.pool_max_size, 100),
                    "health_check_interval": 60,  # 프로덕션에서는 더 자주 체크
                    "socket_keepalive": True,
                }
            )
        elif self.environment == Environment.DEVELOPMENT:
            config.update(
                {
                    "pool_max_size": min(self.pool_max_size, 20),
                    "health_check_interval": 30,
                    "default_ttl": 300,  # 개발환경에서는 짧은 TTL
                }
            )
        elif self.environment == Environment.TEST:
            config.update(
                {"pool_max_size": 5, "health_check_interval": 10, "default_ttl": 60}
            )

        return config

    def validate_connection_params(self) -> Result[None, str]:
        """연결 매개변수 전체 검증"""
        errors = []

        # URL 파싱 테스트
        conn_result = self.parse_connection_info()
        if conn_result.is_failure():
            errors.append(conn_result.get_error() or "Connection error")

        # 환경별 검증
        if self.environment == Environment.PRODUCTION:
            if self.socket_timeout < 10:
                errors.append(
                    "프로덕션 환경에서는 socket_timeout이 10초 이상이어야 합니다"
                )
            if self.pool_max_size < 20:
                errors.append(
                    "프로덕션 환경에서는 pool_max_size가 20 이상이어야 합니다"
                )

        if errors:
            return Failure(f"Redis 설정 검증 실패: {'; '.join(errors)}")

        return Success(None)


class RedisConfigFactory:
    """Redis 설정 팩토리"""

    @staticmethod
    def create_from_settings(settings: Settings) -> Result[RedisCloudConfig, str]:
        """Settings 객체로부터 Redis 설정 생성"""
        if not settings.redis_url:
            return Failure("Redis URL이 설정되지 않았습니다")

        try:
            config = RedisCloudConfig(
                redis_url=settings.redis_url,
                db=settings.redis_db,
                pool_max_size=settings.redis_max_connections,
                pool_min_size=1,  # 기본값
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                socket_keepalive=True,  # 기본값
                health_check_interval=30,  # 기본값
                ssl=settings.redis_ssl,
                decode_responses=settings.redis_decode_responses,
                default_ttl=settings.redis_cache_ttl,
                namespace="px",  # 기본값
                environment=settings.environment,
            )

            # 설정 검증
            validation_result = config.validate_connection_params()
            if validation_result.is_failure():
                return Failure(validation_result.get_error() or "Validation failed")

            return Success(config)

        except Exception as e:
            return Failure(f"Redis 설정 생성 실패: {str(e)}")

    @staticmethod
    def create_for_environment(
        environment: Environment, redis_url: str, **overrides: Any
    ) -> Result[RedisCloudConfig, str]:
        """환경별 최적화된 Redis 설정 생성"""
        base_config: Dict[str, Any] = {"redis_url": redis_url, "environment": environment}

        # 환경별 기본값
        if environment == Environment.PRODUCTION:
            base_config.update(
                {
                    "pool_max_size": 50,
                    "socket_timeout": 10,
                    "health_check_interval": 60,
                    "default_ttl": 7200,  # 2시간
                }
            )
        elif environment == Environment.DEVELOPMENT:
            base_config.update(
                {
                    "pool_max_size": 10,
                    "socket_timeout": 5,
                    "health_check_interval": 30,
                    "default_ttl": 300,  # 5분
                }
            )
        elif environment == Environment.TEST:
            base_config.update(
                {
                    "pool_max_size": 5,
                    "socket_timeout": 3,
                    "health_check_interval": 10,
                    "default_ttl": 60,  # 1분
                }
            )

        # 사용자 재정의 적용
        base_config.update(overrides)

        try:
            config = RedisCloudConfig(**base_config)

            # 설정 검증
            validation_result = config.validate_connection_params()
            if validation_result.is_failure():
                return Failure(validation_result.get_error() or "Validation failed")

            return Success(config)

        except Exception as e:
            return Failure(f"환경별 Redis 설정 생성 실패: {str(e)}")
