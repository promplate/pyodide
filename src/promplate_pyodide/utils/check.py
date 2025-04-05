from pyodide.ffi import JsProxy


def is_fake_openai():
    import openai

    return isinstance(openai, JsProxy)


def is_fake_httpx():
    try:
        import httpx
    except ModuleNotFoundError:
        return True
    else:
        return isinstance(httpx, JsProxy)
