"""Async agents resource for the Moderately AI API."""

from typing import Optional

from ..types import Agent, PaginatedResponse
from ._base import AsyncBaseResource


class AsyncAgents(AsyncBaseResource):
    """Manage AI agents in your teams (async version).

    Examples:
        ```python
        import asyncio
        import moderatelyai_sdk

        async def main():
            async with moderatelyai_sdk.AsyncModeratelyAI() as client:
                # List all agents
                agents = await client.agents.list()

                # Get a specific agent
                agent = await client.agents.retrieve("agent_123")

                # Create a new agent
                agent = await client.agents.create(
                    name="Customer Support Agent",
                    description="Handles customer inquiries"
                )

                # Update an agent
                agent = await client.agents.update(
                    "agent_123",
                    name="Updated Agent Name"
                )

                # Delete an agent
                await client.agents.delete("agent_123")

        asyncio.run(main())
        ```
    """

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all agents with pagination (async).

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

        return await self._get(
            "/agents",
            options={"query": query},
        )

    async def retrieve(self, agent_id: str) -> Agent:
        """Retrieve a specific agent by ID (async).

        Args:
            agent_id: The ID of the agent to retrieve.

        Returns:
            The agent data.

        Raises:
            NotFoundError: If the agent doesn't exist.
        """
        return await self._get(f"/agents/{agent_id}")

    async def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> Agent:
        """Create a new agent (async).

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
            "teamId": self._client.team_id,  # Use client's team_id (API expects camelCase)
            **kwargs,
        }
        if description is not None:
            body["description"] = description

        return await self._post("/agents", body=body)

    async def update(
        self,
        agent_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> Agent:
        """Update an existing agent (async).

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

        return await self._patch(f"/agents/{agent_id}", body=body)

    async def delete(self, agent_id: str) -> None:
        """Delete an agent (async).

        Args:
            agent_id: The ID of the agent to delete.

        Raises:
            NotFoundError: If the agent doesn't exist.
        """
        await self._delete(f"/agents/{agent_id}")
