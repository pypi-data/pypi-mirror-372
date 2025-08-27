"""
에러 추적 및 집계 시스템
에러 패턴 분석 및 통계 제공
"""

import time
from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from dataclasses import dataclass, field

F = TypeVar('F', bound=Callable[..., Any])
from datetime import datetime, timedelta
from collections import defaultdict, deque
from threading import Lock

from src.shared.kernel import Result, Success, Failure


@dataclass
class ErrorEntry:
    """에러 엔트리"""

    timestamp: datetime
    error_type: str
    error_message: str
    operation: str
    module: str
    function: str
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None


class ErrorTracker:
    """에러 추적 시스템"""

    def __init__(self, max_entries: int = 1000, retention_hours: int = 24):
        """
        에러 추적기 초기화

        Args:
            max_entries: 최대 에러 엔트리 수
            retention_hours: 에러 보관 시간 (시간)
        """
        self.max_entries = max_entries
        self.retention_hours = retention_hours
        self.errors: deque[ErrorEntry] = deque(maxlen=max_entries)
        self._lock = Lock()

        # 통계 카운터
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.operation_errors: Dict[str, int] = defaultdict(int)
        self.module_errors: Dict[str, int] = defaultdict(int)

    def track_error(
        self,
        error: Exception,
        operation: str,
        module: str,
        function: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """에러 추적"""
        with self._lock:
            # 에러 엔트리 생성
            entry = ErrorEntry(
                timestamp=datetime.utcnow(),
                error_type=type(error).__name__,
                error_message=str(error),
                operation=operation,
                module=module,
                function=function,
                context=context or {},
                stack_trace=self._get_stack_trace(error),
            )

            # 에러 저장
            self.errors.append(entry)

            # 통계 업데이트
            self.error_counts[entry.error_type] += 1
            self.operation_errors[operation] += 1
            self.module_errors[module] += 1

            # 오래된 통계 정리
            self._cleanup_old_entries()

    def _get_stack_trace(self, error: Exception) -> Optional[str]:
        """스택 트레이스 추출"""
        import traceback

        try:
            return traceback.format_exc()
        except:
            return None

    def _cleanup_old_entries(self) -> None:
        """오래된 엔트리 정리"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)

        # 오래된 엔트리 제거 (앞에서부터) - HOF 패턴 적용
        from itertools import takewhile
        
        # takewhile을 사용하여 제거할 엔트리들 수집
        old_entries = list(takewhile(
            lambda entry: entry.timestamp < cutoff_time,
            list(self.errors)  # deque를 리스트로 변환
        ))
        
        # 제거 대상 엔트리들 수만큼 popleft 수행
        for _ in range(len(old_entries)):
            old_entry = self.errors.popleft()
            
            # 통계에서 차감
            self.error_counts[old_entry.error_type] = max(
                0, self.error_counts[old_entry.error_type] - 1
            )
            self.operation_errors[old_entry.operation] = max(
                0, self.operation_errors[old_entry.operation] - 1
            )
            self.module_errors[old_entry.module] = max(
                0, self.module_errors[old_entry.module] - 1
            )

    def get_error_summary(self, last_hours: Optional[int] = None) -> Dict[str, Any]:
        """에러 요약 정보 조회"""
        with self._lock:
            self._cleanup_old_entries()

            # 시간 필터링
            if last_hours:
                cutoff_time = datetime.utcnow() - timedelta(hours=last_hours)
                filtered_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
            else:
                filtered_errors = list(self.errors)

            if not filtered_errors:
                return {
                    "total_errors": 0,
                    "error_rate": 0.0,
                    "top_error_types": [],
                    "top_operations": [],
                    "top_modules": [],
                    "recent_errors": [],
                }

            # 통계 계산 - HOF 패턴 적용
            from collections import Counter
            
            # map + Counter 사용으로 함수형 스타일 구현
            error_type_counts = Counter(map(lambda e: e.error_type, filtered_errors))
            operation_counts = Counter(map(lambda e: e.operation, filtered_errors))
            module_counts = Counter(map(lambda e: e.module, filtered_errors))

            # 상위 N개 추출
            top_error_types = sorted(
                error_type_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            top_operations = sorted(
                operation_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            top_modules = sorted(
                module_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]

            # 최근 에러 (최대 10개)
            # HOF 패턴: map 사용
            recent_errors = list(map(
                lambda error: {
                    "timestamp": error.timestamp.isoformat(),
                    "error_type": error.error_type,
                    "error_message": error.error_message,
                    "operation": error.operation,
                    "module": error.module,
                    "function": error.function,
                },
                sorted(filtered_errors, key=lambda x: x.timestamp, reverse=True)[:10]
            ))

            # 에러율 계산 (시간당)
            time_span_hours = last_hours or self.retention_hours
            error_rate = len(filtered_errors) / max(1, time_span_hours)

            return {
                "total_errors": len(filtered_errors),
                "error_rate": round(error_rate, 2),
                "top_error_types": [
                    {"type": t, "count": c} for t, c in top_error_types
                ],
                "top_operations": [
                    {"operation": o, "count": c} for o, c in top_operations
                ],
                "top_modules": [{"module": m, "count": c} for m, c in top_modules],
                "recent_errors": recent_errors,
            }

    def get_error_patterns(self) -> List[Dict[str, Any]]:
        """에러 패턴 분석"""
        with self._lock:
            self._cleanup_old_entries()

            # 에러 타입별 패턴 분석
            patterns = []

            for error_type, count in self.error_counts.items():
                if count > 1:  # 2회 이상 발생한 에러만
                    # 해당 에러 타입의 최근 발생 정보
                    type_errors = [e for e in self.errors if e.error_type == error_type]

                    if type_errors:
                        # 가장 최근 에러
                        latest_error = max(type_errors, key=lambda x: x.timestamp)

                        # 주요 발생 작업 - HOF 패턴 사용
                        from collections import Counter
                        operations = Counter(map(lambda e: e.operation, type_errors))

                        top_operation = max(operations.items(), key=lambda x: x[1])

                        patterns.append(
                            {
                                "error_type": error_type,
                                "total_count": count,
                                "latest_occurrence": latest_error.timestamp.isoformat(),
                                "most_frequent_operation": top_operation[0],
                                "operation_count": top_operation[1],
                                "sample_message": latest_error.error_message[:200],
                            }
                        )

            return sorted(patterns, key=lambda x: x["total_count"], reverse=True)

    def get_health_status(self) -> Dict[str, Any]:
        """시스템 건강 상태"""
        with self._lock:
            self._cleanup_old_entries()

            # 최근 1시간 에러
            recent_errors = [
                e
                for e in self.errors
                if e.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ]

            # 건강 점수 계산 (에러가 적을수록 높음)
            health_score = max(0, 100 - len(recent_errors) * 5)  # 에러당 -5점

            # 상태 결정
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "warning"
            else:
                status = "critical"

            return {
                "status": status,
                "health_score": health_score,
                "recent_errors_1h": len(recent_errors),
                "total_tracked_errors": len(self.errors),
                "error_types_count": len(self.error_counts),
                "most_problematic_operation": (
                    max(
                        self.operation_errors.items(),
                        key=lambda x: x[1],
                        default=("none", 0),
                    )[0]
                    if self.operation_errors
                    else "none"
                ),
            }

    def clear_errors(self) -> None:
        """에러 기록 초기화"""
        with self._lock:
            self.errors.clear()
            self.error_counts.clear()
            self.operation_errors.clear()
            self.module_errors.clear()


# 글로벌 에러 추적기 인스턴스
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """글로벌 에러 추적기 획득"""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


def track_error(
    error: Exception,
    operation: str,
    module: str,
    function: str,
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """편의 함수: 에러 추적"""
    tracker = get_error_tracker()
    tracker.track_error(error, operation, module, function, context)


def log_performance(
    operation: Optional[Union[str, Callable[..., Any]]] = None,
    duration_ms: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Any:
    """성능 로깅 편의 함수 또는 데코레이터"""
    import functools
    import time
    from .logger import get_logger

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000  # milliseconds

                op_name = operation or f"{func.__module__}.{func.__name__}"
                logger = get_logger(func.__module__)

                log_data = {
                    "operation": op_name,
                    "duration_ms": duration,
                    "performance": True,
                }
                if context:
                    log_data.update(context)

                if duration > 1000:  # 1초 이상
                    logger.warning(f"Slow operation: {op_name}", extra=log_data)
                else:
                    logger.info(f"Operation completed: {op_name}", extra=log_data)

                return result
            except Exception as e:
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000

                op_name = operation or f"{func.__module__}.{func.__name__}"
                logger = get_logger(func.__module__)
                logger.error(
                    f"Operation failed: {op_name}",
                    extra={
                        "operation": op_name,
                        "duration_ms": duration,
                        "error": str(e),
                    },
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000

                op_name = operation or f"{func.__module__}.{func.__name__}"
                logger = get_logger(func.__module__)

                log_data = {
                    "operation": op_name,
                    "duration_ms": duration,
                    "performance": True,
                }
                if context:
                    log_data.update(context)

                if duration > 1000:
                    logger.warning(f"Slow operation: {op_name}", extra=log_data)
                else:
                    logger.info(f"Operation completed: {op_name}", extra=log_data)

                return result
            except Exception as e:
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000

                op_name = operation or f"{func.__module__}.{func.__name__}"
                logger = get_logger(func.__module__)
                logger.error(
                    f"Operation failed: {op_name}",
                    extra={
                        "operation": op_name,
                        "duration_ms": duration,
                        "error": str(e),
                    },
                )
                raise

        # 함수가 async인지 확인
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    # 데코레이터로 사용되는 경우 (매개변수 없이)
    if callable(operation):
        func = operation
        operation = None
        return decorator(func)

    # 매개변수와 함께 사용되는 경우
    if duration_ms is not None:
        # 일반 함수로 호출된 경우
        logger = get_logger(__name__)
        log_data = {
            "operation": operation,
            "duration_ms": duration_ms,
            "performance": True,
        }
        if context:
            log_data.update(context)

        if duration_ms > 1000:
            logger.warning(f"Slow operation: {operation}", extra=log_data)
        else:
            logger.info(f"Operation completed: {operation}", extra=log_data)
        return None

    # 데코레이터로 사용되는 경우
    return decorator


def log_errors(
    operation: Optional[Union[str, Callable[..., Any]]] = None,
    error: Optional[Exception] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Any:
    """에러 로깅 편의 함수 또는 데코레이터"""
    import functools
    from .logger import get_logger

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                op_name = operation or f"{func.__module__}.{func.__name__}"
                logger = get_logger(func.__module__)

                log_data = {
                    "operation": op_name,
                    "error_type": e.__class__.__name__,
                    "error_message": str(e),
                }
                if context:
                    log_data.update(context)

                logger.error(f"Operation failed: {op_name}", extra=log_data)

                # Error tracker에도 기록
                op_str = op_name if isinstance(op_name, str) else str(op_name)
                track_error(e, op_str, func.__module__, func.__name__, context)
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                op_name = operation or f"{func.__module__}.{func.__name__}"
                logger = get_logger(func.__module__)

                log_data = {
                    "operation": op_name,
                    "error_type": e.__class__.__name__,
                    "error_message": str(e),
                }
                if context:
                    log_data.update(context)

                logger.error(f"Operation failed: {op_name}", extra=log_data)

                # Error tracker에도 기록
                op_str = op_name if isinstance(op_name, str) else str(op_name)
                track_error(e, op_str, func.__module__, func.__name__, context)
                raise

        # 함수가 async인지 확인
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        else:
            return sync_wrapper  # type: ignore

    # 데코레이터로 사용되는 경우 (매개변수 없이)
    if callable(operation):
        func = operation
        operation = None
        return decorator(func)

    # 매개변수와 함께 사용되는 경우
    if error is not None:
        # 일반 함수로 호출된 경우
        logger = get_logger(__name__)

        log_data = {
            "operation": operation,
            "error_type": error.__class__.__name__,
            "error_message": str(error),
        }
        if context:
            log_data.update(context)

        logger.error(f"Operation failed: {operation}", extra=log_data)

        # Error tracker에도 기록
        import inspect

        frame = inspect.currentframe()
        if frame and frame.f_back:
            frame = frame.f_back
            module = frame.f_globals.get("__name__", "unknown")
            function = frame.f_code.co_name
            track_error(error, operation or "unknown", module, function, context)
        return None

    # 데코레이터로 사용되는 경우
    return decorator
