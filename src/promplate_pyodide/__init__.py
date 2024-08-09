from contextlib import suppress
from functools import wraps
from inspect import isclass, isfunction
from pathlib import Path
from types import FunctionType

from .utils.stack_switching import stack_switching_supported


def patch_promplate():
    import promplate

    class Loader(promplate.template.Loader):
        """making HTTP requests in pyodide runtime"""

        @classmethod
        async def afetch(cls, url: str, **kwargs):
            from pyodide.http import pyfetch

            res = await pyfetch(cls._join_url(url), **kwargs)
            obj = cls(await res.text())
            obj.name = Path(url).stem

            return obj

        from .utils.stack_switching import stack_switching_supported

        if stack_switching_supported():

            @classmethod
            def fetch(cls, url: str, **kwargs):  # type: ignore
                from pyodide.ffi import run_sync  # type: ignore

                return run_sync(cls.afetch(url, **kwargs))

        else:

            @classmethod
            def fetch(cls, url: str, **kwargs):
                from pyodide.http import open_url

                res = open_url(cls._join_url(url))
                obj = cls(res.read())
                obj.name = Path(url).stem

                return obj

    class Node(Loader, promplate.Node):
        """patched for making HTTP requests in pyodide runtime"""

    class Template(Loader, promplate.Template):
        """patched for making HTTP requests in pyodide runtime"""

    promplate.template.Loader = Loader
    promplate.template.Template = promplate.Template = Template
    promplate.node.Node = promplate.Node = Node

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

        if stack_switching_supported():
            from .utils.openai.sync import patch_sync_apis

            patch_sync_apis()

        else:
            from .utils.warn import NotImplementedWarning

            o.TextComplete = o.TextGenerate = o.ChatComplete = o.ChatGenerate = o.SyncTextOpenAI = o.SyncChatOpenAI = o.v1.TextComplete = o.v1.TextGenerate = o.v1.ChatComplete = o.v1.ChatGenerate = o.v1.SyncTextOpenAI = o.v1.SyncChatOpenAI = NotImplementedWarning  # fmt: off


async def patch_openai(fallback_import_url: str = "https://esm.sh/openai"):
    from .utils.openai import ensure_openai, translate_openai

    await ensure_openai(fallback_import_url)

    import openai

    openai.Client = openai.AsyncClient = translate_openai()


def patch_httpx():
    from pyodide.code import run_js
    from pyodide.ffi import register_js_module

    register_js_module("httpx", run_js("({ Client() { return null }, AsyncClient() { return null } })"))


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
