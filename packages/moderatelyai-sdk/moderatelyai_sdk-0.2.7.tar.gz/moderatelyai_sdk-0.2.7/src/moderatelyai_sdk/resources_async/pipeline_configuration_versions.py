"""Async Pipeline Configuration Versions resource for the Moderately AI API."""

from typing import Any, Dict, List, Optional

from ..models.pipeline_configuration_version_async import PipelineConfigurationVersionAsyncModel
from ..types import PaginatedResponse
from ._base import AsyncBaseResource


class AsyncPipelineConfigurationVersions(AsyncBaseResource):
    """Manage pipeline configuration versions (async version).

    Configuration versions contain the actual pipeline logic - the blocks, connections,
    and workflow definition. Each pipeline can have multiple configuration versions
    to track changes over time.

    Examples:
        ```python
        # List configuration versions
        versions = await client.pipeline_configuration_versions.list()

        # Get a specific version
        version = await client.pipeline_configuration_versions.retrieve("version_123")

        # Create a new configuration version
        version = await client.pipeline_configuration_versions.create(
            pipeline_id="pipeline_123",
            configuration={
                "id": "my-pipeline",
                "name": "Document Processor",
                "version": "1.0.0",
                "blocks": {
                    "input": {
                        "id": "input",
                        "type": "input",
                        "config": {"json_schema": {"type": "object"}}
                    }
                }
            }
        )

        # Update a configuration version
        version = await client.pipeline_configuration_versions.update(
            "version_123",
            configuration=updated_config
        )

        # Clone a configuration version
        new_version = await client.pipeline_configuration_versions.clone("version_123")

        # Validate a configuration
        validation = await client.pipeline_configuration_versions.validate(configuration)

        # Get the configuration schema
        schema = await client.pipeline_configuration_versions.get_schema()

        # Delete a configuration version
        await client.pipeline_configuration_versions.delete("version_123")
        ```
    """

    async def list(
        self,
        *,
        pipeline_ids: Optional[List[str]] = None,
        pipeline_configuration_version_ids: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: Optional[str] = None,
        order_direction: str = "asc",
    ) -> PaginatedResponse:
        """List pipeline configuration versions with pagination (async).

        Args:
            pipeline_ids: Filter by specific pipeline IDs.
            pipeline_configuration_version_ids: Filter by specific version IDs.
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page (1-1000). Defaults to 10.
            order_by: Field to sort by ("createdAt", "updatedAt").
            order_direction: Sort direction ("asc" or "desc"). Defaults to "asc".

        Returns:
            Paginated list of configuration versions.
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
        if order_by is not None:
            query["orderBy"] = order_by

        response = await self._get("/pipeline-configuration-versions", options={"query": query})

        # Convert configuration version items to rich async models
        if "items" in response:
            response["items"] = [
                PipelineConfigurationVersionAsyncModel(item, self._client) for item in response["items"]
            ]

        return response

    async def retrieve(self, pipeline_configuration_version_id: str) -> PipelineConfigurationVersionAsyncModel:
        """Retrieve a specific configuration version by ID (async).

        Args:
            pipeline_configuration_version_id: The ID of the version to retrieve.

        Returns:
            The configuration version data.

        Raises:
            NotFoundError: If the version doesn't exist.
        """
        version_data = await self._get(f"/pipeline-configuration-versions/{pipeline_configuration_version_id}")
        return PipelineConfigurationVersionAsyncModel(version_data, self._client)

    async def create(
        self,
        *,
        pipeline_id: str,
        configuration: Dict[str, Any],
        **kwargs,
    ) -> PipelineConfigurationVersionAsyncModel:
        """Create a new pipeline configuration version (async).

        Args:
            pipeline_id: The ID of the pipeline this version belongs to.
            configuration: The pipeline configuration object with blocks and connections.
            **kwargs: Additional version properties.

        Returns:
            The created configuration version data.

        Raises:
            ValidationError: If the configuration is invalid.
            NotFoundError: If the pipeline doesn't exist.
        """
        body = {
            "pipelineId": pipeline_id,
            "configuration": configuration,
            **kwargs,
        }

        version_data = await self._post("/pipeline-configuration-versions", body=body)
        return PipelineConfigurationVersionAsyncModel(version_data, self._client)

    async def update(
        self,
        pipeline_configuration_version_id: str,
        *,
        configuration: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> PipelineConfigurationVersionAsyncModel:
        """Update an existing configuration version (async).

        Args:
            pipeline_configuration_version_id: The ID of the version to update.
            configuration: New configuration object.
            **kwargs: Additional properties to update.

        Returns:
            The updated configuration version data.

        Raises:
            NotFoundError: If the version doesn't exist.
            ValidationError: If the configuration is invalid.
        """
        body = {**kwargs}
        if configuration is not None:
            body["configuration"] = configuration

        version_data = await self._patch(f"/pipeline-configuration-versions/{pipeline_configuration_version_id}", body=body)
        return PipelineConfigurationVersionAsyncModel(version_data, self._client)

    async def delete(self, pipeline_configuration_version_id: str) -> None:
        """Delete a configuration version (async).

        Args:
            pipeline_configuration_version_id: The ID of the version to delete.

        Raises:
            NotFoundError: If the version doesn't exist.
        """
        await self._delete(f"/pipeline-configuration-versions/{pipeline_configuration_version_id}")

    async def clone(self, pipeline_configuration_version_id: str) -> PipelineConfigurationVersionAsyncModel:
        """Clone an existing configuration version (async).

        Creates a new version by copying an existing one. The cloned version will have
        a new ID, incremented version number, and draft status.

        Args:
            pipeline_configuration_version_id: The ID of the version to clone.

        Returns:
            The newly created configuration version.

        Raises:
            NotFoundError: If the version doesn't exist.
        """
        version_data = await self._post(f"/pipeline-configuration-versions/{pipeline_configuration_version_id}/clone")
        return PipelineConfigurationVersionAsyncModel(version_data, self._client)

    async def validate(self, *, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a pipeline configuration (async).

        Validates the configuration against the JSON Schema and business logic rules
        without creating a version.

        Args:
            configuration: The pipeline configuration to validate.

        Returns:
            Validation results with valid flag, errors, warnings, and schemas.
        """
        body = {"configuration": configuration}
        return await self._post("/pipeline-configuration-versions/validate", body=body)

    async def get_schema(self) -> Optional[Dict[str, Any]]:
        """Get the JSON Schema for pipeline configurations (async).

        Returns:
            The JSON Schema definition for pipeline configurations.
        """
        return await self._get("/pipeline-configuration-versions/schema")
