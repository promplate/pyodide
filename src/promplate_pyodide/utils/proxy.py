def to_js(obj):
    from js import Object  # type: ignore
    from pyodide.ffi import to_js

    return to_js(obj, dict_converter=Object.fromEntries)
