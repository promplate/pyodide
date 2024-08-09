from inspect import isawaitable
from typing import AsyncIterable, Awaitable, Callable, Iterable, overload

STOP_ITERATION = object()


def syncify[T](iterable: AsyncIterable[T]) -> Iterable[T]:
    from pyodide.ffi import run_sync

    it = aiter(iterable)
    while True:
        res = run_sync(anext(it, STOP_ITERATION))
        if res is STOP_ITERATION:
            break
        else:
            yield res  # type: ignore


@overload
def to_sync[**P, T](func: Callable[P, AsyncIterable[T]]) -> Callable[P, Iterable[T]]: ...
@overload
def to_sync[**P, T](func: Callable[P, Awaitable[T]]) -> Callable[P, T]: ...


def to_sync(func):  # type: ignore
    from functools import wraps

    from pyodide.ffi import run_sync

    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return run_sync(res) if isawaitable(res) else syncify(res)

    return wrapper
