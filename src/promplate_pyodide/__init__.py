from contextlib import suppress
from inspect import isclass, isfunction
from pathlib import Path
from types import FunctionType

from .utils.warn import NotImplementedWarning


def patch_promplate():
    import promplate

    class Loader(promplate.template.Loader):
        """making HTTP requests in pyodide runtime"""

        @classmethod
        async def afetch(cls, url: str, **kwargs):
            from pyodide.http import pyfetch

            res = await pyfetch(cls._join_url(url))
            obj = cls(await res.text())
            obj.name = Path(url).stem

            return obj

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

    from promplate.prompt.chat import ensure

    from .utils.proxy import to_js

    def patched_ensure(text_or_list: list[promplate.Message] | str):
        """This function is patched to return a JS array. So it should not be called from Python."""
        return to_js(ensure(text_or_list))

    with suppress(ModuleNotFoundError):
        import promplate.llm.openai as o

        o.TextComplete = o.TextGenerate = o.ChatComplete = o.ChatGenerate = o.SyncTextOpenAI = o.SyncChatOpenAI = o.v1.TextComplete = o.v1.TextGenerate = o.v1.ChatComplete = o.v1.ChatGenerate = o.v1.SyncTextOpenAI = o.v1.SyncChatOpenAI = NotImplementedWarning  # fmt: off

        def replace_ensure(func: FunctionType):
            from promplate.prompt.template import SafeChainMapContext as ChainMap

            return FunctionType(func.__code__, ChainMap({"ensure": patched_ensure}, func.__globals__), func.__name__, func.__defaults__, func.__closure__)

        for cls in o.v1.__dict__.values():
            if isclass(cls):
                for name, func in [*cls.__dict__.items()]:
                    if isfunction(func):
                        setattr(cls, name, replace_ensure(func))


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
