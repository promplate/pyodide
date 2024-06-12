try:
    from js import Promise  # type: ignore
    from pyodide.ffi import run_sync  # type: ignore

    def stack_switching_supported():  # type: ignore
        try:
            run_sync(Promise.resolve())
            return True
        except RuntimeError:
            return False

except ImportError:

    def stack_switching_supported():
        return False
