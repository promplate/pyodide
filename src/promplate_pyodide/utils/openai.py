from contextlib import suppress
from typing import cast

from pyodide.code import run_js
from pyodide.ffi import JsCallable, register_js_module, to_js

get_openai_js_script = """(
  async () => {
    const [{ OpenAI }, version] = await Promise.all([import("openai"), import("openai/version")])
    return { OpenAI, version, __all__: [] }
  }
)()"""


async def ensure_openai(fallback_import_url: str):
    with suppress(ModuleNotFoundError):
        import openai.version

        return

    openai = await run_js(get_openai_js_script.replace("openai", fallback_import_url))  # noqa

    register_js_module("openai", openai)


def translate_openai():
    from openai import OpenAI

    js_openai_class = cast(JsCallable, OpenAI)

    def make_client(
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict | None = None,
        default_query: dict | None = None,
        **_,
    ):
        return js_openai_class.new(
            apiKey=api_key or "",
            organization=organization,
            baseURL=base_url,
            timeout=timeout,
            maxRetries=max_retries,
            defaultHeaders=to_js(default_headers),
            defaultQuery=to_js(default_query),
            dangerouslyAllowBrowser=True,
        )

    return make_client
