"""Agents resource for the Moderately AI API."""

from typing import Optional

from ..types import Agent, PaginatedResponse
from ._base import BaseResource


class Agents(BaseResource):
    """Manage AI agents in your teams.

    Examples:
        ```python
        # List all agents
        agents = client.agents.list()

        # Get a specific agent
        agent = client.agents.retrieve("agent_123")

        # Create a new agent
        agent = client.agents.create(
            name="Customer Support Agent",
            team_id="team_123",
            description="Handles customer inquiries"
        )

        # Update an agent
        agent = client.agents.update(
            "agent_123",
            name="Updated Agent Name"
        )

        # Delete an agent
        client.agents.delete("agent_123")
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
        """List all agents with pagination.

        Note: Results are automatically filtered to the team specified in the client.

        Args:
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of agents for the client's team.
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }

        return self._get(
            "/agents",
            options={"query": query},
        )

    def retrieve(self, agent_id: str) -> Agent:
        """Retrieve a specific agent by ID.

        Args:
            agent_id: The ID of the agent to retrieve.

        Returns:
            The agent data.

        Raises:
            NotFoundError: If the agent doesn't exist.
        """
        return self._get(f"/agents/{agent_id}")

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> Agent:
        """Create a new agent.

        Note: The agent will be created in the team specified in the client.

        Args:
            name: The agent's name.
            description: The agent's description.
            **kwargs: Additional agent properties.

        Returns:
            The created agent data.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "name": name,
            "team_id": self._client.team_id,  # Use client's team_id
            **kwargs,
        }
        if description is not None:
            body["description"] = description

        return self._post("/agents", body=body)

    def update(
        self,
        agent_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> Agent:
        """Update an existing agent.

        Args:
            agent_id: The ID of the agent to update.
            name: New agent name.
            description: New agent description.
            **kwargs: Additional properties to update.

        Returns:
            The updated agent data.

        Raises:
            NotFoundError: If the agent doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description

        return self._patch(f"/agents/{agent_id}", body=body)

    def delete(self, agent_id: str) -> None:
        """Delete an agent.

        Args:
            agent_id: The ID of the agent to delete.

        Raises:
            NotFoundError: If the agent doesn't exist.
        """
        self._delete(f"/agents/{agent_id}")
