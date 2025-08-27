"""RFS-Framework Use Case Pattern"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, Any
from dataclasses import dataclass
from . import Result

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")
TError = TypeVar("TError")


class UseCase(ABC, Generic[TRequest, TResponse, TError]):
    """Abstract base class for use cases following RFS pattern"""

    @abstractmethod
    async def execute(self, request: TRequest) -> Result[TResponse, TError]:
        """
        Execute the use case with given request.
        Returns Result monad containing either success or failure.
        """
        pass

    async def validate_request(self, request: TRequest) -> Result[TRequest, str]:
        """
        Override to provide custom request validation.
        Default implementation always returns Success.
        """
        from . import Success

        return Success(request)

    async def __call__(self, request: TRequest) -> Result[TResponse, TError]:
        """Allow use case to be called directly"""
        return await self.execute(request)


@dataclass
class Command(Generic[TRequest]):
    """Base class for command objects in CQRS pattern"""

    pass


@dataclass
class Query(Generic[TRequest]):
    """Base class for query objects in CQRS pattern"""

    pass


class CommandHandler(ABC, Generic[TRequest, TResponse]):
    """Handler for command execution"""

    @abstractmethod
    async def handle(self, command: Command[TRequest]) -> Result[TResponse, str]:
        pass


class QueryHandler(ABC, Generic[TRequest, TResponse]):
    """Handler for query execution"""

    @abstractmethod
    async def handle(self, query: Query[TRequest]) -> Result[TResponse, str]:
        pass


class UseCaseDecorator:
    """Decorator for use case classes"""

    def __init__(self, cls: type) -> None:
        self.cls = cls

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        instance = self.cls(*args, **kwargs)
        return instance


def use_case(cls: type) -> UseCaseDecorator:
    """Decorator to mark a class as a use case"""
    return UseCaseDecorator(cls)
