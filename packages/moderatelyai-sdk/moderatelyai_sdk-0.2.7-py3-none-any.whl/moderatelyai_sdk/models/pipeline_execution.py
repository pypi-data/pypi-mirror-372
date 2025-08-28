"""Pipeline execution model for the Moderately AI SDK."""

import time
from typing import Any, Dict, Optional

from .._base_client import BaseClient
from ..types import PipelineExecution
from ._base import BaseModel


class PipelineExecutionModel(BaseModel):
    """Rich pipeline execution model with convenient methods for execution management.

    Provides an object-oriented interface for working with pipeline executions,
    including monitoring status, cancelling executions, and retrieving results.

    Examples:
        ```python
        # Get execution and check status
        execution = client.pipeline_executions.retrieve("execution_123")
        if execution.is_completed:
            results = execution.get_output()
            print(f"Results: {results}")
        elif execution.is_running:
            print("Execution is still running...")
            execution = execution.wait_for_completion(timeout=300)
        ```
    """

    def __init__(self, data: PipelineExecution, client: BaseClient) -> None:
        super().__init__(data, client)

    @property
    def execution_id(self) -> str:
        """The unique identifier for this execution."""
        return self._data["pipelineExecutionId"]

    @property
    def configuration_version_id(self) -> str:
        """The configuration version ID used for this execution."""
        return self._data["pipelineConfigurationVersionId"]

    @property
    def pipeline_input(self) -> Dict[str, Any]:
        """The input data provided to this execution."""
        return self._data["pipelineInput"]

    @property
    def pipeline_input_summary(self) -> str:
        """Human-readable summary of the input."""
        return self._data["pipelineInputSummary"]

    @property
    def pipeline_output(self) -> Optional[Dict[str, Any]]:
        """The output data from this execution (if completed)."""
        return self._data.get("pipelineOutput")

    @property
    def pipeline_output_summary(self) -> Optional[str]:
        """Human-readable summary of the output."""
        return self._data.get("pipelineOutputSummary")

    @property
    def status(self) -> str:
        """Current execution status."""
        return self._data["status"]

    @property
    def progress_data(self) -> Dict[str, Any]:
        """Progress tracking data for the execution."""
        return self._data.get("progressData", {})

    @property
    def current_step(self) -> Optional[int]:
        """Current step in the pipeline execution."""
        return self._data.get("currentStep")

    @property
    def total_steps(self) -> Optional[int]:
        """Total number of steps in the pipeline."""
        return self._data.get("totalSteps")

    @property
    def created_at(self) -> Optional[str]:
        """When the execution was created."""
        return self._data.get("createdAt")

    @property
    def started_at(self) -> Optional[str]:
        """When the execution started."""
        return self._data.get("startedAt")

    @property
    def completed_at(self) -> Optional[str]:
        """When the execution completed."""
        return self._data.get("completedAt")

    @property
    def failed_at(self) -> Optional[str]:
        """When the execution failed."""
        return self._data.get("failedAt")

    @property
    def cancelled_at(self) -> Optional[str]:
        """When the execution was cancelled."""
        return self._data.get("cancelledAt")

    @property
    def is_pending(self) -> bool:
        """True if execution is pending."""
        return self.status == "pending"

    @property
    def is_running(self) -> bool:
        """True if execution is currently running."""
        return self.status == "running"

    @property
    def is_completed(self) -> bool:
        """True if execution completed successfully."""
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        """True if execution failed."""
        return self.status == "failed"

    @property
    def is_cancelled(self) -> bool:
        """True if execution was cancelled."""
        return self.status == "cancelled"

    @property
    def is_paused(self) -> bool:
        """True if execution is paused."""
        return self.status == "paused"

    @property
    def is_terminal(self) -> bool:
        """True if execution is in a terminal state (completed, failed, or cancelled)."""
        return self.status in ("completed", "failed", "cancelled")

    @property
    def progress_percentage(self) -> Optional[float]:
        """Progress as a percentage (0.0 to 100.0) if steps are available."""
        if self.current_step is not None and self.total_steps is not None and self.total_steps > 0:
            return (self.current_step / self.total_steps) * 100.0
        return None

    def refresh(self) -> "PipelineExecutionModel":
        """Refresh execution status from the API.

        Returns:
            Updated execution model instance.
        """
        updated_data = self._client._request(
            method="GET",
            path=f"/pipeline-executions/{self.execution_id}",
            cast_type=dict,
        )
        return PipelineExecutionModel(updated_data, self._client)

    def cancel(self, *, reason: Optional[str] = None) -> "PipelineExecutionModel":
        """Cancel this execution.

        Args:
            reason: Optional reason for cancelling the execution.

        Returns:
            Updated execution model instance.

        Raises:
            ValidationError: If the execution cannot be cancelled.
        """
        body = {}
        if reason is not None:
            body["reason"] = reason

        updated_data = self._client._request(
            method="POST",
            path=f"/pipeline-executions/{self.execution_id}/cancel",
            cast_type=dict,
            body=body
        )
        return PipelineExecutionModel(updated_data, self._client)

    def get_output(self) -> Any:
        """Get the output of this execution.

        Handles both inline and S3-stored outputs automatically:
        - Inline: Small outputs stored directly in the API response
        - S3: Large outputs stored in S3 with automatic download via presigned URL

        Returns:
            The execution output data or None if not available.

        Raises:
            NotFoundError: If the execution doesn't exist or has no output.
        """
        import json
        import urllib.request

        result = self._client._request(
            method="GET",
            path=f"/pipeline-executions/{self.execution_id}/output",
            cast_type=dict,
        )

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

    def wait_for_completion(
        self,
        *,
        timeout: Optional[int] = None,
        poll_interval: float = 2.0,
        show_progress: bool = True
    ) -> "PipelineExecutionModel":
        """Wait for this execution to complete with progress tracking.

        Based on the polling pattern from the demo script, this method:
        - Polls execution status at regular intervals
        - Shows progress updates (steps, percentage, messages)
        - Handles terminal states (completed, failed, cancelled)
        - Provides timeout support with meaningful errors

        Args:
            timeout: Maximum time to wait in seconds.
            poll_interval: How often to poll for status updates in seconds.
            show_progress: Whether to print progress updates to console.

        Returns:
            Updated execution model instance when complete.

        Raises:
            TimeoutError: If execution doesn't complete within timeout.
            Exception: If execution fails or is cancelled.
        """
        if show_progress:
            print("⏳ Waiting for pipeline to complete...")

        start_time = time.time()
        last_step = -1
        last_progress_msg = ""

        while True:
            time.sleep(poll_interval)

            # Get current execution status
            updated_execution = self.refresh()
            status = updated_execution.status
            current_step = updated_execution.current_step or 0
            total_steps = updated_execution.total_steps or 0
            progress_data = updated_execution.progress_data

            # Calculate progress percentage
            progress_pct = 0
            if total_steps > 0:
                progress_pct = (current_step / total_steps) * 100

            # Extract progress message from various possible fields
            progress_msg = ""
            if progress_data:
                if "message" in progress_data:
                    progress_msg = progress_data["message"]
                elif "status" in progress_data:
                    progress_msg = progress_data["status"]
                elif "current_block" in progress_data:
                    progress_msg = f"Processing {progress_data['current_block']}"

            # Show progress update if something changed
            if show_progress and (current_step != last_step or progress_msg != last_progress_msg):
                if total_steps > 0:
                    print(f"\n   📊 Progress: Step {current_step}/{total_steps} ({progress_pct:.1f}%)")
                else:
                    print(f"\n   📊 Status: {status}")

                if progress_msg:
                    print(f"   📝 {progress_msg}")

                last_step = current_step
                last_progress_msg = progress_msg
            elif show_progress:
                # Show activity indicator
                print(".", end="", flush=True)

            # Check terminal states
            if status == "completed":
                if show_progress:
                    print("\n   ✅ Pipeline completed successfully!")
                return updated_execution
            elif status == "failed":
                if show_progress:
                    print("\n   ❌ Pipeline failed!")
                # Extract error details
                error_msg = progress_data.get('error', 'Unknown error')
                if 'errors' in progress_data:
                    error_msg = "; ".join(progress_data['errors'])
                raise Exception(f"Pipeline execution failed: {error_msg}")
            elif status == "cancelled":
                if show_progress:
                    print("\n   ⚫ Pipeline cancelled!")
                raise Exception("Pipeline execution was cancelled")

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(
                    f"Pipeline execution did not complete within {timeout} seconds. "
                    f"Current status: {status}"
                )

    def __repr__(self) -> str:
        progress = f", progress={self.progress_percentage:.1f}%" if self.progress_percentage is not None else ""
        return f"PipelineExecutionModel(id='{self.execution_id}', status='{self.status}'{progress})"
