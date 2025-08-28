"""Base resource class for all API resources."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .._base_client import BaseClient


class BaseResource:
    """Base class for all API resources.

    Provides common functionality for making API requests and handling responses.
    """

    def __init__(self, client: "BaseClient") -> None:
        self._client = client

    def _get(
        self,
        path: str,
        *,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a GET request."""
        return self._client._request(
            method="GET",
            path=path,
            cast_type=cast_type,
            options=options,
        )

    def _post(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a POST request."""
        return self._client._request(
            method="POST",
            path=path,
            body=body,
            cast_type=cast_type,
            options=options,
        )

    def _patch(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PATCH request."""
        return self._client._request(
            method="PATCH",
            path=path,
            body=body,
            cast_type=cast_type,
            options=options,
        )

    def _put(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a PUT request."""
        return self._client._request(
            method="PUT",
            path=path,
            body=body,
            cast_type=cast_type,
            options=options,
        )

    def _delete(
        self,
        path: str,
        *,
        cast_type: type = dict,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a DELETE request."""
        return self._client._request(
            method="DELETE",
            path=path,
            cast_type=cast_type,
            options=options,
        )
