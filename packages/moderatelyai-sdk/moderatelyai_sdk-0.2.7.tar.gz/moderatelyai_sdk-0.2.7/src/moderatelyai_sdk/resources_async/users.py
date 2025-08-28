"""Async users resource for the Moderately AI API."""


from ..models.user_async import UserAsyncModel
from ..types import PaginatedResponse
from ._base import AsyncBaseResource


class AsyncUsers(AsyncBaseResource):
    """Manage users in your teams (async version)."""

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all users with pagination (async)."""
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        response = await self._get("/users", options={"query": query})

        # Convert items to UserAsyncModel instances
        if "items" in response:
            response["items"] = [
                UserAsyncModel(item, self._client) for item in response["items"]
            ]

        return response

    async def retrieve(self, user_id: str) -> UserAsyncModel:
        """Retrieve a specific user by ID (async)."""
        data = await self._get(f"/users/{user_id}")
        return UserAsyncModel(data, self._client)

    async def update(
        self,
        user_id: str,
        *,
        full_name: str,
        **kwargs,
    ) -> UserAsyncModel:
        """Update an existing user (async).

        Args:
            user_id: The ID of the user to update.
            full_name: New full name for the user (required).
            **kwargs: Additional properties to update.

        Returns:
            The updated user model with rich functionality.

        Raises:
            NotFoundError: If the user doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {
            "fullName": full_name,
            **kwargs,
        }

        data = await self._patch(f"/users/{user_id}", body=body)
        return UserAsyncModel(data, self._client)
