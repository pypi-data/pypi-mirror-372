from typing import Optional


class AuthError(Exception):
    """Raised when authentication or token retrieval fails."""

    def __init__(self, message: str, *, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ApiError(Exception):
    """Raised when the Patsnap API returns an error.

    Contains optional HTTP status code and Patsnap-specific error_code.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response_text = response_text

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        parts = [super().__str__()]
        if self.status_code is not None:
            parts.append(f"http={self.status_code}")
        if self.error_code is not None:
            parts.append(f"code={self.error_code}")
        return " | ".join(parts)


