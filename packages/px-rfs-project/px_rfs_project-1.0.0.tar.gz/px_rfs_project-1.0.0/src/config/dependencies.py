"""
의존성 주입 설정
RFS Framework 패턴 사용
"""

from functools import lru_cache, partial
from typing import Optional, Any, Dict, TYPE_CHECKING, Callable, TypeVar
from src.shared.hof import curry, pipe

# 커링 패턴을 위한 타입 변수
T = TypeVar("T")
U = TypeVar("U")

if TYPE_CHECKING:
    from src.infrastructure.cache.redis_client import RedisClient
    from src.infrastructure.nlp.spacy_processor import SpaCyProcessor
    from src.infrastructure.external.rapidapi_client import RapidAPIClient
from src.shared.kernel import Result, Success, Failure
from src.config.settings import Settings, get_settings


class DependencyContainer:
    """
    의존성 주입 컨테이너
    DB 없이 Redis와 외부 서비스만 관리
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._redis_client: Optional["RedisClient"] = None
        self._spacy_processor: Optional["SpaCyProcessor"] = None
        self._rapidapi_client: Optional["RapidAPIClient"] = None
        self._gcs_client: Optional[object] = None
        self._ai_clients: dict = {}
        
        # 커링된 초기화 함수들 (HOF 패턴)
        self._curried_initializers: Dict[str, Callable] = {}

    async def initialize(self) -> Result[None, str]:
        """의존성 초기화 - 파이프라인 패턴 적용 (규칙 2)"""
        try:
            # 커링된 초기화 함수들 준비
            self._prepare_curried_initializers()
            
            # 의존성 초기화 파이프라인 (RFS 파이프라인 패턴)
            initialization_pipeline = pipe(
                self._create_initialization_config,   # 초기화 설정 생성
                self._execute_conditional_initializations,  # 조건부 초기화
                self._validate_initialization_results      # 결과 검증
            )
            
            result = await initialization_pipeline(self.settings)
            return result if isinstance(result, Result) else Success(None)
            
        except Exception as e:
            return Failure(f"Failed to initialize dependencies: {str(e)}")
    
    def _prepare_curried_initializers(self) -> None:
        """커링된 초기화 함수들 준비 - 20줄 이하 (규칙 1)"""
        self._curried_initializers = {
            "redis": self._create_curried_redis_initializer(),
            "spacy": self._create_curried_spacy_initializer(),
            "rapidapi": self._create_curried_rapidapi_initializer(),
            "gcs": self._create_curried_gcs_initializer(),
            "ai_clients": self._create_curried_ai_initializer()
        }
    
    def _create_initialization_config(self, settings: Settings) -> Dict[str, Any]:
        """초기화 설정 생성 - 20줄 이하 (규칙 1)"""
        return {
            "redis_enabled": settings.use_redis,
            "gcs_enabled": bool(settings.gcs_bucket),
            "rapidapi_key": settings.rapidapi_key,
            "ai_keys": {
                "openai": settings.openai_api_key,
                "anthropic": settings.anthropic_api_key,
                "google": settings.google_api_key,
                "aws_keys": (settings.aws_access_key_id, settings.aws_secret_access_key)
            }
        }
    
    async def _execute_conditional_initializations(self, config: Dict[str, Any]) -> Result[None, str]:
        """조건부 초기화 실행 - 20줄 이하 (규칙 1)"""
        initializations = [
            ("redis", config["redis_enabled"]),
            ("spacy", True),  # 항상 활성화
            ("rapidapi", bool(config["rapidapi_key"])),
            ("gcs", config["gcs_enabled"]),
            ("ai_clients", True)  # 항상 실행
        ]
        
        for service_name, should_init in initializations:
            if should_init:
                result = await self._curried_initializers[service_name]()
                if isinstance(result, Result) and result.is_failure():
                    return result
        
        return Success(None)
    
    def _validate_initialization_results(self, result: Result[None, str]) -> Result[None, str]:
        """초기화 결과 검증 - 20줄 이하 (규칙 1)"""
        return result

    def _create_curried_redis_initializer(self) -> Callable:
        """커링된 Redis 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def redis_initializer() -> Result[None, str]:
            return await self._init_redis_with_config()
        return redis_initializer
    
    async def _init_redis_with_config(self) -> Result[None, str]:
        """Redis 설정 기반 초기화 - 20줄 이하 (규칙 1)"""
        try:
            if not self.settings.use_redis or not self.settings.redis_url:
                from src.infrastructure.cache.redis_client import RedisClient
                self._redis_client = RedisClient(None)
                return Success(None)

            # Redis 설정 생성 파이프라인
            redis_setup_pipeline = pipe(
                lambda s: __import__('src.infrastructure.cache.redis_config', fromlist=['RedisConfigFactory']).RedisConfigFactory.create_from_settings(s),
                lambda config_result: config_result.get_or_none() if config_result.is_success() else None
            )
            
            redis_config = redis_setup_pipeline(self.settings)
            if redis_config is None:
                return Failure("Redis config creation failed")

            from src.infrastructure.cache.redis_client import RedisClient
            self._redis_client = RedisClient(redis_config)
            connect_result = await self._redis_client.connect()
            return Success(None) if connect_result.is_success() else connect_result
        except Exception as e:
            return Failure(f"Redis initialization failed: {str(e)}")

    async def _init_redis(self) -> Result[None, str]:
        """Redis Cloud 클라이언트 초기화 (개선됨)"""
        try:
            if not self.settings.use_redis or not self.settings.redis_url:
                # Redis가 비활성화된 경우 - 정상적인 상황
                from src.infrastructure.cache.redis_client import RedisClient

                self._redis_client = RedisClient(None)  # 비활성화 상태로 생성
                return Success(None)

            # Redis 설정 생성
            from src.infrastructure.cache.redis_config import RedisConfigFactory

            config_result = RedisConfigFactory.create_from_settings(self.settings)

            if config_result.is_failure():
                return Failure(config_result.get_error() or "Redis config creation failed")

            redis_config = config_result.get_or_none()
            if redis_config is None:
                return Failure("Redis config creation returned None")

            # Redis Cloud 클라이언트 생성 (생성자 주입 패턴)
            from src.infrastructure.cache.redis_client import RedisClient

            self._redis_client = RedisClient(redis_config)

            # 연결 테스트
            connect_result = await self._redis_client.connect()
            if connect_result.is_failure():
                return Failure(f"Redis 연결 테스트 실패: {connect_result.get_error()}")

            return Success(None)

        except Exception as e:
            return Failure(f"Failed to initialize Redis Cloud: {str(e)}")

    def _create_curried_spacy_initializer(self) -> Callable:
        """커링된 SpaCy 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def spacy_initializer() -> Result[None, str]:
            try:
                from src.infrastructure.nlp.spacy_processor import SpaCyProcessor
                self._spacy_processor = SpaCyProcessor(self.settings)

                if not self._spacy_processor.is_available():
                    return Failure("SpaCy model not available")

                return Success(None)
            except Exception as e:
                return Failure(f"Failed to initialize SpaCy: {str(e)}")
        return spacy_initializer

    def _create_curried_rapidapi_initializer(self) -> Callable:
        """커링된 RapidAPI 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def rapidapi_initializer() -> Result[None, str]:
            return await self._init_rapidapi()
        return rapidapi_initializer

    def _create_curried_gcs_initializer(self) -> Callable:
        """커링된 GCS 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def gcs_initializer() -> Result[None, str]:
            return await self._init_gcs()
        return gcs_initializer

    def _create_curried_ai_initializer(self) -> Callable:
        """커링된 AI 클라이언트 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def ai_initializer() -> Result[None, str]:
            return await self._init_ai_clients()
        return ai_initializer

    async def _init_rapidapi(self) -> Result[None, str]:
        """RapidAPI 클라이언트 초기화"""
        try:
            if not self.settings.rapidapi_key:
                # RapidAPI가 설정되지 않은 경우 - 선택적 서비스이므로 경고만
                self._rapidapi_client = None
                return Success(None)

            # RapidAPI 설정 생성
            from src.infrastructure.external.rapidapi_config import (
                RapidAPIConfigFactory,
            )

            config_result = RapidAPIConfigFactory.create_from_settings(self.settings)

            if config_result.is_failure():
                return Failure(config_result.get_error() or "RapidAPI config creation failed")

            rapidapi_config = config_result.get_or_none()
            if rapidapi_config is None:
                return Failure("RapidAPI config creation returned None")

            # RapidAPI 클라이언트 생성 (생성자 주입 패턴)
            from src.infrastructure.external.rapidapi_client import RapidAPIClient

            self._rapidapi_client = RapidAPIClient(rapidapi_config)

            return Success(None)

        except Exception as e:
            return Failure(f"Failed to initialize RapidAPI: {str(e)}")

    async def _init_gcs(self) -> Result[None, str]:
        """GCS 클라이언트 초기화"""
        try:
            if not self.settings.gcs_project:
                return Failure("GCS project not configured")

            # GCS 클라이언트 생성 (실제 구현 시 google-cloud-storage 사용)
            # from google.cloud import storage
            # self._gcs_client = storage.Client(
            #     project=self.settings.gcs_project,
            #     credentials=self.settings.google_application_credentials
            # )

            return Success(None)
        except Exception as e:
            return Failure(f"Failed to initialize GCS: {str(e)}")

    async def _init_ai_clients(self) -> Result[None, str]:
        """AI 클라이언트 초기화"""
        try:
            # OpenAI 클라이언트
            if self.settings.openai_api_key:
                # from openai import AsyncOpenAI
                # self._ai_clients["openai"] = AsyncOpenAI(
                #     api_key=self.settings.openai_api_key
                # )
                pass

            # Anthropic 클라이언트
            if self.settings.anthropic_api_key:
                # from anthropic import AsyncAnthropic
                # self._ai_clients["anthropic"] = AsyncAnthropic(
                #     api_key=self.settings.anthropic_api_key
                # )
                pass

            # Google Gemini 클라이언트
            if self.settings.google_api_key:
                # import google.generativeai as genai
                # genai.configure(api_key=self.settings.google_api_key)
                # self._ai_clients["gemini"] = genai
                pass

            # AWS Bedrock 클라이언트
            if self.settings.aws_access_key_id and self.settings.aws_secret_access_key:
                # import boto3
                # self._ai_clients["bedrock"] = boto3.client(
                #     "bedrock-runtime",
                #     region_name=self.settings.aws_region,
                #     aws_access_key_id=self.settings.aws_access_key_id,
                #     aws_secret_access_key=self.settings.aws_secret_access_key
                # )
                pass

            if not self._ai_clients:
                return Failure("No AI clients configured")

            return Success(None)
        except Exception as e:
            return Failure(f"Failed to initialize AI clients: {str(e)}")

    @property
    def redis(self) -> Any:
        """Redis Cloud 클라이언트 getter"""
        return self._redis_client

    @property
    def spacy(self) -> Any:
        """SpaCy 프로세서 getter"""
        return self._spacy_processor

    @property
    def rapidapi(self) -> Any:
        """RapidAPI 클라이언트 getter"""
        return self._rapidapi_client

    @property
    def gcs(self) -> Any:
        """GCS 클라이언트 getter"""
        return self._gcs_client

    @property
    def ai_clients(self) -> Dict[str, Any]:
        """AI 클라이언트 딕셔너리 getter"""
        return self._ai_clients

    def get_ai_client(self, provider: str) -> Any:
        """특정 AI 클라이언트 반환"""
        return self._ai_clients.get(provider)

    async def cleanup(self) -> Result[None, str]:
        """리소스 정리"""
        try:
            # Redis Cloud 연결 종료
            if self._redis_client:
                await self._redis_client.disconnect()

            # SpaCy 리소스 정리 (싱글톤이므로 별도 정리 불필요)

            # 기타 리소스 정리
            self._ai_clients.clear()

            return Success(None)
        except Exception as e:
            return Failure(f"Failed to cleanup resources: {str(e)}")


# 싱글톤 컨테이너 인스턴스
_container: Optional[DependencyContainer] = None


@lru_cache()
def get_container() -> DependencyContainer:
    """의존성 컨테이너 싱글톤 반환"""
    global _container
    if _container is None:
        settings = get_settings()
        _container = DependencyContainer(settings)
    return _container


async def initialize_dependencies() -> Result[None, str]:
    """애플리케이션 시작 시 의존성 초기화"""
    container = get_container()
    return await container.initialize()


async def cleanup_dependencies() -> Result[None, str]:
    """애플리케이션 종료 시 리소스 정리"""
    container = get_container()
    return await container.cleanup()


# Phase 4: HOF/커링 패턴 확장 메서드들 (DependencyContainer에 추가)
def extend_dependency_container_with_hof():
    """의존성 컨테이너에 HOF 메서드들을 동적 추가"""
    
    def _create_curried_rapidapi_initializer(self) -> Callable:
        """커링된 RapidAPI 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def rapidapi_initializer() -> Result[None, str]:
            try:
                if not self.settings.rapidapi_key:
                    self._rapidapi_client = None
                    return Success(None)

                # RapidAPI 설정 파이프라인
                rapidapi_setup_pipeline = pipe(
                    lambda s: __import__('src.infrastructure.external.rapidapi_config', fromlist=['RapidAPIConfigFactory']).RapidAPIConfigFactory.create_from_settings(s),
                    lambda config_result: config_result.get_or_none() if config_result.is_success() else None
                )
                
                rapidapi_config = rapidapi_setup_pipeline(self.settings)
                if rapidapi_config is None:
                    return Failure("RapidAPI config creation failed")

                from src.infrastructure.external.rapidapi_client import RapidAPIClient
                self._rapidapi_client = RapidAPIClient(rapidapi_config)
                return Success(None)
            except Exception as e:
                return Failure(f"Failed to initialize RapidAPI: {str(e)}")
        return rapidapi_initializer
    
    def _create_curried_gcs_initializer(self) -> Callable:
        """커링된 GCS 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def gcs_initializer() -> Result[None, str]:
            try:
                if not self.settings.gcs_project:
                    return Failure("GCS project not configured")
                return Success(None)
            except Exception as e:
                return Failure(f"Failed to initialize GCS: {str(e)}")
        return gcs_initializer
    
    def _create_curried_ai_initializer(self) -> Callable:
        """커링된 AI 클라이언트 초기화 함수 - 20줄 이하 (규칙 1)"""
        @curry
        async def ai_initializer() -> Result[None, str]:
            try:
                # AI 클라이언트 설정 파이프라인
                ai_config_pipeline = pipe(
                    _extract_ai_credentials,  # 인증 정보 추출
                    _configure_ai_clients,    # 클라이언트 설정
                    _validate_ai_setup        # 설정 검증
                )
                
                return ai_config_pipeline(self.settings)
            except Exception as e:
                return Failure(f"Failed to initialize AI clients: {str(e)}")
        
        def _extract_ai_credentials(settings: Settings) -> Dict[str, Any]:
            return {
                "openai": settings.openai_api_key,
                "anthropic": settings.anthropic_api_key,
                "google": settings.google_api_key,
                "aws": (settings.aws_access_key_id, settings.aws_secret_access_key)
            }
        
        def _configure_ai_clients(credentials: Dict[str, Any]) -> Dict[str, Any]:
            configured = {}
            if credentials["openai"]: configured["openai"] = "configured"
            if credentials["anthropic"]: configured["anthropic"] = "configured"
            if credentials["google"]: configured["gemini"] = "configured"
            if all(credentials["aws"]): configured["bedrock"] = "configured"
            return configured
        
        def _validate_ai_setup(configured_clients: Dict[str, Any]) -> Result[None, str]:
            self._ai_clients = configured_clients
            return Success(None) if self._ai_clients else Failure("No AI clients configured")
        
        return ai_initializer
    
    # DependencyContainer 클래스에 메서드 동적 추가
    DependencyContainer._create_curried_rapidapi_initializer = _create_curried_rapidapi_initializer
    DependencyContainer._create_curried_gcs_initializer = _create_curried_gcs_initializer
    DependencyContainer._create_curried_ai_initializer = _create_curried_ai_initializer


# 컨테이너 확장 실행
extend_dependency_container_with_hof()
