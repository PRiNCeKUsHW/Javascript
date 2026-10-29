class ToolkitError(Exception):
    """Base class for every error this toolkit raises on purpose."""


class ValidationError(ToolkitError):
    """A record has a missing or invalid field."""

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field
