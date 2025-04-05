from contextlib import suppress
from functools import wraps
from inspect import isclass, isfunction
from pathlib import Path
from types import FunctionType

from .utils.check import is_fake_httpx, is_fake_openai
from .utils.stack_switching import stack_switching_supported


def patch_promplate():
    import promplate

    if is_fake_httpx():
        from promplate.prompt.template import Loader

        @classmethod
        @wraps(Loader.afetch)
        async def afetch(cls, url: str, **kwargs):
            from pyodide.http import pyfetch

            res = await pyfetch(cls._join_url(url), **kwargs)
            obj = cls(await res.text())
            obj.name = Path(url).stem

            return obj

        @classmethod
        @wraps(Loader.fetch)
        def fetch(cls, url: str, **kwargs):
            if stack_switching_supported():
                from pyodide.ffi import run_sync  # type: ignore

                return run_sync(cls.afetch(url, **kwargs))

            else:
                from pyodide.http import open_url

                res = open_url(cls._join_url(url))
                obj = cls(res.read())
                obj.name = Path(url).stem

                return obj

        Loader.afetch = afetch  # type: ignore
        Loader.fetch = fetch  # type: ignore

    if not is_fake_openai():
        return

    patch_class(promplate.node.Interruptable)

    from .utils.proxy import to_js

    with suppress(ModuleNotFoundError):
        import promplate.llm.openai as o

        def patched_ensure(text_or_list: list[promplate.Message] | str):
            """This function is patched to return a JS array. So it should not be called from Python."""
            return to_js(promplate.prompt.chat.ensure(text_or_list))

        def patch_function(func: FunctionType):
            from promplate.prompt.template import SafeChainMapContext as ChainMap

            func = FunctionType(func.__code__, ChainMap({"ensure": patched_ensure}, func.__globals__), func.__name__, func.__defaults__, func.__closure__)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*(to_js(i) for i in args), **{i: to_js(j) for i, j in kwargs.items()})

            return wrapper

        for cls in o.v1.__dict__.values():
            if isclass(cls):
                for name, func in [*cls.__dict__.items()]:
                    if isfunction(func) and func.__name__ == "__call__":
                        setattr(cls, name, patch_function(func))

        from .utils.openai.sync import patch_sync_apis

        patch_sync_apis()


async def patch_openai(fallback_import_url: str = "https://esm.sh/openai"):
    from .utils.openai import ensure_openai, translate_openai

    await ensure_openai(fallback_import_url)

    if not is_fake_openai():
        return

    import openai

    openai.Client = openai.AsyncClient = translate_openai()


def patch_httpx():
    import promplate.llm.openai.v1 as o

    o._get_client = o._get_aclient = lambda: None  # type: ignore


async def patch_all():
    await patch_openai()
    patch_httpx()
    patch_promplate()


def patch_params(func: FunctionType):
    from .utils.proxy import to_py

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*(to_py(i) for i in args), **{i: to_py(j) for i, j in kwargs.items()})

    return wrapper


def patch_class(cls: type):
    for name, func in cls.__dict__.items():
        if isfunction(func):
            setattr(cls, name, patch_params(func))
