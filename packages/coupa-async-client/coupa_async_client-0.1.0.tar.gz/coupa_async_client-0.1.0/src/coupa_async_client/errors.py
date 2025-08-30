class CoupaClientError(Exception):
    """Base exception for the library."""


class CoupaAuthError(CoupaClientError):
    """Auth/Token related errors."""
