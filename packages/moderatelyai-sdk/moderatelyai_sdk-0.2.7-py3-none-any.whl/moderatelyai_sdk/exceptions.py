"""Exception classes for the Moderately AI SDK."""

from typing import Any, Dict, List, Optional


class ModeratelyAIError(Exception):
    """Base exception class for all Moderately AI SDK errors.

    All SDK-specific exceptions inherit from this class, making it easy
    to catch any SDK-related error with a single except clause.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class APIError(ModeratelyAIError):
    """Raised when an API request fails due to a server error or client error.

    This is the most common exception you'll encounter when using the SDK.
    It includes the HTTP status code and full response data for debugging.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class AuthenticationError(ModeratelyAIError):
    """Raised when authentication fails.

    This typically means:
    - No API key was provided
    - The API key is invalid or expired
    - The API key doesn't have permission for the requested operation
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)


class ValidationError(ModeratelyAIError):
    """Raised when request validation fails.

    This includes detailed information about which fields failed validation
    and why, making it easy to fix the request.
    """

    def __init__(
        self,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(message)
        self.validation_details = details or []

    def __str__(self) -> str:
        if not self.validation_details:
            return self.message

        details_str = []
        for detail in self.validation_details:
            field = detail.get("field", "unknown")
            field_message = detail.get("message", "validation failed")
            details_str.append(f"{field}: {field_message}")

        return f"{self.message}\nValidation errors:\n" + "\n".join(
            f"  - {d}" for d in details_str
        )


class RateLimitError(APIError):
    """Raised when the API rate limit is exceeded.

    Includes retry_after information when available, indicating how long
    to wait before making another request.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code=429)
        self.retry_after = retry_after

    def __str__(self) -> str:
        if self.retry_after:
            return f"{self.message}. Retry after {self.retry_after} seconds."
        return self.message


class TimeoutError(ModeratelyAIError):
    """Raised when a request times out.

    This can happen due to network issues or when the server takes too
    long to respond. The SDK automatically retries timeout errors with
    exponential backoff.
    """

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)


class NotFoundError(APIError):
    """Raised when a requested resource is not found (HTTP 404)."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class ConflictError(APIError):
    """Raised when a request conflicts with the current state (HTTP 409)."""

    def __init__(self, message: str = "Request conflicts with current state") -> None:
        super().__init__(message, status_code=409)


class UnprocessableEntityError(APIError):
    """Raised when the request is well-formed but semantically incorrect (HTTP 422)."""

    def __init__(self, message: str = "Unprocessable entity") -> None:
        super().__init__(message, status_code=422)
