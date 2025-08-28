"""Async base client functionality shared between async clients."""

import asyncio
import json
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx

from .exceptions import (
    APIError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .types import HTTPMethod


class AsyncBaseClient:
    """Base async client with shared functionality."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: Union[float, httpx.Timeout],
        max_retries: int,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        team_id: Optional[str] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
        self.default_query = default_query or {}
        self.team_id = team_id

        if http_client is not None:
            self._client = http_client
        else:
            self._client = httpx.AsyncClient(
                timeout=timeout,
                headers=self._build_headers(),
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
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
        """Build the complete URL for a request."""
        path = path.lstrip("/")
        return urljoin(f"{self.base_url}/", path)

    async def _request(
        self,
        method: HTTPMethod,
        path: str,
        *,
        cast_type: type,
        body: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async HTTP request with automatic retries and error handling."""
        options = options or {}
        url = self._build_url(path)

        # Prepare request parameters
        params = {**self.default_query, **options.get("query", {})}
        headers = options.get("headers", {})
        json_data = body if body is not None else None

        # Retry logic with exponential backoff
        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                )
                return await self._process_response(response, cast_type=cast_type)
            except RateLimitError as e:
                if attempt == self.max_retries:
                    raise
                # Wait for the retry-after time or use exponential backoff
                wait_time = getattr(e, "retry_after", 2**attempt)
                await asyncio.sleep(wait_time)
                last_exception = e
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                if attempt == self.max_retries:
                    raise TimeoutError(
                        f"Request timed out after {self.max_retries + 1} attempts"
                    ) from e
                await asyncio.sleep(2**attempt)  # Exponential backoff
                last_exception = e

        # If we get here, we exhausted all retries
        if last_exception:
            raise last_exception

    async def _process_response(self, response: httpx.Response, *, cast_type: type) -> Any:
        """Process the HTTP response and handle errors."""
        # Handle HTTP errors
        if response.status_code >= 400:
            await self._handle_error_response(response)

        # Handle rate limiting
        if response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                retry_after = int(retry_after)
            else:
                retry_after = 60

            error = RateLimitError("Rate limit exceeded")
            error.retry_after = retry_after
            raise error

        # Handle successful responses
        if response.status_code == 204:  # No Content
            return None

        # Handle empty responses (like DELETE operations)
        if cast_type is type(None):
            return None

        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            # If we expect no content and got empty response, that's fine
            if cast_type is type(None):
                return None
            raise APIError(f"Invalid JSON response: {e}") from e

        # Validate response structure if needed
        if cast_type is dict:
            return data

        # For typed responses, you could add validation here
        return data

    async def _handle_error_response(self, response: httpx.Response) -> None:
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
