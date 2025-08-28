"""Async agent executions resource for the Moderately AI API."""

from typing import Any, Dict, Optional

from ..types import AgentExecution, PaginatedResponse
from ._base import AsyncBaseResource


class AsyncAgentExecutions(AsyncBaseResource):
    """Manage agent executions in your teams (async version)."""

    async def list(
        self,
        *,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all agent executions with pagination (async)."""
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        if agent_id is not None:
            query["agent_id"] = agent_id
        if status is not None:
            query["status"] = status

        return await self._get("/agent-executions", options={"query": query})

    async def retrieve(self, execution_id: str) -> AgentExecution:
        """Retrieve a specific agent execution by ID (async)."""
        return await self._get(f"/agent-executions/{execution_id}")

    async def create(
        self,
        *,
        agent_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AgentExecution:
        """Create a new agent execution (async)."""
        body = {
            "agent_id": agent_id,
            **kwargs,
        }
        if input_data is not None:
            body["input_data"] = input_data

        return await self._post("/agent-executions", body=body)

    async def cancel(self, execution_id: str) -> AgentExecution:
        """Cancel a running agent execution (async)."""
        return await self._patch(f"/agent-executions/{execution_id}/cancel")

    async def delete(self, execution_id: str) -> None:
        """Delete an agent execution (async)."""
        await self._delete(f"/agent-executions/{execution_id}")
