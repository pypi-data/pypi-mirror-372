"""Agent executions resource for the Moderately AI API."""

from typing import Any, Dict, Optional

from ..types import AgentExecution, PaginatedResponse
from ._base import BaseResource


class AgentExecutions(BaseResource):
    """Manage agent executions and monitor their progress.

    Examples:
        ```python
        # List all executions
        executions = client.agent_executions.list()

        # Get a specific execution
        execution = client.agent_executions.retrieve("execution_123")

        # Create a new execution
        execution = client.agent_executions.create(
            agent_id="agent_123",
            input_data={"message": "Hello, world!"}
        )

        # Cancel a running execution
        client.agent_executions.cancel("execution_123")
        ```
    """

    def list(
        self,
        *,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all agent executions with pagination.

        Args:
            agent_id: Filter executions by agent ID.
            status: Filter executions by status (e.g., "running", "completed", "failed").
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of agent executions.
        """
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

        return self._get(
            "/agent-executions",
            options={"query": query},
        )

    def retrieve(self, execution_id: str) -> AgentExecution:
        """Retrieve a specific agent execution by ID.

        Args:
            execution_id: The ID of the execution to retrieve.

        Returns:
            The agent execution data.

        Raises:
            NotFoundError: If the execution doesn't exist.
        """
        return self._get(f"/agent-executions/{execution_id}")

    def create(
        self,
        *,
        agent_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> AgentExecution:
        """Create a new agent execution.

        Args:
            agent_id: The ID of the agent to execute.
            input_data: Input data to pass to the agent.
            **kwargs: Additional execution properties.

        Returns:
            The created agent execution data.

        Raises:
            ValidationError: If the request data is invalid.
            NotFoundError: If the agent doesn't exist.
        """
        body = {
            "agent_id": agent_id,
            **kwargs,
        }
        if input_data is not None:
            body["input_data"] = input_data

        return self._post("/agent-executions", body=body)

    def cancel(self, execution_id: str) -> AgentExecution:
        """Cancel a running agent execution.

        Args:
            execution_id: The ID of the execution to cancel.

        Returns:
            The updated execution data.

        Raises:
            NotFoundError: If the execution doesn't exist.
            ConflictError: If the execution cannot be cancelled (e.g., already completed).
        """
        return self._post(f"/agent-executions/{execution_id}/cancel")

    def wait_for_completion(
        self,
        execution_id: str,
        *,
        timeout: Optional[float] = None,
        poll_interval: float = 2.0,
    ) -> AgentExecution:
        """Wait for an agent execution to complete.

        This is a convenience method that polls the execution status until
        it reaches a terminal state (completed, failed, or cancelled).

        Args:
            execution_id: The ID of the execution to wait for.
            timeout: Maximum time to wait in seconds. If None, waits indefinitely.
            poll_interval: Time between status checks in seconds. Defaults to 2.0.

        Returns:
            The final execution data.

        Raises:
            TimeoutError: If the timeout is reached before completion.
            NotFoundError: If the execution doesn't exist.
        """
        import time

        start_time = time.time()

        while True:
            execution = self.retrieve(execution_id)
            status = execution.get("status", "")

            # Check if execution is in a terminal state
            if status in ["completed", "failed", "cancelled"]:
                return execution

            # Check timeout
            if timeout is not None and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Execution {execution_id} did not complete within {timeout} seconds"
                )

            # Wait before next poll
            time.sleep(poll_interval)
