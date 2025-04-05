from ..sync import to_sync


def patch_sync_apis():
    from promplate.llm import openai as o

    o.SyncTextOpenAI.complete = o.TextComplete.__call__ = to_sync(o.AsyncTextComplete.__call__)  # type: ignore
    o.SyncTextOpenAI.generate = o.TextGenerate.__call__ = to_sync(o.AsyncTextGenerate.__call__)  # type: ignore
    o.SyncChatOpenAI.complete = o.ChatComplete.__call__ = to_sync(o.AsyncChatComplete.__call__)  # type: ignore
    o.SyncChatOpenAI.generate = o.ChatGenerate.__call__ = to_sync(o.AsyncChatGenerate.__call__)  # type: ignore
