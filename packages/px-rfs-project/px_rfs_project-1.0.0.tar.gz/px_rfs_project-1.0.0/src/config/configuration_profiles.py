"""
RFS Framework 환경별 설정 프로필
15-configuration-injection 문서 패턴 적용
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

from src.shared.kernel import Result, Success, Failure
from src.config.settings import Environment, Settings


class ConfigurationProfile(Enum):
    """설정 프로필 타입"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


@dataclass
class ServiceConfiguration:
    """서비스별 설정"""

    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    max_connections: int = 20
    additional_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RedisConfiguration:
    """Redis 서비스 설정"""

    enabled: bool = True
    url: Optional[str] = None
    db: int = 0
    pool_max_size: int = 20
    pool_min_size: int = 1
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    health_check_interval: int = 30
    namespace: str = "px"
    default_ttl: int = 3600

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "enabled": self.enabled,
            "redis_url": self.url,
            "db": self.db,
            "pool_max_size": self.pool_max_size,
            "pool_min_size": self.pool_min_size,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "health_check_interval": self.health_check_interval,
            "namespace": self.namespace,
            "default_ttl": self.default_ttl,
        }


@dataclass
class RapidAPIConfiguration:
    """RapidAPI 서비스 설정"""

    enabled: bool = False
    api_key: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    youtube_host: str = "youtube-subtitle-downloader.p.rapidapi.com"
    linkedin_host: str = "linkedin-data-extractor.p.rapidapi.com"
    website_host: str = "url-to-text.p.rapidapi.com"

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "enabled": self.enabled,
            "api_key": self.api_key,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "youtube_host": self.youtube_host,
            "linkedin_host": self.linkedin_host,
            "website_host": self.website_host,
        }


@dataclass
class SpaCyConfiguration:
    """SpaCy NLP 서비스 설정"""

    enabled: bool = True
    model_name: str = "ko_core_news_sm"
    fallback_model: str = "en_core_web_sm"
    max_chunk_size: int = 2000
    overlap_size: int = 200
    use_gpu: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "enabled": self.enabled,
            "model_name": self.model_name,
            "fallback_model": self.fallback_model,
            "max_chunk_size": self.max_chunk_size,
            "overlap_size": self.overlap_size,
            "use_gpu": self.use_gpu,
        }


@dataclass
class SecurityConfiguration:
    """보안 설정"""

    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:3000"])
    secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_file_size: int = 10485760  # 10MB
    allowed_extensions: List[str] = field(
        default_factory=lambda: [".md", ".txt", ".pdf", ".pptx", ".xlsx"]
    )

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "cors_origins": self.cors_origins,
            "secret_key": self.secret_key,
            "jwt_algorithm": self.jwt_algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "max_file_size": self.max_file_size,
            "allowed_extensions": self.allowed_extensions,
        }


@dataclass
class ProfileConfiguration:
    """환경별 전체 설정 프로필"""

    profile: ConfigurationProfile
    redis: RedisConfiguration = field(default_factory=RedisConfiguration)
    rapidapi: RapidAPIConfiguration = field(default_factory=RapidAPIConfiguration)
    spacy: SpaCyConfiguration = field(default_factory=SpaCyConfiguration)
    security: SecurityConfiguration = field(default_factory=SecurityConfiguration)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "profile": self.profile.value,
            "redis": self.redis.to_dict(),
            "rapidapi": self.rapidapi.to_dict(),
            "spacy": self.spacy.to_dict(),
            "security": self.security.to_dict(),
        }


class ConfigurationProfileFactory:
    """설정 프로필 팩토리"""

    @staticmethod
    def create_development_profile() -> ProfileConfiguration:
        """개발 환경 프로필"""
        return ProfileConfiguration(
            profile=ConfigurationProfile.DEVELOPMENT,
            redis=RedisConfiguration(
                enabled=True,
                pool_max_size=10,
                health_check_interval=30,
                default_ttl=300,  # 5분
            ),
            rapidapi=RapidAPIConfiguration(enabled=False, timeout=30),
            spacy=SpaCyConfiguration(enabled=True, max_chunk_size=1000, use_gpu=False),
            security=SecurityConfiguration(
                cors_origins=["http://localhost:3000", "http://localhost:8080"],
                access_token_expire_minutes=60,  # 1시간
            ),
        )

    @staticmethod
    def create_staging_profile() -> ProfileConfiguration:
        """스테이징 환경 프로필"""
        return ProfileConfiguration(
            profile=ConfigurationProfile.STAGING,
            redis=RedisConfiguration(
                enabled=True,
                pool_max_size=30,
                health_check_interval=60,
                default_ttl=1800,  # 30분
            ),
            rapidapi=RapidAPIConfiguration(enabled=True, timeout=45),
            spacy=SpaCyConfiguration(enabled=True, max_chunk_size=2000, use_gpu=False),
            security=SecurityConfiguration(
                cors_origins=["https://staging.example.com"],
                access_token_expire_minutes=30,
            ),
        )

    @staticmethod
    def create_production_profile() -> ProfileConfiguration:
        """프로덕션 환경 프로필"""
        return ProfileConfiguration(
            profile=ConfigurationProfile.PRODUCTION,
            redis=RedisConfiguration(
                enabled=True,
                pool_max_size=50,
                pool_min_size=5,
                socket_timeout=10,
                health_check_interval=60,
                default_ttl=3600,  # 1시간
            ),
            rapidapi=RapidAPIConfiguration(enabled=True, timeout=60, max_retries=5),
            spacy=SpaCyConfiguration(
                enabled=True,
                max_chunk_size=2000,
                use_gpu=True,  # 프로덕션에서는 GPU 사용
            ),
            security=SecurityConfiguration(
                cors_origins=["https://api.example.com"],
                access_token_expire_minutes=15,  # 보안 강화
                max_file_size=5242880,  # 5MB로 축소
            ),
        )

    @staticmethod
    def create_test_profile() -> ProfileConfiguration:
        """테스트 환경 프로필"""
        return ProfileConfiguration(
            profile=ConfigurationProfile.TEST,
            redis=RedisConfiguration(
                enabled=False,  # 테스트에서는 Redis 비활성화
                pool_max_size=5,
                health_check_interval=10,
                default_ttl=60,
            ),
            rapidapi=RapidAPIConfiguration(
                enabled=False, timeout=10  # 테스트에서는 외부 API 비활성화
            ),
            spacy=SpaCyConfiguration(
                enabled=True,
                model_name="en_core_web_sm",  # 테스트용 영어 모델
                max_chunk_size=500,
                use_gpu=False,
            ),
            security=SecurityConfiguration(
                cors_origins=["http://localhost:3000"],
                secret_key="test-secret-key",
                access_token_expire_minutes=5,  # 짧은 만료 시간
            ),
        )

    @classmethod
    def create_profile(
        cls, environment: Environment
    ) -> Result[ProfileConfiguration, str]:
        """환경에 따른 프로필 생성"""
        try:
            if environment == Environment.DEVELOPMENT:
                return Success(cls.create_development_profile())
            elif environment == Environment.STAGING:
                return Success(cls.create_staging_profile())
            elif environment == Environment.PRODUCTION:
                return Success(cls.create_production_profile())
            elif environment == Environment.TEST:
                return Success(cls.create_test_profile())
            # 모든 Environment enum case가 처리됨 - else는 도달 불가능
            # else:
            #     return Failure(f"Unknown environment: {environment}")
        except Exception as e:
            return Failure(f"Failed to create profile: {str(e)}")

    @classmethod
    def create_from_settings(
        cls, settings: Settings
    ) -> Result[ProfileConfiguration, str]:
        """Settings 객체로부터 프로필 생성"""
        profile_result = cls.create_profile(settings.environment)

        if profile_result.is_failure():
            return Failure(profile_result.get_error() or "Profile creation failed")

        profile = profile_result.get_or_none()
        if profile is None:
            return Failure("Profile creation returned None")

        try:
            # Settings의 값으로 프로필 업데이트
            if settings.redis_url:
                profile.redis.url = settings.redis_url
                profile.redis.enabled = settings.use_redis
                profile.redis.db = settings.redis_db
                profile.redis.pool_max_size = settings.redis_max_connections
                profile.redis.socket_timeout = settings.redis_socket_timeout
                profile.redis.socket_connect_timeout = (
                    settings.redis_socket_connect_timeout
                )
                profile.redis.default_ttl = settings.redis_cache_ttl

            if settings.rapidapi_key:
                profile.rapidapi.api_key = settings.rapidapi_key
                profile.rapidapi.enabled = True

            # 보안 설정 업데이트
            profile.security.cors_origins = settings.get_cors_origins_list()
            profile.security.secret_key = settings.secret_key
            profile.security.jwt_algorithm = settings.jwt_algorithm
            profile.security.access_token_expire_minutes = (
                settings.access_token_expire_minutes
            )
            profile.security.max_file_size = settings.max_file_size
            profile.security.allowed_extensions = settings.get_allowed_extensions_list()

            return Success(profile)

        except Exception as e:
            return Failure(f"Failed to update profile from settings: {str(e)}")
