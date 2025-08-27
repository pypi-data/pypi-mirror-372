"""
RFS Framework 서비스 레지스트리 구현
15-configuration-injection 문서 패턴 적용
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Type, TypeVar, Callable, Union
from enum import Enum

from src.shared.kernel import Result, Success, Failure

T = TypeVar("T")


class ServiceScope(Enum):
    """서비스 스코프 정의"""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceDescriptor:
    """서비스 기술자"""

    service_type: Type
    factory: Callable[..., Any]
    scope: ServiceScope
    dependencies: Optional[list[str]] = None
    config_key: Optional[str] = None
    initialized: bool = False
    instance: Optional[Any] = None


class ServiceRegistry:
    """
    RFS Framework 서비스 레지스트리
    Constructor Injection과 Registry-based 패턴 결합
    """

    def __init__(self) -> None:
        self._services: Dict[str, ServiceDescriptor] = {}
        self._instances: Dict[str, Any] = {}
        self._configuration: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        service_type: Type[T],
        factory: Callable[..., T],
        scope: ServiceScope = ServiceScope.SINGLETON,
        dependencies: Optional[list[str]] = None,
        config_key: Optional[str] = None,
    ) -> "ServiceRegistry":
        """서비스 등록"""
        self._services[name] = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            scope=scope,
            dependencies=dependencies or [],
            config_key=config_key,
        )
        return self

    def register_singleton(
        self,
        name: str,
        service_type: Type[T],
        factory: Callable[..., T],
        dependencies: Optional[list[str]] = None,
        config_key: Optional[str] = None,
    ) -> "ServiceRegistry":
        """싱글톤 서비스 등록 편의 메소드"""
        return self.register(
            name,
            service_type,
            factory,
            ServiceScope.SINGLETON,
            dependencies,
            config_key,
        )

    def register_transient(
        self,
        name: str,
        service_type: Type[T],
        factory: Callable[..., T],
        dependencies: Optional[list[str]] = None,
        config_key: Optional[str] = None,
    ) -> "ServiceRegistry":
        """임시 서비스 등록 편의 메소드"""
        return self.register(
            name,
            service_type,
            factory,
            ServiceScope.TRANSIENT,
            dependencies,
            config_key,
        )

    def configure(self, configuration: Dict[str, Any]) -> "ServiceRegistry":
        """설정 등록"""
        self._configuration.update(configuration)
        return self

    def get_config(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        keys = key.split(".")
        value = self._configuration

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def resolve(self, name: str) -> Result[Any, str]:
        """서비스 해결 (의존성 주입 포함)"""
        if name not in self._services:
            return Failure(f"Service '{name}' not registered")

        descriptor = self._services[name]

        # 싱글톤 인스턴스가 이미 존재하는 경우
        if (
            descriptor.scope == ServiceScope.SINGLETON
            and descriptor.instance is not None
        ):
            return Success(descriptor.instance)

        try:
            # 의존성 해결
            resolved_dependencies = {}
            for dep_name in (descriptor.dependencies or []):
                dep_result = self.resolve(dep_name)
                if dep_result.is_failure():
                    return Failure(
                        f"Failed to resolve dependency '{dep_name}': {dep_result.get_error()}"
                    )
                resolved_dependencies[dep_name] = dep_result.get_or_none()

            # 설정 주입
            config = {}
            if descriptor.config_key:
                config = self.get_config(descriptor.config_key, {})

            # 인스턴스 생성
            if descriptor.dependencies:
                # 의존성이 있는 경우
                instance = descriptor.factory(**resolved_dependencies, config=config)
            elif descriptor.config_key:
                # 설정만 있는 경우
                instance = descriptor.factory(config)
            else:
                # 의존성과 설정이 모두 없는 경우
                instance = descriptor.factory()

            # 싱글톤인 경우 인스턴스 저장
            if descriptor.scope == ServiceScope.SINGLETON:
                descriptor.instance = instance

            return Success(instance)

        except Exception as e:
            return Failure(f"Failed to create service '{name}': {str(e)}")

    def get(self, name: str) -> Optional[Any]:
        """서비스 조회 (None 반환 가능)"""
        result = self.resolve(name)
        return result.get_or_none() if result.is_success() else None

    def get_required(self, name: str) -> Any:
        """필수 서비스 조회 (예외 발생 가능)"""
        result = self.resolve(name)
        if result.is_failure():
            raise ValueError(result.get_error())
        return result.get_or_none()

    def is_registered(self, name: str) -> bool:
        """서비스 등록 여부 확인"""
        return name in self._services

    def clear(self) -> None:
        """레지스트리 초기화"""
        self._services.clear()
        self._instances.clear()
        self._configuration.clear()


# 전역 기본 레지스트리
default_registry = ServiceRegistry()


def get_service_registry() -> ServiceRegistry:
    """기본 서비스 레지스트리 반환"""
    return default_registry


def register_service(
    name: str,
    service_type: Type[T],
    factory: Callable[..., T],
    scope: ServiceScope = ServiceScope.SINGLETON,
    dependencies: Optional[list[str]] = None,
    config_key: Optional[str] = None,
) -> ServiceRegistry:
    """기본 레지스트리에 서비스 등록"""
    return default_registry.register(
        name, service_type, factory, scope, dependencies, config_key
    )


def get_service(name: str) -> Optional[Any]:
    """기본 레지스트리에서 서비스 조회"""
    return default_registry.get(name)


def get_required_service(name: str) -> Any:
    """기본 레지스트리에서 필수 서비스 조회"""
    return default_registry.get_required(name)
