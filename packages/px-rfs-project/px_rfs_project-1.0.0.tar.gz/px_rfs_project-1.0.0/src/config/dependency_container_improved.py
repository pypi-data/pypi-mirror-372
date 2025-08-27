"""
개선된 의존성 주입 컨테이너
RFS Framework 15-configuration-injection 패턴 적용
"""

from typing import Optional, Dict, Any, Callable, TypeVar
from functools import lru_cache, partial
from src.shared.hof import curry, pipe

from src.shared.kernel import Result, Success, Failure

# 커링 패턴을 위한 타입 변수
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
from src.config.settings import Settings, get_settings
from src.config.service_registry import (
    ServiceRegistry,
    ServiceScope,
    get_service_registry,
)
from src.config.configuration_profiles import (
    ConfigurationProfileFactory,
    ProfileConfiguration,
)


class ImprovedDependencyContainer:
    """
    개선된 의존성 주입 컨테이너
    RFS Framework HOF/커링 패턴 적용 - 규칙 3 준수
    """

    def __init__(self, settings: Settings, registry: Optional[ServiceRegistry] = None):
        self.settings = settings
        self.registry = registry or get_service_registry()
        self.profile: Optional[ProfileConfiguration] = None
        self._initialized = False
        
        # 커링된 팩토리 함수들 저장 (HOF 패턴)
        self._curried_factories: Dict[str, Callable] = {}
        self._service_configurators: Dict[str, Callable] = {}

    async def initialize(self) -> Result[None, str]:
        """의존성 컨테이너 초기화"""
        if self._initialized:
            return Success(None)

        try:
            # 1. 설정 프로필 생성
            profile_result = ConfigurationProfileFactory.create_from_settings(
                self.settings
            )
            if profile_result.is_failure():
                return Failure(profile_result.get_error() or "Profile creation failed")

            self.profile = profile_result.get_or_none()
            if self.profile is None:
                return Failure("Profile configuration is None")

            # 2. 레지스트리에 설정 등록
            self.registry.configure(self.profile.to_dict())

            # 3. 핵심 서비스 등록
            await self._register_core_services()

            # 4. 인프라 서비스 등록
            await self._register_infrastructure_services()

            # 5. 도메인 서비스 등록
            await self._register_domain_services()

            # 6. 애플리케이션 서비스 등록
            await self._register_application_services()

            self._initialized = True
            return Success(None)

        except Exception as e:
            return Failure(f"컨테이너 초기화 실패: {str(e)}")

    async def _register_core_services(self):
        """핵심 서비스 등록 - 커링 패턴 적용 (규칙 3)"""
        # 커링된 설정 팩토리 생성
        settings_factory = self._create_curried_settings_factory()
        profile_factory = self._create_curried_profile_factory()
        
        # Settings 서비스 (HOF 패턴)
        self.registry.register_singleton("settings", Settings, settings_factory)

        # Configuration Profile 서비스 (HOF 패턴)
        self.registry.register_singleton(
            "config_profile", ProfileConfiguration, profile_factory
        )

    async def _register_infrastructure_services(self):
        """인프라스트럭처 서비스 등록 - 커링 패턴 적용 (규칙 3)"""
        # 인프라 서비스 등록 파이프라인 (RFS 파이프라인 패턴)
        infrastructure_pipeline = pipe(
            self._prepare_service_configs,     # 설정 준비
            self._create_infrastructure_factories,  # 팩토리 생성
            self._register_infrastructure_services_with_factories  # 서비스 등록
        )
        
        infrastructure_pipeline(self.profile)

    async def _register_domain_services(self):
        """도메인 서비스 등록 - 커링 패턴 적용 (규칙 3)"""
        # 도메인 서비스 팩토리들을 커링 패턴으로 생성
        chunking_factory_curried = self._create_curried_chunking_factory()
        extractor_factory_curried = self._create_curried_extractor_factory()
        
        # 텍스트 청킹 팩토리 (HOF 패턴)
        self.registry.register_singleton(
            "chunking_factory",
            object,  # ChunkingStrategyFactory 타입
            chunking_factory_curried,
            dependencies=["spacy_processor"],
        )

        # 파일 추출기 팩토리 (HOF 패턴)
        self.registry.register_singleton(
            "extractor_factory",
            object,  # ExtractorFactory 타입
            extractor_factory_curried,
        )

    async def _register_application_services(self):
        """애플리케이션 서비스 등록 - 커링 패턴 적용 (규칙 3)"""
        # 애플리케이션 서비스 팩토리를 커링 패턴으로 생성
        text_extraction_factory_curried = self._create_curried_text_extraction_service()
        
        # 텍스트 추출 서비스 (HOF 패턴)
        self.registry.register_singleton(
            "text_extraction_service",
            object,  # TextExtractionService 타입
            text_extraction_factory_curried,
            dependencies=[
                "redis_client",
                "rapidapi_client",
                "chunking_factory",
                "extractor_factory",
            ],
        )

    def _create_curried_settings_factory(self) -> Callable[[], Settings]:
        """Settings 팩토리 커링 - 20줄 이하 (규칙 1)"""
        @curry
        def create_settings() -> Settings:
            return self.settings
        return create_settings
    
    def _create_curried_profile_factory(self) -> Callable[[], Optional[ProfileConfiguration]]:
        """Profile 팩토리 커링 - 20줄 이하 (규칙 1)"""
        @curry
        def create_profile() -> Optional[ProfileConfiguration]:
            return self.profile
        return create_profile
    
    def _prepare_service_configs(self, profile: ProfileConfiguration) -> Dict[str, Dict[str, Any]]:
        """서비스 설정 준비 - 20줄 이하 (규칙 1)"""
        return {
            "redis": {"enabled": profile.redis.enabled, "profile": profile.redis},
            "rapidapi": {"enabled": profile.rapidapi.enabled, "profile": profile.rapidapi},
            "spacy": {"enabled": profile.spacy.enabled, "profile": profile.spacy},
        }
    
    def _create_infrastructure_factories(self, configs: Dict[str, Dict[str, Any]]) -> Dict[str, Callable]:
        """인프라 팩토리 생성 - HOF 패턴 (규칙 3)"""
        return {
            "redis_factory": self._create_curried_redis_factory(configs["redis"]),
            "rapidapi_factory": self._create_curried_rapidapi_factory(configs["rapidapi"]),
            "spacy_factory": self._create_curried_spacy_factory(configs["spacy"]),
        }
    
    def _register_infrastructure_services_with_factories(self, factories: Dict[str, Callable]) -> None:
        """팩토리로 인프라 서비스 등록 - 20줄 이하 (규칙 1)"""
        service_mappings = [
            ("redis_client", "redis_factory"),
            ("rapidapi_client", "rapidapi_factory"),
            ("spacy_processor", "spacy_factory")
        ]
        
        for service_name, factory_key in service_mappings:
            if factory_key in factories:
                self.registry.register_singleton(
                    service_name, object, factories[factory_key], config_key=service_name.split("_")[0]
                )
    
    def _create_curried_redis_factory(self, config_info: Dict[str, Any]) -> Callable:
        """Redis 클라이언트 커링 팩토리 - 20줄 이하 (규칙 1)"""
        @curry
        def redis_factory(config: Dict[str, Any]):
            from src.infrastructure.cache.redis_client import RedisClient
            from src.infrastructure.cache.redis_config import RedisConfigFactory

            if not config_info.get("enabled", False):
                return RedisClient(None)

            config_result = RedisConfigFactory.create_from_settings(self.settings)
            if config_result.is_failure():
                raise ValueError(config_result.get_error() or "Redis config failed")

            return RedisClient(config_result.get_or_none())
        return redis_factory

    def _create_curried_rapidapi_factory(self, config_info: Dict[str, Any]) -> Callable:
        """RapidAPI 클라이언트 커링 팩토리 - 20줄 이하 (규칙 1)"""
        @curry
        def rapidapi_factory(config: Dict[str, Any]):
            from src.infrastructure.external.rapidapi_client import RapidAPIClient
            from src.infrastructure.external.rapidapi_config import RapidAPIConfigFactory

            if not config_info.get("enabled", False):
                return None

            config_result = RapidAPIConfigFactory.create_from_settings(self.settings)
            if config_result.is_failure():
                raise ValueError(config_result.get_error() or "RapidAPI config failed")

            rapidapi_config = config_result.get_or_none()
            if rapidapi_config is None:
                raise ValueError("RapidAPI config creation returned None")
        
            return RapidAPIClient(rapidapi_config)
        return rapidapi_factory

    def _create_curried_spacy_factory(self, config_info: Dict[str, Any]) -> Callable:
        """SpaCy 프로세서 커링 팩토리 - 20줄 이하 (규칙 1)"""
        @curry
        def spacy_factory(config: Dict[str, Any]):
            from src.infrastructure.nlp.spacy_processor import SpaCyProcessor

            if not config_info.get("enabled", False):
                return None

            return SpaCyProcessor(self.settings)
        return spacy_factory

    def _create_curried_chunking_factory(self) -> Callable:
        """청킹 팩토리 커링 생성 - 20줄 이하 (규칙 1)"""
        @curry
        def chunking_factory(spacy_processor):
            from src.domain.text.chunking_factory import ChunkingStrategyFactory

            return ChunkingStrategyFactory(spacy_processor)
        return chunking_factory

    def _create_curried_extractor_factory(self) -> Callable:
        """추출기 팩토리 커링 생성 - 20줄 이하 (규칙 1)"""
        @curry
        def extractor_factory():
            from src.infrastructure.extractors.extractor_factory import ExtractorFactory

            return ExtractorFactory()
        return extractor_factory

    def _create_curried_text_extraction_service(self) -> Callable:
        """텍스트 추출 서비스 커링 생성 - 20줄 이하 (규칙 1)"""
        @curry
        def text_extraction_factory(
            redis_client, rapidapi_client, chunking_factory, extractor_factory
        ):
            from src.application.services.text_extraction_service import (
                TextExtractionService,
            )

            return TextExtractionService(
                redis_client=redis_client,
                rapidapi_client=rapidapi_client,
                chunking_factory=chunking_factory,
                extractor_factory=extractor_factory,
            )
        return text_extraction_factory

    def get_service(self, name: str) -> Optional[Any]:
        """서비스 조회"""
        return self.registry.get(name)

    def get_required_service(self, name: str) -> Any:
        """필수 서비스 조회"""
        return self.registry.get_required(name)

    async def cleanup(self) -> Result[None, str]:
        """리소스 정리"""
        try:
            # Redis 클라이언트 정리
            redis_client = self.get_service("redis_client")
            if redis_client and hasattr(redis_client, "disconnect"):
                await redis_client.disconnect()

            # 기타 리소스 정리
            self.registry.clear()
            self._initialized = False

            return Success(None)
        except Exception as e:
            return Failure(f"리소스 정리 실패: {str(e)}")


# 싱글톤 컨테이너 관리
_improved_container: Optional[ImprovedDependencyContainer] = None


@lru_cache()
def get_improved_container() -> ImprovedDependencyContainer:
    """개선된 의존성 컨테이너 싱글톤 반환"""
    global _improved_container
    if _improved_container is None:
        settings = get_settings()
        _improved_container = ImprovedDependencyContainer(settings)
    return _improved_container


async def initialize_improved_dependencies() -> Result[None, str]:
    """개선된 의존성 초기화"""
    container = get_improved_container()
    return await container.initialize()


async def cleanup_improved_dependencies() -> Result[None, str]:
    """개선된 의존성 리소스 정리"""
    container = get_improved_container()
    return await container.cleanup()


# 편의 함수들
def get_service(name: str) -> Optional[Any]:
    """서비스 조회 편의 함수"""
    container = get_improved_container()
    return container.get_service(name)


def get_required_service(name: str) -> Any:
    """필수 서비스 조회 편의 함수"""
    container = get_improved_container()
    return container.get_required_service(name)


# 특정 서비스 조회 편의 함수들
def get_redis_client():
    """Redis 클라이언트 조회"""
    return get_service("redis_client")


def get_rapidapi_client():
    """RapidAPI 클라이언트 조회"""
    return get_service("rapidapi_client")


def get_spacy_processor():
    """SpaCy 프로세서 조회"""
    return get_service("spacy_processor")


def get_text_extraction_service():
    """텍스트 추출 서비스 조회"""
    return get_service("text_extraction_service")


def get_chunking_factory():
    """청킹 팩토리 조회"""
    return get_service("chunking_factory")


def get_extractor_factory():
    """추출기 팩토리 조회"""
    return get_service("extractor_factory")
