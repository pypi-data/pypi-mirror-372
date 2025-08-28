"""User model with rich functionality for user operations.

This module provides the UserModel class, which represents a user with rich
functionality for user management operations like updating profile and
accessing user resources.

Example:
    ```python
    from moderatelyai_sdk import ModeratelyAI

    client = ModeratelyAI(api_key="your_key", team_id="your_team")

    # Get a user with rich functionality
    user = client.users.retrieve("user_123")

    # Use rich user operations
    print(f"User: {user.display_name()} ({user.full_name})")
    print(f"Created: {user.formatted_created_at()}")

    if user.has_nickname():
        print(f"Nickname: {user.nickname}")

    # Update user profile
    user.update_profile(full_name="New Name")

    # Get user's teams (if applicable)
    teams = user.get_teams()

    # Check if user was recently created
    if user.is_recent(days=7):
        print("This is a new user!")
    ```
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..exceptions import APIError
from ._base import BaseModel


class UserModel(BaseModel):
    """Model representing a user with rich functionality.

    UserModel provides a high-level interface for working with users in the
    Moderately AI platform. Instead of working with raw dictionaries, you get
    a rich object with methods for common user operations.

    This class is returned by user operations like:
    - `client.users.retrieve()`
    - `client.users.update()`

    Note: User creation and deletion are not supported by the API.

    Attributes:
        user_id: Unique identifier for the user
        full_name: User's full name
        nickname: User's nickname (optional)
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        ```python
        # Get a user and check properties
        user = client.users.retrieve("user_123")

        print(f"User: {user.display_name()} ({user.full_name})")
        print(f"Member since: {user.formatted_created_at()}")

        # Update user profile
        if not user.has_nickname():
            user.update_profile(nickname="Cool Nickname")

        # Check if user is recently created
        if user.is_recent(days=30):
            print("Welcome new user!")
        ```
    """

    @property
    def user_id(self) -> str:
        """The unique identifier for this user."""
        return self._data["userId"]

    @property
    def full_name(self) -> str:
        """The user's full name."""
        return self._data["fullName"]

    @property
    def nickname(self) -> Optional[str]:
        """The user's nickname."""
        return self._data.get("nickname")

    @property
    def created_at(self) -> str:
        """When this user was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this user was last updated."""
        return self._data["updatedAt"]

    def display_name(self) -> str:
        """Get the user's display name, using nickname or full name.

        Returns:
            The user's nickname if available, otherwise their full name.

        Example:
            ```python
            print(f"Welcome, {user.display_name()}!")
            ```
        """
        return self.nickname or self.full_name

    def has_nickname(self) -> bool:
        """Check if the user has a nickname set.

        Returns:
            True if the user has a nickname, False if only full name is available.

        Example:
            ```python
            if not user.has_nickname():
                user.update_profile(nickname="Cool Nickname")
            ```
        """
        return self.nickname is not None and self.nickname.strip() != ""

    def formatted_created_at(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get a formatted version of the creation timestamp.

        Args:
            format_str: Python datetime format string. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            Formatted creation timestamp.

        Example:
            ```python
            # Default format
            print(f"Created: {user.formatted_created_at()}")

            # Custom format
            print(f"Joined: {user.formatted_created_at('%B %d, %Y')}")
            ```
        """
        try:
            # Assuming ISO format timestamp
            created_dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            return created_dt.strftime(format_str)
        except (ValueError, AttributeError):
            # Fallback to original string if parsing fails
            return self.created_at

    def is_recent(self, days: int = 7) -> bool:
        """Check if the user was created recently.

        Args:
            days: Number of days to consider as "recent". Defaults to 7.

        Returns:
            True if the user was created within the specified number of days.

        Example:
            ```python
            # Check if user joined in the last week
            if user.is_recent():
                send_welcome_email(user)

            # Check if user joined in the last month
            if user.is_recent(days=30):
                show_onboarding_tips(user)
            ```
        """
        try:
            created_dt = datetime.fromisoformat(self.created_at.replace('Z', '+00:00'))
            cutoff_dt = datetime.now() - timedelta(days=days)
            return created_dt.replace(tzinfo=None) > cutoff_dt
        except (ValueError, AttributeError):
            # If we can't parse the date, assume not recent
            return False

    def update_profile(
        self,
        *,
        full_name: Optional[str] = None,
        nickname: Optional[str] = None,
        **kwargs: Any,
    ) -> "UserModel":
        """Update this user's profile information.

        Args:
            full_name: New full name for the user.
            nickname: New nickname for the user.
            **kwargs: Additional properties to update.

        Returns:
            Updated user model.

        Example:
            ```python
            # Update user's full name
            user = user.update_profile(full_name="John Smith")

            # Update nickname
            user = user.update_profile(nickname="Johnny")

            # Update multiple properties
            user = user.update_profile(
                full_name="Jane Doe",
                nickname="Janie"
            )
            ```
        """
        body = {**kwargs}
        if full_name is not None:
            body["fullName"] = full_name
        if nickname is not None:
            body["nickname"] = nickname

        updated_data = self._client._request(
            method="PATCH",
            path=f"/users/{self.user_id}",
            body=body,
            cast_type=dict,
        )

        # Update our internal data and return self
        self._data = updated_data
        return self

    def get_teams(self) -> List[Dict[str, Any]]:
        """Get the teams this user belongs to.

        Returns:
            List of team data dictionaries.

        Example:
            ```python
            teams = user.get_teams()
            for team in teams:
                print(f"Member of: {team['name']}")
            ```
        """
        try:
            response = self._client._request(
                method="GET",
                path=f"/users/{self.user_id}/teams",
                cast_type=dict,
            )
            return response.get("items", [])
        except APIError:
            # If endpoint doesn't exist or user has no teams, return empty list
            return []


    def _refresh(self) -> None:
        """Refresh this user from the API."""
        response = self._client._request(
            method="GET",
            path=f"/users/{self.user_id}",
            cast_type=dict,
        )
        self._data = response
