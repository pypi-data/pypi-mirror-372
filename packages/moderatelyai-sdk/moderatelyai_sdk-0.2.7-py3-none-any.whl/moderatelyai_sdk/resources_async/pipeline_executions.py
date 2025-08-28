"""Async Pipeline Executions resource for the Moderately AI API."""

from typing import Any, Dict, List, Optional

from ..models.pipeline_execution_async import PipelineExecutionAsyncModel
from ..types import PaginatedResponse
from ._base import AsyncBaseResource


class AsyncPipelineExecutions(AsyncBaseResource):
    """Manage pipeline executions (async version).

    Pipeline executions are runtime instances that process input data through
    a specific pipeline configuration version. They track status, progress,
    and output data.

    Examples:
        ```python
        # List executions
        executions = await client.pipeline_executions.list()

        # Get a specific execution
        execution = await client.pipeline_executions.retrieve("execution_123")

        # Create a new execution
        execution = await client.pipeline_executions.create(
            pipeline_configuration_version_id="version_123",
            pipeline_input={"documents": ["doc1.pdf", "doc2.pdf"]},
            pipeline_input_summary="Process 2 legal documents"
        )

        # Update execution status/output
        execution = await client.pipeline_executions.update(
            "execution_123",
            status="completed",
            pipeline_output={"results": "..."},
            pipeline_output_summary="Successfully processed 2 documents"
        )

        # Cancel a running execution
        execution = await client.pipeline_executions.cancel("execution_123")

        # Get execution output
        output = await client.pipeline_executions.get_output("execution_123")
        ```
    """

    async def list(
        self,
        *,
        pipeline_ids: Optional[List[str]] = None,
        pipeline_configuration_version_ids: Optional[List[str]] = None,
        pipeline_execution_ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        statuses: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[str] = None,
        order_direction: str = "asc",
    ) -> PaginatedResponse:
        """List pipeline executions with pagination (async).

        Args:
            pipeline_ids: Filter by pipeline IDs (requires join through config versions).
            pipeline_configuration_version_ids: Filter by config version IDs.
            pipeline_execution_ids: Filter by specific execution IDs.
            status: Filter by single execution status.
            statuses: Filter by multiple execution statuses.
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page (1-1000). Defaults to 10.
            order_by: Field to sort by ("createdAt", "updatedAt", "startedAt").
            order_direction: Sort direction ("asc" or "desc"). Defaults to "asc".

        Returns:
            Paginated list of pipeline executions.
        """
        query = {
            "page": page,
            "pageSize": page_size,
            "orderDirection": order_direction,
        }

        if pipeline_ids is not None:
            query["pipelineIds"] = ",".join(pipeline_ids)
        if pipeline_configuration_version_ids is not None:
            query["pipelineConfigurationVersionIds"] = ",".join(pipeline_configuration_version_ids)
        if pipeline_execution_ids is not None:
            query["pipelineExecutionIds"] = ",".join(pipeline_execution_ids)
        if status is not None:
            query["status"] = status
        if statuses is not None:
            query["statuses"] = ",".join(statuses)
        if order_by is not None:
            query["orderBy"] = order_by

        response = await self._get("/pipeline-executions", options={"query": query})

        # Convert execution items to rich async models
        if "items" in response:
            response["items"] = [
                PipelineExecutionAsyncModel(item, self._client) for item in response["items"]
            ]

        return response

    async def retrieve(self, pipeline_execution_id: str) -> PipelineExecutionAsyncModel:
        """Retrieve a specific pipeline execution by ID (async).

        Args:
            pipeline_execution_id: The ID of the execution to retrieve.

        Returns:
            The pipeline execution data.

        Raises:
            NotFoundError: If the execution doesn't exist.
        """
        execution_data = await self._get(f"/pipeline-executions/{pipeline_execution_id}")
        return PipelineExecutionAsyncModel(execution_data, self._client)

    async def create(
        self,
        *,
        pipeline_configuration_version_id: str,
        pipeline_input: Dict[str, Any],
        pipeline_input_summary: str,
        current_step: Optional[int] = None,
        total_steps: Optional[int] = None,
        **kwargs,
    ) -> PipelineExecutionAsyncModel:
        """Create a new pipeline execution (async).

        Args:
            pipeline_configuration_version_id: The ID of the config version to execute.
            pipeline_input: The input data for the pipeline execution.
            pipeline_input_summary: Human-readable summary of the input (max 1000 chars).
            current_step: The current step in the pipeline execution (0-indexed).
            total_steps: The total number of steps in the pipeline.
            **kwargs: Additional execution properties.

        Returns:
            The created pipeline execution data.

        Raises:
            ValidationError: If the input data is invalid.
            NotFoundError: If the config version doesn't exist.
        """
        body = {
            "pipelineConfigurationVersionId": pipeline_configuration_version_id,
            "pipelineInput": pipeline_input,
            "pipelineInputSummary": pipeline_input_summary,
            **kwargs,
        }

        if current_step is not None:
            body["currentStep"] = current_step
        if total_steps is not None:
            body["totalSteps"] = total_steps

        execution_data = await self._post("/pipeline-executions", body=body)
        return PipelineExecutionAsyncModel(execution_data, self._client)

    async def update(
        self,
        pipeline_execution_id: str,
        *,
        pipeline_output: Optional[Dict[str, Any]] = None,
        pipeline_output_summary: Optional[str] = None,
        status: Optional[str] = None,
        progress_data: Optional[Dict[str, Any]] = None,
        current_step: Optional[int] = None,
        total_steps: Optional[int] = None,
        started_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        failed_at: Optional[str] = None,
        cancelled_at: Optional[str] = None,
        paused_at: Optional[str] = None,
        **kwargs,
    ) -> PipelineExecutionAsyncModel:
        """Update an existing pipeline execution (async).

        Used by workers to report execution progress and results.

        Args:
            pipeline_execution_id: The ID of the execution to update.
            pipeline_output: The output data from the pipeline execution.
            pipeline_output_summary: Human-readable summary of the output (max 1000 chars).
            status: The execution status (pending, running, completed, failed, cancelled, paused).
            progress_data: Progress tracking data for the execution.
            current_step: The current step in the pipeline execution.
            total_steps: The total number of steps in the pipeline.
            started_at: When the execution started.
            completed_at: When the execution completed.
            failed_at: When the execution failed.
            cancelled_at: When the execution was cancelled.
            paused_at: When the execution was paused.
            **kwargs: Additional properties to update.

        Returns:
            The updated pipeline execution data.

        Raises:
            NotFoundError: If the execution doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}

        if pipeline_output is not None:
            body["pipelineOutput"] = pipeline_output
        if pipeline_output_summary is not None:
            body["pipelineOutputSummary"] = pipeline_output_summary
        if status is not None:
            body["status"] = status
        if progress_data is not None:
            body["progressData"] = progress_data
        if current_step is not None:
            body["currentStep"] = current_step
        if total_steps is not None:
            body["totalSteps"] = total_steps
        if started_at is not None:
            body["startedAt"] = started_at
        if completed_at is not None:
            body["completedAt"] = completed_at
        if failed_at is not None:
            body["failedAt"] = failed_at
        if cancelled_at is not None:
            body["cancelledAt"] = cancelled_at
        if paused_at is not None:
            body["pausedAt"] = paused_at

        execution_data = await self._patch(f"/pipeline-executions/{pipeline_execution_id}", body=body)
        return PipelineExecutionAsyncModel(execution_data, self._client)

    async def cancel(
        self,
        pipeline_execution_id: str,
        *,
        reason: Optional[str] = None,
    ) -> PipelineExecutionAsyncModel:
        """Cancel a running or pending pipeline execution (async).

        Only non-terminal executions can be cancelled.

        Args:
            pipeline_execution_id: The ID of the execution to cancel.
            reason: Optional reason for cancelling the execution (max 500 chars).

        Returns:
            The updated execution with cancelled status.

        Raises:
            NotFoundError: If the execution doesn't exist.
            ValidationError: If the execution cannot be cancelled.
        """
        body = {}
        if reason is not None:
            body["reason"] = reason

        execution_data = await self._post(f"/pipeline-executions/{pipeline_execution_id}/cancel", body=body)
        return PipelineExecutionAsyncModel(execution_data, self._client)

    async def get_output(self, pipeline_execution_id: str) -> Any:
        """Get the output of a specific pipeline execution (async).

        Handles both inline and S3-stored outputs automatically:
        - Inline: Small outputs stored directly in the API response
        - S3: Large outputs stored in S3 with automatic download via presigned URL

        Args:
            pipeline_execution_id: The ID of the execution.

        Returns:
            The execution output data or None if not available.

        Raises:
            NotFoundError: If the execution doesn't exist or has no output.
        """
        import json
        import urllib.request

        result = await self._get(f"/pipeline-executions/{pipeline_execution_id}/output")

        if result.get('type') == 'inline':
            # Output is stored inline in the response
            return result.get('data', {})
        elif result.get('type') == 's3':
            # Output is in S3, need to download from presigned URL
            download_url = result.get('downloadUrl')
            if not download_url:
                return None

            # Download from presigned S3 URL
            request = urllib.request.Request(download_url)
            with urllib.request.urlopen(request) as response:
                content = response.read()

                # Check if content is compressed
                if result.get('metadata', {}).get('compressionType') == 'gzip':
                    import gzip
                    content = gzip.decompress(content)

                # Parse JSON output
                output_data = json.loads(content.decode('utf-8'))
                return output_data
        else:
            # Unknown output type or no output
            return None
