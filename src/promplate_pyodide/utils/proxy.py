from pyodide.ffi import JsProxy


def to_js(obj):
    from js import Object  # type: ignore
    from pyodide.ffi import to_js

    return to_js(obj, dict_converter=Object.fromEntries)


def to_py(obj: JsProxy):
    return obj.to_py() if isinstance(obj, JsProxy) else obj
