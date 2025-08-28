"""Base client functionality shared between sync and async clients."""

import json
import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx

from .exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .types import HTTPMethod


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        max_backoff: float = 60.0,
        retryable_status_codes: Optional[List[int]] = None,
    ) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.max_backoff = max_backoff
        self.retryable_status_codes = retryable_status_codes or [429, 502, 503, 504]


class BaseClient:
    """Base client with shared functionality for both sync and async clients."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: Union[float, httpx.Timeout] = 30.0,
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        team_id: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.retry_config = retry_config or RetryConfig(max_retries=max_retries)
        self.default_headers = default_headers or {}
        self.default_query = default_query or {}
        self.team_id = team_id

        if http_client is not None:
            self._client = http_client
        else:
            # Configure timeout with sane defaults
            if isinstance(timeout, (int, float)):
                timeout = httpx.Timeout(
                    connect=10.0,  # 10s to establish connection
                    read=timeout,  # User-specified read timeout
                    write=30.0,  # 30s to send data
                    pool=5.0,  # 5s to get connection from pool
                )

            self._client = httpx.Client(
                timeout=timeout,
                headers=self._build_headers(),
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0,
                ),
                follow_redirects=True,
            )

    def _build_headers(self) -> Dict[str, str]:
        """Build default headers for requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "moderatelyai-python/0.1.0",
            "Accept": "application/json",
        }
        headers.update(self.default_headers)
        return headers

    def _build_url(self, path: str) -> str:
        """Build the full URL for a request."""
        if path.startswith("/"):
            path = path[1:]
        return urljoin(self.base_url + "/", path)

    def _request(
        self,
        method: HTTPMethod,
        path: str,
        *,
        cast_type: type,
        body: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an HTTP request with automatic retries and error handling."""
        options = options or {}
        url = self._build_url(path)

        # Prepare request parameters
        params = {**self.default_query, **options.get("query", {})}
        headers = options.get("headers", {})
        json_data = body if body is not None else None

        # Retry logic with configurable exponential backoff
        last_exception: Optional[Exception] = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                response = self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                )

                # Check if we should retry based on status code
                if (
                    attempt < self.retry_config.max_retries
                    and response.status_code in self.retry_config.retryable_status_codes
                ):
                    wait_time = min(
                        self.retry_config.backoff_factor**attempt,
                        self.retry_config.max_backoff,
                    )
                    time.sleep(wait_time)
                    continue

                return self._process_response(response, cast_type=cast_type)

            except RateLimitError as e:
                if attempt == self.retry_config.max_retries:
                    raise
                # Use retry-after header if available, otherwise exponential backoff
                wait_time = getattr(e, "retry_after", None)
                if wait_time is None:
                    wait_time = min(
                        self.retry_config.backoff_factor**attempt,
                        self.retry_config.max_backoff,
                    )
                time.sleep(wait_time)
                last_exception = e

            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as e:
                if attempt == self.retry_config.max_retries:
                    raise TimeoutError(
                        f"Request failed after {self.retry_config.max_retries + 1} attempts: {str(e)}"
                    ) from e

                # Exponential backoff for network errors
                wait_time = min(
                    self.retry_config.backoff_factor**attempt,
                    self.retry_config.max_backoff,
                )
                time.sleep(wait_time)
                last_exception = e

        # If we get here, we exhausted all retries
        if last_exception:
            raise last_exception

    def _process_response(self, response: httpx.Response, *, cast_type: type) -> Any:
        """Process the HTTP response and handle errors."""
        # Handle HTTP error status codes
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key or authentication failed")
        elif response.status_code == 403:
            raise AuthenticationError("Insufficient permissions for this operation")
        elif response.status_code == 429:
            # Extract retry-after from headers if available
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    retry_after = int(retry_after)
                except ValueError:
                    retry_after = 60
            else:
                retry_after = 60

            error = RateLimitError("Rate limit exceeded")
            error.retry_after = retry_after
            raise error
        elif response.status_code >= 400:
            self._handle_error_response(response)

        # Parse successful response
        if response.status_code == 204:  # No Content
            return None

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {e}") from e

        # Validate response structure if needed
        if cast_type is dict:
            return data

        # For typed responses, you could add validation here
        return data

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        try:
            error_data = response.json()

            # Check if it's a validation error with detailed field errors
            if response.status_code == 400 and "details" in error_data:
                raise ValidationError(
                    error_data.get("message", f"HTTP {response.status_code}"),
                    details=error_data.get("details", []),
                )

            # General API error
            error_message = error_data.get("message", f"HTTP {response.status_code}")
            raise APIError(
                error_message,
                status_code=response.status_code,
                response_data=error_data,
            )
        except json.JSONDecodeError:
            # If we can't parse the error response as JSON
            raise APIError(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
            ) from None
