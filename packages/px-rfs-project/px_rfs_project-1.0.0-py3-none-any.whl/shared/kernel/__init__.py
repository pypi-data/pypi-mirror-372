"""
공유 커널 모듈 - RFS Framework 패턴 구현
"""

from typing import TypeVar, Generic, Optional, Callable, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class Result(Generic[T, E], ABC):
    """Result 모나드 - 예외 없는 에러 처리"""

    @abstractmethod
    def is_success(self) -> bool:
        """성공 여부 확인"""
        pass

    @abstractmethod
    def is_failure(self) -> bool:
        """실패 여부 확인"""
        pass

    @abstractmethod
    def get_or_none(self) -> Optional[T]:
        """값을 가져오거나 None 반환"""
        pass

    @abstractmethod
    def get_error(self) -> Optional[E]:
        """에러를 가져오거나 None 반환"""
        pass

    @abstractmethod
    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """값 변환"""
        pass

    @abstractmethod
    def flat_map(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """모나드 체이닝"""
        pass

    @abstractmethod
    def bind(self, func: Callable[[T], "Result[U, E]"]) -> "Result[U, E]":
        """flat_map 별칭"""
        pass

    @abstractmethod
    def or_else(self, default: T) -> T:
        """기본값 반환"""
        pass


@dataclass
class Success(Result[T, E]):
    """성공 결과"""

    value: T

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False

    def get_or_none(self) -> Optional[T]:
        return self.value

    def get_error(self) -> Optional[E]:
        return None

    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        try:
            return Success(func(self.value))
        except Exception as e:
            return Failure(e)  # type: ignore

    def flat_map(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        try:
            return func(self.value)
        except Exception as e:
            return Failure(e)  # type: ignore

    def bind(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """flat_map의 별칭"""
        return self.flat_map(func)

    def or_else(self, default: T) -> T:
        return self.value


@dataclass
class Failure(Result[T, E]):
    """실패 결과"""

    error: E

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True

    def get_or_none(self) -> Optional[T]:
        return None

    def get_error(self) -> Optional[E]:
        return self.error

    def map(self, func: Callable[[T], U]) -> Result[U, E]:
        return Failure(self.error)

    def flat_map(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return Failure(self.error)

    def bind(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
        """flat_map의 별칭"""
        return self.flat_map(func)

    def or_else(self, default: T) -> T:
        return default


class Mono(Generic[T]):
    """리액티브 Mono - 단일 값 비동기 처리"""

    def __init__(self, value_provider: Callable[[], T]):
        self._value_provider = value_provider

    @classmethod
    def just(cls, value: T) -> "Mono[T]":
        """값으로 Mono 생성"""
        return cls(lambda: value)

    @classmethod
    def from_result(cls, result: Result[T, Any]) -> "Mono[T]":
        """Result에서 Mono 생성"""

        def provider() -> T:
            if result.is_success():
                value = result.get_or_none()
                if value is not None:
                    return value
                raise ValueError("Success result has None value")
            raise ValueError(f"Result 실패: {result.get_error()}")

        return cls(provider)

    @classmethod
    def from_callable(cls, callable_func: Callable[[], T]) -> "Mono[T]":
        """callable 함수에서 Mono 생성"""
        return cls(callable_func)

    @classmethod
    def error(cls, error: Exception) -> "Mono[T]":
        """에러로 Mono 생성"""
        def provider() -> T:
            raise error
        return cls(provider)

    async def to_result(self) -> Result[T, str]:
        """Result로 변환 - 이벤트 루프 호환성 개선"""
        import asyncio
        import inspect
        
        try:
            value = self._value_provider()
            
            # 코루틴인 경우 적절히 처리
            if inspect.iscoroutine(value):
                try:
                    # 현재 이벤트 루프가 실행 중인지 확인
                    loop = asyncio.get_running_loop()
                    # 이미 실행 중인 루프에서는 await 사용
                    value = await value
                except RuntimeError:
                    # 실행 중인 루프가 없으면 새로 생성
                    import typing
                    if typing.TYPE_CHECKING:
                        # 타입 체킹 시에는 Any로 처리
                        value = asyncio.run(typing.cast(typing.Any, value))
                    else:
                        value = asyncio.run(value)
            
            return Success(value)
        except Exception as e:
            return Failure(str(e))

    def map(self, func: Callable[[T], U]) -> "Mono[U]":
        """값 변환"""

        def new_provider() -> U:
            return func(self._value_provider())

        return Mono(new_provider)

    def flat_map(self, func: Callable[[T], "Mono[U]"]) -> "Mono[U]":
        """모나드 체이닝"""

        def new_provider() -> U:
            inner_mono = func(self._value_provider())
            return inner_mono._value_provider()

        return Mono(new_provider)


class Flux(Generic[T]):
    """리액티브 Flux - 다중 값 스트림 처리"""

    def __init__(self, items_provider: Callable[[], list[T]]):
        self._items_provider = items_provider

    @classmethod
    def from_iterable(cls, items: list[T]) -> "Flux[T]":
        """리스트에서 Flux 생성"""
        return cls(lambda: items)

    def map(self, func: Callable[[T], U]) -> "Flux[U]":
        """각 항목에 함수 적용"""

        def new_provider() -> list[U]:
            return [func(item) for item in self._items_provider()]

        return Flux(new_provider)

    def filter(self, predicate: Callable[[T], bool]) -> "Flux[T]":
        """조건에 맞는 항목만 필터링"""

        def new_provider() -> list[T]:
            return [item for item in self._items_provider() if predicate(item)]

        return Flux(new_provider)

    async def collect_list(self) -> list[T]:
        """리스트로 수집"""
        return self._items_provider()


__all__ = ["Result", "Success", "Failure", "Mono", "Flux"]
