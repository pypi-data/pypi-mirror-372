"""
애플리케이션 설정 관리
RFS Framework 패턴 사용, DB 없는 구조
"""

from functools import lru_cache
from typing import Optional, List, Dict, Any, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from enum import Enum
from src.shared.kernel import Result, Success, Failure
from src.shared.hof import pipe, compact_map, partition, when, tap


class Environment(str, Enum):
    """실행 환경"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(str, Enum):
    """로그 레벨"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    애플리케이션 전체 설정
    DB를 사용하지 않고 Redis와 GCS를 활용
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",  # 추가 환경 변수 허용
    )

    # ========================================
    # 애플리케이션 기본 설정
    # ========================================
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="실행 환경"
    )

    app_name: str = Field(
        default="Cosmos Enterprise Server", description="애플리케이션 이름"
    )

    app_version: str = Field(default="1.0.0", description="애플리케이션 버전")

    debug: bool = Field(default=False, description="디버그 모드")

    log_level: LogLevel = Field(default=LogLevel.INFO, description="로그 레벨")

    # ========================================
    # API 서버 설정
    # ========================================
    api_host: str = Field(default="0.0.0.0", description="API 서버 호스트")

    api_port: int = Field(default=8001, description="API 서버 포트")

    api_prefix: str = Field(default="/api/v1", description="API 경로 prefix")

    workers: int = Field(default=1, description="워커 프로세스 수")

    timeout: int = Field(default=60, description="요청 타임아웃 (초)")

    # ========================================
    # Google Cloud Storage 설정
    # ========================================
    gcs_bucket: Optional[str] = Field(default=None, description="GCS 버킷 이름")

    gcs_project: Optional[str] = Field(default=None, description="GCP 프로젝트 ID")

    google_application_credentials: Optional[str] = Field(
        default=None, description="Google 인증 파일 경로"
    )

    # ========================================
    # Redis Cloud 캐시 설정
    # ========================================
    redis_url: Optional[str] = Field(default=None, description="Redis Cloud 연결 URL")

    redis_db: int = Field(default=0, description="Redis 데이터베이스 번호")

    redis_max_connections: int = Field(default=50, description="Redis 최대 연결 수")

    redis_cache_ttl: int = Field(default=3600, description="기본 캐시 TTL (초)")

    redis_ssl: bool = Field(default=False, description="Redis SSL/TLS 사용 여부")

    redis_decode_responses: bool = Field(
        default=True, description="Redis 응답 자동 디코딩"
    )

    redis_socket_timeout: int = Field(default=5, description="Redis 소켓 타임아웃 (초)")

    redis_socket_connect_timeout: int = Field(
        default=5, description="Redis 연결 타임아웃 (초)"
    )

    use_redis: bool = Field(default=False, description="Redis 사용 여부")

    # ========================================
    # AI/ML API 설정
    # ========================================
    google_api_key: Optional[str] = Field(
        default=None, description="Google Gemini API 키"
    )

    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")

    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic Claude API 키"
    )

    aws_access_key_id: Optional[str] = Field(
        default=None, description="AWS Access Key (Bedrock)"
    )

    aws_secret_access_key: Optional[str] = Field(
        default=None, description="AWS Secret Key (Bedrock)"
    )

    aws_region: str = Field(default="ap-northeast-2", description="AWS Region")

    bedrock_model_id: Optional[str] = Field(
        default=None, description="AWS Bedrock 모델 ID"
    )

    # ========================================
    # 외부 API 설정
    # ========================================
    rapidapi_key: Optional[str] = Field(default=None, description="RapidAPI 키")

    divona_v3_api_url: Optional[str] = Field(default=None, description="디보나 API URL")

    divona_v3_enabled: bool = Field(default=False, description="디보나 API 사용 여부")

    divona_v3_timeout: int = Field(default=60, description="디보나 API 타임아웃")

    # ========================================
    # Cloud Tasks 설정
    # ========================================
    cloud_tasks_location: str = Field(
        default="asia-northeast3", description="Cloud Tasks 큐 위치"
    )

    cloud_tasks_queue: str = Field(
        default="cosmos-processing", description="Cloud Tasks 큐 이름"
    )

    cloud_run_worker_url: Optional[str] = Field(
        default=None, description="Cloud Run Worker URL"
    )

    # ========================================
    # 파일 처리 설정
    # ========================================
    upload_dir: str = Field(default="./uploads", description="로컬 업로드 디렉토리")

    max_file_size: int = Field(
        default=10485760, description="최대 파일 크기 (바이트)"  # 10MB
    )

    allowed_extensions: str = Field(
        default=".md,.txt,.pdf,.pptx,.xlsx", description="허용된 파일 확장자"
    )

    max_files: int = Field(default=10, description="동시 업로드 최대 파일 수")

    chunk_size: int = Field(default=2000, description="텍스트 청크 크기")

    # ========================================
    # 보안 설정
    # ========================================
    cors_origins: str = Field(
        default="http://localhost:3000", description="CORS 허용 오리진"
    )

    secret_key: str = Field(
        default="your-secret-key-change-this-in-production",
        description="애플리케이션 시크릿 키",
    )

    jwt_algorithm: str = Field(default="HS256", description="JWT 알고리즘")

    access_token_expire_minutes: int = Field(
        default=30, description="액세스 토큰 만료 시간 (분)"
    )

    # ========================================
    # 모니터링 설정
    # ========================================
    health_check: bool = Field(default=True, description="헬스체크 활성화")

    metrics: bool = Field(default=False, description="메트릭 수집 활성화")

    # ========================================
    # 로깅 설정
    # ========================================
    log_all: bool = Field(default=False, description="전체 로그 활성화")

    log_redis_metrics: bool = Field(default=False, description="Redis 메트릭 로그")

    log_api_request: bool = Field(default=False, description="API 요청 로그")

    log_ai_usage: bool = Field(default=False, description="AI 사용 로그")

    log_cache: bool = Field(default=False, description="캐시 로그")

    log_error: bool = Field(default=True, description="에러 로그")

    # ========================================
    # Validators
    # ========================================
    @field_validator("environment", mode="before")
    @classmethod
    def set_debug_from_environment(cls, v: str) -> str:
        """환경에 따라 디버그 모드 자동 설정"""
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> str:
        """CORS 오리진 문자열 파싱"""
        if isinstance(v, str):
            return v
        return ",".join(v) if isinstance(v, list) else v

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Union[str, List[str]]) -> str:
        """허용 확장자 문자열 파싱"""
        if isinstance(v, str):
            return v
        return ",".join(v) if isinstance(v, list) else v

    # ========================================
    # Helper Methods
    # ========================================
    def get_cors_origins_list(self) -> List[str]:
        """CORS 오리진 리스트 반환 - RFS HOF 패턴 사용"""
        if not self.cors_origins:
            return []

        # RFS HOF 패턴: 함수형 데이터 처리
        origins_list = self.cors_origins.split(",")
        filtered_origins = compact_map(
            lambda item: item.strip() if item.strip() else None, origins_list
        )
        return filtered_origins

    def get_allowed_extensions_list(self) -> List[str]:
        """허용 확장자 리스트 반환 - RFS HOF 패턴 사용"""
        if not self.allowed_extensions:
            return []

        # RFS HOF 패턴: 함수형 데이터 처리
        extensions_list = self.allowed_extensions.split(",")
        filtered_extensions = compact_map(
            lambda ext: ext.strip() if ext.strip() else None, extensions_list
        )
        return filtered_extensions

    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        """개발 환경 여부"""
        return self.environment == Environment.DEVELOPMENT

    def get_redis_config(self) -> Dict[str, Any]:
        """Redis Cloud 설정 딕셔너리 반환"""
        if not self.use_redis or not self.redis_url:
            return {}

        return {
            "redis_url": self.redis_url,
            "db": self.redis_db,
            "ttl": self.redis_cache_ttl,
            "pool_max_size": self.redis_max_connections,
            "ssl": self.redis_ssl,
            "decode_responses": self.redis_decode_responses,
            "socket_timeout": self.redis_socket_timeout,
            "socket_connect_timeout": self.redis_socket_connect_timeout,
            "namespace": "px",  # 고정 네임스페이스
        }

    def get_gcs_config(self) -> Dict[str, Any]:
        """GCS 설정 딕셔너리 반환"""
        if not self.gcs_bucket:
            return {}

        return {
            "bucket": self.gcs_bucket,
            "project": self.gcs_project,
            "credentials": self.google_application_credentials,
        }

    def validate_config(self) -> Result[None, str]:
        """설정 유효성 검증 - RFS HOF 패턴 사용"""

        # RFS HOF 패턴: 함수형 검증 파이프라인
        validation_functions = [
            self._validate_production_settings,
            self._validate_ai_api_keys,
            self._validate_file_settings,
        ]

        # 모든 검증 함수 실행하고 에러 수집
        all_errors = compact_map(
            lambda validate_fn: validate_fn(), validation_functions
        )

        # 평탄화된 에러 리스트
        flattened_errors = [error for error_list in all_errors for error in error_list]

        return (
            Failure(f"설정 오류: {', '.join(flattened_errors)}")
            if flattened_errors
            else Success(None)
        )

    def _validate_production_settings(self) -> List[str]:
        """프로덕션 환경 설정 검증"""
        if not self.is_production():
            return []

        # RFS HOF 패턴: 조건부 검증 함수들
        validations = [
            (
                "Production requires a secure secret key",
                lambda: self.secret_key == "your-secret-key-change-this-in-production",
            ),
            ("Debug mode should be disabled in production", lambda: self.debug),
            ("Redis is recommended for production", lambda: not self.use_redis),
        ]

        return compact_map(
            lambda validation: validation[0] if validation[1]() else None, validations
        )

    def _validate_ai_api_keys(self) -> List[str]:
        """AI API 키 검증"""
        ai_keys = [
            self.google_api_key,
            self.openai_api_key,
            self.anthropic_api_key,
            (self.aws_access_key_id and self.aws_secret_access_key),
        ]

        return ["At least one AI API key is required"] if not any(ai_keys) else []

    def _validate_file_settings(self) -> List[str]:
        """파일 업로드 설정 검증"""
        validations = [
            ("max_file_size must be positive", lambda: self.max_file_size <= 0),
            ("max_files must be positive", lambda: self.max_files <= 0),
        ]

        return compact_map(
            lambda validation: validation[0] if validation[1]() else None, validations
        )


@lru_cache()
def get_settings() -> Settings:
    """
    설정 싱글톤 인스턴스 반환
    캐시를 통해 한 번만 로드
    """
    return Settings()
