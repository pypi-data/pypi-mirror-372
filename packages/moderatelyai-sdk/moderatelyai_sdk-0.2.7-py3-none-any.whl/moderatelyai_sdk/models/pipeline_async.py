"""Async pipeline model for the Moderately AI SDK."""

from typing import Any, Dict, List, Optional

from .._base_client_async import AsyncBaseClient
from ..types import Pipeline
from ._base_async import BaseAsyncModel


class PipelineAsyncModel(BaseAsyncModel):
    """Rich async pipeline model with convenient methods for pipeline management.

    Provides an object-oriented interface for working with pipelines asynchronously,
    including creating configurations, executing pipelines, and monitoring results.

    Examples:
        ```python
        # Get pipeline and execute it (non-blocking)
        pipeline = await client.pipelines.retrieve("pipeline_123")
        execution = await pipeline.execute(
            configuration_version_id="version_123",
            pipeline_input={"documents": ["doc1.pdf"]},
            pipeline_input_summary="Process document"
        )

        # Execute and block until completion
        execution = await pipeline.execute(
            configuration_version_id="version_123",
            pipeline_input={"documents": ["doc1.pdf"]},
            pipeline_input_summary="Process document",
            block=True,
            timeout=300  # 5 minute timeout
        )
        print(f"Execution completed with status: {execution.status}")
        ```
    """

    def __init__(self, data: Pipeline, client: AsyncBaseClient) -> None:
        super().__init__(data, client)

    @property
    def pipeline_id(self) -> str:
        """The unique identifier for this pipeline."""
        return self._data["pipelineId"]

    @property
    def team_id(self) -> str:
        """The team ID that owns this pipeline."""
        return self._data["teamId"]

    @property
    def name(self) -> str:
        """The pipeline name."""
        return self._data["name"]

    @property
    def description(self) -> Optional[str]:
        """The pipeline description."""
        return self._data.get("description")

    @property
    def created_at(self) -> Optional[str]:
        """When the pipeline was created."""
        return self._data.get("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        """When the pipeline was last updated."""
        return self._data.get("updatedAt")

    @property
    def last_run_at(self) -> Optional[str]:
        """When the pipeline was last executed."""
        return self._data.get("lastRunAt")

    @property
    def total_runs(self) -> float:
        """Total number of executions for this pipeline."""
        return self._data.get("totalRuns", 0)

    @property
    def successful_runs(self) -> float:
        """Number of successful executions."""
        return self._data.get("successfulRuns", 0)

    @property
    def success_rate(self) -> float:
        """Success rate (0.0 to 1.0) for pipeline executions."""
        return self._data.get("successRate", 0.0)

    async def update(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "PipelineAsyncModel":
        """Update this pipeline and return the updated instance (async).

        Args:
            name: New pipeline name.
            description: New pipeline description.
            **kwargs: Additional properties to update.

        Returns:
            Updated pipeline model instance.
        """
        updated_data = await self._client._request(
            method="PATCH",
            path=f"/pipelines/{self.pipeline_id}",
            cast_type=dict,
            body={
                k: v for k, v in {
                    "name": name,
                    "description": description,
                    **kwargs
                }.items() if v is not None
            }
        )
        return PipelineAsyncModel(updated_data, self._client)

    async def delete(self) -> None:
        """Delete this pipeline (async).

        Warning: This will permanently delete the pipeline and all associated
        configuration versions and executions.
        """
        await self._client._request(
            method="DELETE",
            path=f"/pipelines/{self.pipeline_id}",
            cast_type=dict,
        )

    async def create_configuration_version(
        self,
        *,
        configuration: Dict[str, Any],
        **kwargs
    ):
        """Create a new configuration version for this pipeline (async).

        Args:
            configuration: The pipeline configuration object with blocks and connections.
            **kwargs: Additional configuration version properties.

        Returns:
            The created async configuration version model.
        """
        from .pipeline_configuration_version_async import PipelineConfigurationVersionAsyncModel

        data = await self._client._request(
            method="POST",
            path="/pipeline-configuration-versions",
            cast_type=dict,
            body={
                "pipelineId": self.pipeline_id,
                "configuration": configuration,
                **kwargs
            }
        )
        return PipelineConfigurationVersionAsyncModel(data, self._client)

    async def list_configuration_versions(self):
        """Get all configuration versions for this pipeline (async).

        Returns:
            List of async configuration version models.
        """
        from .pipeline_configuration_version_async import PipelineConfigurationVersionAsyncModel

        response = await self._client._request(
            method="GET",
            path="/pipeline-configuration-versions",
            cast_type=dict,
            options={"query": {"pipelineIds": self.pipeline_id}}
        )

        return [
            PipelineConfigurationVersionAsyncModel(item, self._client)
            for item in response.get("items", [])
        ]

    async def list_executions(
        self,
        *,
        status: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10
    ):
        """Get executions for this pipeline (async).

        Args:
            status: Filter by single execution status.
            statuses: Filter by multiple execution statuses.
            page: Page number (1-based).
            page_size: Number of items per page.

        Returns:
            List of async execution models.
        """
        from .pipeline_execution_async import PipelineExecutionAsyncModel

        query = {
            "pipelineIds": self.pipeline_id,
            "page": page,
            "pageSize": page_size
        }
        if status:
            query["status"] = status
        if statuses:
            query["statuses"] = ",".join(statuses)

        response = await self._client._request(
            method="GET",
            path="/pipeline-executions",
            cast_type=dict,
            options={"query": query}
        )

        return [
            PipelineExecutionAsyncModel(item, self._client)
            for item in response.get("items", [])
        ]

    async def get_latest_execution(self):
        """Get the most recent execution for this pipeline (async).

        Returns:
            Latest async execution model or None if no executions exist.
        """
        executions = await self.list_executions(page_size=1)
        return executions[0] if executions else None

    async def execute(
        self,
        *,
        configuration_version_id: str,
        pipeline_input: Dict[str, Any],
        pipeline_input_summary: str,
        block: bool = False,
        timeout: Optional[int] = None,
        poll_interval: float = 2.0,
        show_progress: bool = True,
        **kwargs
    ):
        """Execute this pipeline with the given configuration and input (async).

        This is the main convenience method that provides both non-blocking and
        blocking execution modes. When block=True, it follows the polling pattern
        from the demo script to wait for completion.

        Args:
            configuration_version_id: ID of the configuration version to execute.
            pipeline_input: Input data for the pipeline execution.
            pipeline_input_summary: Human-readable summary of the input.
            block: If True, wait for execution to complete before returning.
            timeout: Maximum time to wait in seconds (only used with block=True).
            poll_interval: How often to poll for status updates in seconds.
            show_progress: Whether to show progress updates during blocking execution.
            **kwargs: Additional execution properties.

        Returns:
            Async pipeline execution model. If block=False, returns immediately with
            pending/running execution. If block=True, returns completed execution.

        Raises:
            TimeoutError: If block=True and execution doesn't complete within timeout.
            Exception: If block=True and execution fails or is cancelled.

        Examples:
            ```python
            # Non-blocking execution (default)
            execution = await pipeline.execute(
                configuration_version_id="version_123",
                pipeline_input={"documents": ["doc1.pdf"]},
                pipeline_input_summary="Process document"
            )
            print(f"Started execution: {execution.execution_id}")

            # Blocking execution with timeout
            execution = await pipeline.execute(
                configuration_version_id="version_123",
                pipeline_input={"documents": ["doc1.pdf"]},
                pipeline_input_summary="Process document",
                block=True,
                timeout=600,  # 10 minutes
                poll_interval=3.0
            )
            if execution.is_completed:
                results = await execution.get_output()
                print(f"Success! Results: {results}")
            ```
        """
        from .pipeline_execution_async import PipelineExecutionAsyncModel

        # Create the execution
        execution_data = await self._client._request(
            method="POST",
            path="/pipeline-executions",
            cast_type=dict,
            body={
                "pipelineConfigurationVersionId": configuration_version_id,
                "pipelineInput": pipeline_input,
                "pipelineInputSummary": pipeline_input_summary,
                **kwargs
            }
        )

        execution = PipelineExecutionAsyncModel(execution_data, self._client)

        # If not blocking, return immediately
        if not block:
            return execution

        # Block and poll until completion using the execution model's wait method
        return await execution.wait_for_completion(
            timeout=timeout,
            poll_interval=poll_interval,
            show_progress=show_progress
        )

    async def _refresh(self) -> None:
        """Refresh this pipeline from the API."""
        fresh_data = await self._client._request(
            method="GET",
            path=f"/pipelines/{self.pipeline_id}",
            cast_type=dict,
        )
        self._data = fresh_data

    def __repr__(self) -> str:
        return f"PipelineAsyncModel(id='{self.pipeline_id}', name='{self.name}')"