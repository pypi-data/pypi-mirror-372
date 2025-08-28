"""Async teams resource for the Moderately AI API."""

from typing import Optional

from ..types import PaginatedResponse, Team
from ._base import AsyncBaseResource


class AsyncTeams(AsyncBaseResource):
    """Manage teams (async version)."""

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all teams with pagination (async)."""
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        return await self._get("/teams", options={"query": query})

    async def retrieve(self, team_id: str) -> Team:
        """Retrieve a specific team by ID (async)."""
        return await self._get(f"/teams/{team_id}")

    async def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> Team:
        """Create a new team (async)."""
        body = {
            "name": name,
            **kwargs,
        }
        if description is not None:
            body["description"] = description
        return await self._post("/teams", body=body)

    async def update(
        self,
        team_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> Team:
        """Update an existing team (async)."""
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        return await self._patch(f"/teams/{team_id}", body=body)

    async def delete(self, team_id: str) -> None:
        """Delete a team (async)."""
        await self._delete(f"/teams/{team_id}")
