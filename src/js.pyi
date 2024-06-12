from typing import Any, Awaitable, Callable, Iterable

from pyodide.ffi import JsArray, JsProxy

class Object:
    fromEntries: Callable[[Iterable[JsArray[Any]]], JsProxy]

class Promise:
    resolve: Callable[..., Awaitable[JsProxy]]
