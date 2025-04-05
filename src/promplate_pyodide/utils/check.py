from pyodide.ffi import JsProxy


def is_fake_openai():
    import openai

    return isinstance(openai, JsProxy)


def is_fake_httpx():
    import httpx

    return isinstance(httpx, JsProxy)
