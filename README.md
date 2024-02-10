# promplate-pyodide

Run your [`promplate`](https://promplate.dev/) project in the browser with [pyodide](https://pyodide.org/)!

## Usage

If you just want to use its templating staff:

```py
from micropip import install  # in pyodide runtime
await install("promplate-pyodide")

from promplate_pyodide import *
patch_promplate()
```

If you also want to use its OpenAI LLM, you should register the `openai` module because it is not compatible with pyodide.
Note that you can register it as the JavaScript OpenAI SDK because its API is similar to the Python SDK.

```py
patch_promplate(True)
```

This will patch `ensure` method to return a JavaScript array instead of a Python list.
And it will remove sync APIs of `promplate.llm.openai` because the JavaScript OpenAI SDK is async-only.
