class WarnPrinter:
    def __init__(self, warn: str):
        self.warn = warn

    def __call__(self, *args, **kwargs):
        return self

    def __await__(self):
        return self

    def __repr__(self) -> str:
        return self.warn


NotImplementedWarning = WarnPrinter("This feature does not support pyodide runtime!")
