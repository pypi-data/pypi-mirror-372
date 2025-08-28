"""Base resource class for all async API resources."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .._base_client_async import AsyncBaseClient


class AsyncBaseResource:
    """Base class for all async API resources.

    Provides common functionality for making async API requests and handling responses.
    """

    def __init__(self, client: "AsyncBaseClient") -> None:
        self._client = client

    async def _get(
        self,
        path: str,
        *,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async GET request."""
        return await self._client._request(
            method="GET",
            path=path,
            cast_type=cast_type,
            options=options,
        )

    async def _post(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async POST request."""
        return await self._client._request(
            method="POST",
            path=path,
            body=body,
            cast_type=cast_type,
            options=options,
        )

    async def _patch(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async PATCH request."""
        return await self._client._request(
            method="PATCH",
            path=path,
            body=body,
            cast_type=cast_type,
            options=options,
        )

    async def _put(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async PUT request."""
        return await self._client._request(
            method="PUT",
            path=path,
            body=body,
            cast_type=cast_type,
            options=options,
        )

    async def _delete(
        self,
        path: str,
        *,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an async DELETE request."""
        return await self._client._request(
            method="DELETE",
            path=path,
            cast_type=cast_type,
            options=options,
        )
