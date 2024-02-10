from pathlib import Path


def patch_promplate(patch_openai=False):
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

    if patch_openai:
        from promplate.prompt.chat import ensure as _ensure

        from .utils.proxy import to_js

        def ensure(text_or_list: list[promplate.Message] | str):
            """This function is patched to return a JS array. So it should not be called from Python."""
            return to_js(_ensure(text_or_list))

        promplate.prompt.chat.ensure = ensure

        import promplate.llm.openai

        promplate.llm.openai.TextComplete = promplate.llm.openai.AsyncTextComplete
        promplate.llm.openai.TextGenerate = promplate.llm.openai.AsyncTextGenerate
        promplate.llm.openai.ChatComplete = promplate.llm.openai.AsyncChatComplete
        promplate.llm.openai.ChatGenerate = promplate.llm.openai.AsyncChatGenerate
        del promplate.llm.openai.SyncTextOpenAI
        del promplate.llm.openai.SyncChatOpenAI
