"""
구조화된 로깅 시스템
JSON 형식으로 로그 출력, 컨텍스트 정보 포함
"""

import logging
import json
import sys
from typing import Dict, Any, Optional, Union, Callable, TypeVar, Awaitable, Coroutine

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])
from enum import Enum
from datetime import datetime
from functools import wraps

# Settings import 제거 (순환 의존성 방지)


class LogLevel(str, Enum):
    """로그 레벨"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredFormatter(logging.Formatter):
    """구조화된 로그 포매터 (JSON)"""

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 형식으로 포매팅"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 추가 컨텍스트 정보 포함
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # 예외 정보 포함
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data, ensure_ascii=False)


class ContextualLogger:
    """컨텍스트 정보를 포함한 로거"""

    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(name)
        self.context = context or {}

    def _log_with_context(
        self, level: int, message: str, extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """컨텍스트 정보와 함께 로그 출력"""
        combined_extra = {**self.context}
        if extra_data:
            combined_extra.update(extra_data)

        # extra_data를 LogRecord에 추가
        extra_record = {"extra_data": combined_extra} if combined_extra else {}
        self.logger.log(level, message, extra=extra_record)

    def debug(self, message: str, **kwargs: Any) -> None:
        """디버그 로그"""
        self._log_with_context(logging.DEBUG, message, kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """정보 로그"""
        self._log_with_context(logging.INFO, message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """경고 로그"""
        self._log_with_context(logging.WARNING, message, kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """에러 로그"""
        self._log_with_context(logging.ERROR, message, kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """치명적 에러 로그"""
        self._log_with_context(logging.CRITICAL, message, kwargs)

    def with_context(self, **context: Any) -> "ContextualLogger":
        """새로운 컨텍스트로 로거 생성"""
        combined_context = {**self.context, **context}
        return ContextualLogger(self.logger.name, combined_context)

    def log_operation(self, operation: str, status: str = "started", **metadata: Any) -> None:
        """작업 로그 (시작/완료/실패)"""
        self.info(f"Operation {status}", operation=operation, status=status, **metadata)

    def log_performance(self, operation: str, duration_ms: float, **metadata: Any) -> None:
        """성능 로그"""
        self.info(
            f"Performance: {operation}",
            operation=operation,
            duration_ms=duration_ms,
            **metadata,
        )

    def log_error_with_context(self, error: Exception, operation: str, **context: Any) -> None:
        """에러와 컨텍스트 정보 함께 로깅"""
        self.error(
            f"Error in {operation}: {str(error)}",
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            **context,
        )


def setup_logging(
    level: Union[str, LogLevel] = LogLevel.INFO, enable_json: bool = True
) -> None:
    """로깅 시스템 초기화"""
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(
        getattr(logging, level.value if isinstance(level, LogLevel) else level)
    )

    # 기존 핸들러 제거
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)

    if enable_json:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    root_logger.addHandler(console_handler)

    # 서드파티 라이브러리 로그 레벨 조정
    logging.getLogger("aioredis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> ContextualLogger:
    """컨텍스트 로거 생성"""
    return ContextualLogger(name, context)


# 성능 측정 데코레이터
def log_performance(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """성능 측정 데코레이터"""

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            import time

            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger(func.__module__)

            start_time = time.time()
            logger.log_operation(op_name, "started")

            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.log_performance(op_name, duration, status="success")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.log_performance(op_name, duration, status="error")
                logger.log_error_with_context(e, op_name)
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            import time

            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger(func.__module__)

            start_time = time.time()
            logger.log_operation(op_name, "started")

            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.log_performance(op_name, duration, status="success")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.log_performance(op_name, duration, status="error")
                logger.log_error_with_context(e, op_name)
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator


# 에러 로깅 데코레이터
def log_errors(operation_name: Optional[str] = None) -> Callable[[F], F]:
    """에러 로깅 데코레이터"""

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger(func.__module__)

            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.log_error_with_context(e, op_name)
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            logger = get_logger(func.__module__)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log_error_with_context(e, op_name)
                raise

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    return decorator
