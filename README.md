# promplate-pyodide

Run your [`promplate`](https://promplate.dev/) project in the browser with [pyodide](https://pyodide.org/)!

## Usage

```py
from micropip import install  # in pyodide runtime
await install("promplate-pyodide")

from promplate_pyodide import patch_all
patch_all()
```

You can register the `openai` module as the JavaScript SDK in the JavaScript scope because the Python SDK v1.x doesn't support pyodide.

It will remove sync APIs of `promplate.llm.openai` because the JavaScript OpenAI SDK is async-only.

---

Of course you can use OpenAI Python SDK v0.x in pyodide, but it is not recommended.
