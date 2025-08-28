"""Teams resource for the Moderately AI API."""

from typing import Optional

from ..types import PaginatedResponse, Team
from ._base import BaseResource


class Teams(BaseResource):
    """Manage teams in your organization.

    Examples:
        ```python
        # List all teams
        teams = client.teams.list()

        # Get a specific team
        team = client.teams.retrieve("team_123")

        # Create a new team
        team = client.teams.create(
            name="Engineering Team",
            description="Software development team"
        )

        # Update a team
        team = client.teams.update(
            "team_123",
            name="Updated Team Name"
        )

        # Delete a team
        client.teams.delete("team_123")
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
        """List all teams with pagination.

        Args:
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of teams.
        """
        return self._get(
            "/teams",
            options={
                "query": {
                    "page": page,
                    "page_size": page_size,
                    "order_by": order_by,
                    "order_direction": order_direction,
                }
            },
        )

    def retrieve(self, team_id: str) -> Team:
        """Retrieve a specific team by ID.

        Args:
            team_id: The ID of the team to retrieve.

        Returns:
            The team data.

        Raises:
            NotFoundError: If the team doesn't exist.
        """
        return self._get(f"/teams/{team_id}")

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> Team:
        """Create a new team.

        Args:
            name: The team's name.
            description: The team's description.
            **kwargs: Additional team properties.

        Returns:
            The created team data.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "name": name,
            **kwargs,
        }
        if description is not None:
            body["description"] = description

        return self._post("/teams", body=body)

    def update(
        self,
        team_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> Team:
        """Update an existing team.

        Args:
            team_id: The ID of the team to update.
            name: New team name.
            description: New team description.
            **kwargs: Additional properties to update.

        Returns:
            The updated team data.

        Raises:
            NotFoundError: If the team doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description

        return self._patch(f"/teams/{team_id}", body=body)

    def delete(self, team_id: str) -> None:
        """Delete a team.

        Args:
            team_id: The ID of the team to delete.

        Raises:
            NotFoundError: If the team doesn't exist.
        """
        self._delete(f"/teams/{team_id}")
