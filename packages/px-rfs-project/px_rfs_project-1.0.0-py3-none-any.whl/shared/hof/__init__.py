"""
RFS Framework 고차 함수(HOF) 구현
함수형 프로그래밍 패턴과 리액티브 스트림 처리를 위한 고차 함수 제공
"""

from typing import TypeVar, Callable, Iterable, List, Optional, Tuple, Union, Any
from ..kernel import Result, Success, Failure

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


# 컬렉션 처리 함수들
def compact_map(func: Callable[[T], Optional[U]], items: Iterable[T]) -> List[U]:
    """
    리스트의 각 항목에 함수를 적용하고 None이 아닌 결과만 반환
    None 값을 자동으로 필터링하는 map + filter 조합 - HOF 패턴 적용
    """
    return [mapped for item in items if (mapped := func(item)) is not None]


def safe_map(func: Callable[[T], U], items: Iterable[T]) -> List[Result[U, str]]:
    """
    안전한 매핑 함수 - 각 항목에 대해 Result를 반환 - HOF 패턴 적용
    예외가 발생하면 Failure로 감싸서 반환
    """
    def safe_apply(item: T) -> Result[U, str]:
        try:
            return Success(func(item))
        except Exception as e:
            return Failure(str(e))
    
    return list(map(safe_apply, items))


def partition(
    predicate: Callable[[T], bool], items: Iterable[T]
) -> Tuple[List[T], List[T]]:
    """
    조건에 따라 리스트를 두 개의 리스트로 분할 - HOF 패턴 적용
    첫 번째 리스트: 조건을 만족하는 항목들
    두 번째 리스트: 조건을 만족하지 않는 항목들
    """
    items_list = list(items)
    truthy = list(filter(predicate, items_list))
    falsy = list(filter(lambda x: not predicate(x), items_list))
    return truthy, falsy


def chain(functions: List[Callable]) -> Callable:
    """
    함수들의 체인을 생성 (좌측에서 우측으로 실행)
    pipe의 별칭 함수
    """

    def chained_function(initial_value: T) -> T:
        # HOF 패턴: reduce 사용
        from functools import reduce
        return reduce(lambda acc, func: func(acc), functions, initial_value)

    return chained_function


def pipe(*functions: Callable) -> Callable:
    """
    함수들의 파이프라인을 생성 (좌측에서 우측으로 실행)
    pipe(f, g, h)(x) = h(g(f(x)))
    """

    def piped_function(initial_value: T) -> T:
        # HOF 패턴: reduce 사용
        from functools import reduce
        return reduce(lambda acc, func: func(acc), functions, initial_value)

    return piped_function


def compose(*functions: Callable) -> Callable:
    """
    함수들의 합성을 생성 (우측에서 좌측으로 실행)
    compose(f, g, h)(x) = f(g(h(x)))
    """

    def composed_function(initial_value: T) -> T:
        # HOF 패턴: reduce + reversed 사용
        from functools import reduce
        return reduce(lambda acc, func: func(acc), reversed(functions), initial_value)

    return composed_function


def safe_pipe(*functions: Callable) -> Callable[[T], Result[U, str]]:
    """
    안전한 파이프라인 - 각 단계에서 예외가 발생하면 Failure 반환
    Result 타입과 함께 사용하기 적합
    """

    def safe_piped_function(initial_value: T) -> Result[U, str]:
        try:
            # HOF 패턴: reduce 사용
            from functools import reduce
            result = reduce(lambda acc, func: func(acc), functions, initial_value)
            return Success(result)  # type: ignore
        except Exception as e:
            return Failure(str(e))

    return safe_piped_function


def result_chain(
    *functions: Callable[[T], Result[U, str]]
) -> Callable[[T], Result[U, str]]:
    """
    Result를 반환하는 함수들의 체인
    한 단계에서라도 Failure가 발생하면 즉시 Failure 반환 (모나드 체이닝)
    """

    def result_chained_function(initial_value: T) -> Result[U, str]:
        # HOF 패턴: 순차적 모나드 체이닝
        from functools import reduce
        
        def bind_chain(acc_result: Result[Any, str], func: Callable[[Any], Result[Any, str]]) -> Result[Any, str]:
            return acc_result.bind(func) if acc_result.is_success() else acc_result
        
        return reduce(bind_chain, functions, Success(initial_value))  # type: ignore

    return result_chained_function


def tap(func: Callable[[T], None]) -> Callable[[T], T]:
    """
    사이드 이펙트를 수행하지만 원본 값을 그대로 반환
    디버깅이나 로깅에 유용
    """

    def tap_function(value: T) -> T:
        func(value)
        return value

    return tap_function


def when(condition: Callable[[T], bool], func: Callable[[T], T]) -> Callable[[T], T]:
    """
    조건부 함수 적용
    조건이 참일 때만 함수를 적용, 그렇지 않으면 원본 값 반환
    """

    def conditional_function(value: T) -> T:
        if condition(value):
            return func(value)
        return value

    return conditional_function


def unless(condition: Callable[[T], bool], func: Callable[[T], T]) -> Callable[[T], T]:
    """
    조건이 거짓일 때만 함수를 적용
    when의 반대 함수
    """

    def conditional_function(value: T) -> T:
        if not condition(value):
            return func(value)
        return value

    return conditional_function


def memoize(func: Callable) -> Callable:
    """
    함수의 결과를 메모이제이션하여 성능 향상
    동일한 인자에 대해서는 캐시된 결과를 반환
    """
    cache = {}

    def memoized_function(*args: Any, **kwargs: Any) -> Any:
        # 키 생성 (args와 kwargs 조합)
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return memoized_function


def curry(func: Callable) -> Callable:
    """
    함수를 커리화 - 부분 적용을 지원하는 함수로 변환
    """
    import functools
    import inspect
    
    sig = inspect.signature(func)
    arity = len(sig.parameters)
    
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= arity:
            return func(*args, **kwargs)
        return functools.partial(curried, *args, **kwargs)
    
    return curried


__all__ = [
    "compact_map",
    "safe_map",
    "partition",
    "chain",
    "pipe",
    "compose",
    "safe_pipe",
    "result_chain",
    "tap",
    "when",
    "unless",
    "memoize",
    "curry",
]
