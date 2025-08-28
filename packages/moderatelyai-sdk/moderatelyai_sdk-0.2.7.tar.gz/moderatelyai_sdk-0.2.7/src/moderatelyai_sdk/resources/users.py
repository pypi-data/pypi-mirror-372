"""Users resource for the Moderately AI API."""


from ..models.user import UserModel
from ..types import PaginatedResponse
from ._base import BaseResource


class Users(BaseResource):
    """Manage users in your organization.

    Note: The Users resource only supports read and update operations.
    User creation and deletion are handled through other mechanisms.

    Examples:
        ```python
        # List all users (returns raw paginated data)
        users_response = client.users.list()

        # Get a specific user with rich functionality
        user = client.users.retrieve("user_123")

        # Use rich user operations
        print(f"User: {user.display_name()} ({user.full_name})")
        print(f"Nickname: {user.nickname}")
        print(f"Created: {user.formatted_created_at()}")

        # Update user profile
        user = user.update_profile(full_name="Jane Smith")

        # Or update via resource
        user = client.users.update("user_123", full_name="John Doe")
        ```
    """

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all users with pagination.

        Args:
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of users.
        """
        response = self._get(
            "/users",
            options={
                "query": {
                    "page": page,
                    "page_size": page_size,
                    "order_by": order_by,
                    "order_direction": order_direction,
                }
            },
        )

        # Convert items to UserModel instances
        if "items" in response:
            response["items"] = [
                UserModel(item, self._client) for item in response["items"]
            ]

        return response

    def retrieve(self, user_id: str) -> UserModel:
        """Retrieve a specific user by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The user model with rich functionality.

        Raises:
            NotFoundError: If the user doesn't exist.
        """
        data = self._get(f"/users/{user_id}")
        return UserModel(data, self._client)

    def update(
        self,
        user_id: str,
        *,
        full_name: str,
        **kwargs,
    ) -> UserModel:
        """Update an existing user.

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

        data = self._patch(f"/users/{user_id}", body=body)
        return UserModel(data, self._client)
