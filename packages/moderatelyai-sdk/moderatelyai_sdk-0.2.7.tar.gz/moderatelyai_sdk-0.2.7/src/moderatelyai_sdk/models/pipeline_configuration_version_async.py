"""Async pipeline configuration version model for the Moderately AI SDK."""

from typing import Any, Dict, List, Optional

from .._base_client_async import AsyncBaseClient
from ..types import PipelineConfigurationVersion
from ._base_async import BaseAsyncModel


class PipelineConfigurationVersionAsyncModel(BaseAsyncModel):
    """Rich async pipeline configuration version model with convenient methods.

    Provides an object-oriented interface for working with pipeline configuration
    versions asynchronously, including updating configurations, validation, cloning, and execution.

    Examples:
        ```python
        # Get configuration version and execute it
        config_version = await client.pipeline_configuration_versions.retrieve("version_123")
        execution = await config_version.execute(
            pipeline_input={"documents": ["doc1.pdf"]},
            pipeline_input_summary="Process document"
        )

        # Clone and modify a configuration
        new_version = await config_version.clone()
        updated_config = new_version.configuration.copy()
        updated_config["blocks"]["llm"]["config"]["temperature"] = 0.5
        new_version = await new_version.update(configuration=updated_config)
        ```
    """

    def __init__(self, data: PipelineConfigurationVersion, client: AsyncBaseClient) -> None:
        super().__init__(data, client)

    @property
    def configuration_version_id(self) -> str:
        """The unique identifier for this configuration version."""
        return self._data["pipelineConfigurationVersionId"]

    @property
    def pipeline_id(self) -> str:
        """The pipeline ID this configuration version belongs to."""
        return self._data["pipelineId"]

    @property
    def configuration(self) -> Dict[str, Any]:
        """The pipeline configuration object (blocks, connections, etc.)."""
        return self._data["configuration"]

    @property
    def created_at(self) -> Optional[str]:
        """When the configuration version was created."""
        return self._data.get("createdAt")

    @property
    def updated_at(self) -> Optional[str]:
        """When the configuration version was last updated."""
        return self._data.get("updatedAt")

    @property
    def status(self) -> Optional[str]:
        """The status of this configuration version."""
        return self._data.get("status")

    @property
    def version(self) -> Optional[str]:
        """The version string for this configuration."""
        return self._data.get("version")

    async def update(
        self,
        *,
        configuration: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "PipelineConfigurationVersionAsyncModel":
        """Update this configuration version and return the updated instance (async).

        Args:
            configuration: New configuration object.
            **kwargs: Additional properties to update.

        Returns:
            Updated async configuration version model instance.
        """
        body = {**kwargs}
        if configuration is not None:
            body["configuration"] = configuration

        updated_data = await self._client._request(
            method="PATCH",
            path=f"/pipeline-configuration-versions/{self.configuration_version_id}",
            cast_type=dict,
            body=body
        )
        return PipelineConfigurationVersionAsyncModel(updated_data, self._client)

    async def delete(self) -> None:
        """Delete this configuration version (async).

        Warning: This will permanently delete the configuration version.
        Any executions using this version will still retain their results.
        """
        await self._client._request(
            method="DELETE",
            path=f"/pipeline-configuration-versions/{self.configuration_version_id}",
            cast_type=dict,
        )

    async def clone(self) -> "PipelineConfigurationVersionAsyncModel":
        """Clone this configuration version (async).

        Creates a new configuration version by copying this one. The cloned
        version will have a new ID, incremented version number, and draft status.

        Returns:
            Newly created async configuration version model.
        """
        cloned_data = await self._client._request(
            method="POST",
            path=f"/pipeline-configuration-versions/{self.configuration_version_id}/clone",
            cast_type=dict,
            body={}
        )
        return PipelineConfigurationVersionAsyncModel(cloned_data, self._client)

    async def validate(self) -> Dict[str, Any]:
        """Validate this configuration version (async).

        Validates the configuration against the JSON Schema and business logic
        rules without creating a new version.

        Returns:
            Validation results with valid flag, errors, warnings, and schemas.
        """
        return await self._client._request(
            method="POST",
            path="/pipeline-configuration-versions/validate",
            cast_type=dict,
            body={"configuration": self.configuration}
        )

    async def execute(
        self,
        *,
        pipeline_input: Dict[str, Any],
        pipeline_input_summary: str,
        block: bool = False,
        timeout: Optional[int] = None,
        poll_interval: float = 2.0,
        show_progress: bool = True,
        **kwargs
    ):
        """Execute this configuration version (async).

        This is a convenience method that creates a pipeline execution using
        this configuration version.

        Args:
            pipeline_input: Input data for the pipeline execution.
            pipeline_input_summary: Human-readable summary of the input.
            block: If True, wait for execution to complete before returning.
            timeout: Maximum time to wait in seconds (only used with block=True).
            poll_interval: How often to poll for status updates in seconds.
            show_progress: Whether to show progress updates during blocking execution.
            **kwargs: Additional execution properties.

        Returns:
            Async pipeline execution model. If block=False, returns immediately.
            If block=True, returns when execution completes.

        Examples:
            ```python
            # Non-blocking execution
            execution = await config_version.execute(
                pipeline_input={"documents": ["doc1.pdf"]},
                pipeline_input_summary="Process document"
            )

            # Blocking execution with timeout
            execution = await config_version.execute(
                pipeline_input={"documents": ["doc1.pdf"]},
                pipeline_input_summary="Process document",
                block=True,
                timeout=300
            )
            ```
        """
        from .pipeline_execution_async import PipelineExecutionAsyncModel

        # Create the execution
        execution_data = await self._client._request(
            method="POST",
            path="/pipeline-executions",
            cast_type=dict,
            body={
                "pipelineConfigurationVersionId": self.configuration_version_id,
                "pipelineInput": pipeline_input,
                "pipelineInputSummary": pipeline_input_summary,
                **kwargs
            }
        )

        execution = PipelineExecutionAsyncModel(execution_data, self._client)

        # If not blocking, return immediately
        if not block:
            return execution

        # Block and poll until completion
        return await execution.wait_for_completion(
            timeout=timeout,
            poll_interval=poll_interval,
            show_progress=show_progress
        )

    async def list_executions(
        self,
        *,
        status: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10
    ):
        """Get executions that used this configuration version (async).

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
            "pipelineConfigurationVersionIds": self.configuration_version_id,
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

    async def get_pipeline(self):
        """Get the parent pipeline for this configuration version (async).

        Returns:
            Async pipeline model instance.
        """
        from .pipeline_async import PipelineAsyncModel

        pipeline_data = await self._client._request(
            method="GET",
            path=f"/pipelines/{self.pipeline_id}",
            cast_type=dict,
        )
        return PipelineAsyncModel(pipeline_data, self._client)

    async def get_latest_execution(self):
        """Get the most recent execution using this configuration version (async).

        Returns:
            Latest async execution model or None if no executions exist.
        """
        executions = await self.list_executions(page_size=1)
        return executions[0] if executions else None

    async def _refresh(self) -> None:
        """Refresh this configuration version from the API."""
        fresh_data = await self._client._request(
            method="GET",
            path=f"/pipeline-configuration-versions/{self.configuration_version_id}",
            cast_type=dict,
        )
        self._data = fresh_data

    def __repr__(self) -> str:
        return f"PipelineConfigurationVersionAsyncModel(id='{self.configuration_version_id}', pipeline_id='{self.pipeline_id}')"