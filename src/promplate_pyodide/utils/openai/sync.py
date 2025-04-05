# type: ignore

from ..sync import to_sync


def patch_sync_apis():
    from promplate.llm.openai import v0, v1

    v1.SyncTextOpenAI.complete = v1.TextComplete.__call__ = to_sync(v1.AsyncTextComplete.__call__)
    v1.SyncTextOpenAI.generate = v1.TextGenerate.__call__ = to_sync(v1.AsyncTextGenerate.__call__)
    v1.SyncChatOpenAI.complete = v1.ChatComplete.__call__ = to_sync(v1.AsyncChatComplete.__call__)
    v1.SyncChatOpenAI.generate = v1.ChatGenerate.__call__ = to_sync(v1.AsyncChatGenerate.__call__)

    v0.TextComplete.__call__ = to_sync(v0.AsyncTextComplete.__call__)
    v0.TextGenerate.__call__ = to_sync(v0.AsyncTextGenerate.__call__)
    v0.ChatComplete.__call__ = to_sync(v0.AsyncChatComplete.__call__)
    v0.ChatGenerate.__call__ = to_sync(v0.AsyncChatGenerate.__call__)
