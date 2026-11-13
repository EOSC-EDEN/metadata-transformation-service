"""Domain failures independent of HTTP."""


class TransformationError(Exception):
    """A failed request, with a stable code and any completed processing steps."""

    def __init__(self, code: str, message: str, *, stage: str = "request"):
        super().__init__(message)
        self.code = code
        self.stage = stage
        self.steps: list[dict] = []
