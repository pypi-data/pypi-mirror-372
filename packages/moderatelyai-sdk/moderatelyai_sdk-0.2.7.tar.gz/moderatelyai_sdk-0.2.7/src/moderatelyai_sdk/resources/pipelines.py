"""Pipelines resource for the Moderately AI API."""

from typing import List, Optional

from ..models.pipeline import PipelineModel
from ..types import PaginatedResponse
from ._base import BaseResource


class Pipelines(BaseResource):
    """Manage pipelines in your teams.

    Pipelines are basic metadata containers with name, description, and team ownership.
    The actual pipeline logic is stored in PipelineConfigurationVersions.
    Execution instances are managed through PipelineExecutions.

    Examples:
        ```python
        # List all pipelines
        pipelines = client.pipelines.list()

        # Get a specific pipeline
        pipeline = client.pipelines.retrieve("pipeline_123")

        # Create a new pipeline
        pipeline = client.pipelines.create(
            name="Document Analysis Pipeline",
            description="Processes legal documents"
        )

        # Update a pipeline
        pipeline = client.pipelines.update(
            "pipeline_123",
            name="Updated Pipeline Name"
        )

        # Delete a pipeline
        client.pipelines.delete("pipeline_123")
        ```
    """

    def list(
        self,
        *,
        pipeline_ids: Optional[List[str]] = None,
        name_like: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[str] = None,
        order_direction: str = "asc",
    ) -> PaginatedResponse:
        """List all pipelines with pagination.

        Note: Results are automatically filtered to the team specified in the client.

        Args:
            pipeline_ids: Filter by specific pipeline IDs.
            name_like: Filter pipelines by name (case-insensitive partial match).
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page (1-1000). Defaults to 10.
            order_by: Field to sort by ("name", "createdAt", "updatedAt").
            order_direction: Sort direction ("asc" or "desc"). Defaults to "asc".

        Returns:
            Paginated list of pipelines for the client's team.
        """
        query = {
            "page": page,
            "pageSize": page_size,
            "orderDirection": order_direction,
        }

        if pipeline_ids is not None:
            query["pipelineIds"] = ",".join(pipeline_ids)
        if name_like is not None:
            query["nameLike"] = name_like
        if order_by is not None:
            query["orderBy"] = order_by

        response = self._get("/pipelines", options={"query": query})

        # Convert pipeline items to fat models
        if "items" in response:
            response["items"] = [
                PipelineModel(item, self._client) for item in response["items"]
            ]

        return response

    def retrieve(self, pipeline_id: str) -> PipelineModel:
        """Retrieve a specific pipeline by ID.

        Args:
            pipeline_id: The ID of the pipeline to retrieve.

        Returns:
            The pipeline model instance.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
        """
        pipeline_data = self._get(f"/pipelines/{pipeline_id}")
        return PipelineModel(pipeline_data, self._client)

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> PipelineModel:
        """Create a new pipeline.

        Note: The pipeline will be created in the team specified in the client.

        Args:
            name: The pipeline's name (1-255 characters). Must be unique within the team.
            description: The pipeline's description (max 1000 characters).
            **kwargs: Additional pipeline properties.

        Returns:
            The created pipeline model instance.

        Raises:
            ValidationError: If the request data is invalid.
            ConflictError: If a pipeline with the same name already exists in the team.
        """
        body = {
            "teamId": self._client.team_id,
            "name": name,
            **kwargs,
        }
        if description is not None:
            body["description"] = description

        pipeline_data = self._post("/pipelines", body=body)
        return PipelineModel(pipeline_data, self._client)

    def update(
        self,
        pipeline_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs,
    ) -> PipelineModel:
        """Update an existing pipeline.

        Args:
            pipeline_id: The ID of the pipeline to update.
            name: New pipeline name (1-255 characters). Must be unique within the team.
            description: New pipeline description (max 1000 characters).
            **kwargs: Additional properties to update.

        Returns:
            The updated pipeline model instance.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
            ValidationError: If the request data is invalid.
            ConflictError: If a pipeline with the same name already exists in the team.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description

        pipeline_data = self._patch(f"/pipelines/{pipeline_id}", body=body)
        return PipelineModel(pipeline_data, self._client)

    def delete(self, pipeline_id: str) -> None:
        """Delete a pipeline.

        Args:
            pipeline_id: The ID of the pipeline to delete.

        Raises:
            NotFoundError: If the pipeline doesn't exist.
        """
        self._delete(f"/pipelines/{pipeline_id}")
