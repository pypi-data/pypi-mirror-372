import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar, cast, overload

R = TypeVar("R")


def wrap_with_callbacks_sync(
    fn: Callable[..., R],
    *,
    before: Optional[Callable[..., None]] = None,
    on_success: Optional[Callable[[R], None]] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
    suppress_exceptions: bool = False,
) -> Callable[..., R]:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        if before:
            before()
        try:
            result = fn(*args, **kwargs)
            if on_success:
                on_success(result)
            return result
        except Exception as e:
            if on_failure:
                on_failure(e)
            if suppress_exceptions:
                return None  # type: ignore
            raise

    return wrapper


def wrap_with_callbacks_async(
    fn: Callable[..., Awaitable[R]],
    *,
    before: Optional[Callable[..., None]] = None,
    on_success: Optional[Callable[[R], None]] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
    suppress_exceptions: bool = False,
) -> Callable[..., Awaitable[R]]:
    @wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        if before:
            before()
        try:
            result = await fn(*args, **kwargs)
            if on_success:
                on_success(result)
            return result
        except Exception as e:
            if on_failure:
                on_failure(e)
            if suppress_exceptions:
                return None  # type: ignore
            raise

    return wrapper


@overload
def wrap_with_callbacks(
    fn: Callable[..., Awaitable[R]],
    *,
    before: Optional[Callable[[], None]] = ...,
    on_success: Optional[Callable[[R], None]] = ...,
    on_failure: Optional[Callable[[Exception], None]] = ...,
    suppress_exceptions: bool = ...,
) -> Callable[..., Awaitable[R]]: ...


@overload
def wrap_with_callbacks(
    *,
    before: Optional[Callable[..., None]] = ...,
    on_success: Optional[Callable[[Any], None]] = ...,
    on_failure: Optional[Callable[[Exception], None]] = ...,
    suppress_exceptions: bool = ...,
) -> Callable[[Callable[..., R]], Callable[..., R]]: ...


@overload
def wrap_with_callbacks(
    fn: Callable[..., R],
    *,
    before: Optional[Callable[[], None]] = ...,
    on_success: Optional[Callable[[R], None]] = ...,
    on_failure: Optional[Callable[[Exception], None]] = ...,
    suppress_exceptions: bool = ...,
) -> Callable[..., R]: ...


def wrap_with_callbacks(
    fn: Optional[Callable[..., Any]] = None,
    *,
    before: Optional[Callable[[], None]] = None,
    on_success: Optional[Callable[[Any], None]] = None,
    on_failure: Optional[Callable[[Exception], None]] = None,
    suppress_exceptions: bool = False,
) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        if asyncio.iscoroutinefunction(func):
            return wrap_with_callbacks_async(
                cast(Callable[..., Awaitable[Any]], func),
                before=before,
                on_success=on_success,
                on_failure=on_failure,
                suppress_exceptions=suppress_exceptions,
            )
        else:
            return wrap_with_callbacks_sync(
                cast(Callable[..., Any], func),
                before=before,
                on_success=on_success,
                on_failure=on_failure,
                suppress_exceptions=suppress_exceptions,
            )

    if fn is None:
        return decorator
    else:
        return decorator(fn)
