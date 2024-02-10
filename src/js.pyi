from typing import Any, Callable, Iterable

from pyodide.ffi import JsArray, JsProxy

class Object:
    fromEntries: Callable[[Iterable[JsArray[Any]]], JsProxy]
