"""Custom exceptions for UV API integrations."""


class UVServiceError(RuntimeError):
    """Raised when the external UV service cannot return valid data."""


class UVServiceFallback(RuntimeError):
    """Raised when a fallback response is returned instead of live data."""
