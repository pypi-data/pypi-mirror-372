"""Dataset schema versions resource (internal use)."""

from typing import Any, Dict, List, Optional

from ..models.dataset_schema_version import DatasetSchemaVersionModel
from ._base import BaseResource


class DatasetSchemaVersions(BaseResource):
    """Internal resource for dataset schema version operations.

    This resource is not exposed in the main client - it's used internally
    by the DatasetModel to provide schema version functionality.
    """

    def list(
        self,
        *,
        dataset_ids: Optional[List[str]] = None,
        dataset_schema_version_ids: Optional[List[str]] = None,
        status: Optional[str] = None,
        version_no: Optional[int] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "createdAt",
        order_direction: str = "desc",
    ) -> List[DatasetSchemaVersionModel]:
        """List dataset schema versions.

        Args:
            dataset_ids: Filter by specific dataset IDs.
            dataset_schema_version_ids: Filter by specific schema version IDs.
            status: Filter by status ('draft', 'current', 'archived').
            version_no: Filter by version number.
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "createdAt".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            List of schema version models.
        """
        query = {
            "page": page,
            "pageSize": page_size,
            "orderBy": order_by,
            "orderDirection": order_direction,
        }

        if dataset_ids is not None:
            query["datasetIds"] = dataset_ids
        if dataset_schema_version_ids is not None:
            query["datasetSchemaVersionIds"] = dataset_schema_version_ids
        if status is not None:
            query["status"] = status
        if version_no is not None:
            query["versionNo"] = version_no

        response = self._get(
            "/dataset-schema-versions",
            options={"query": query},
        )

        # Convert response items to models
        versions = []
        for item in response.get("items", []):
            versions.append(DatasetSchemaVersionModel(item, self._client))

        return versions

    def retrieve(self, schema_version_id: str) -> DatasetSchemaVersionModel:
        """Retrieve a specific schema version by ID.

        Args:
            schema_version_id: The ID of the schema version to retrieve.

        Returns:
            The schema version model.

        Raises:
            NotFoundError: If the schema version doesn't exist.
        """
        data = self._get(f"/dataset-schema-versions/{schema_version_id}")
        return DatasetSchemaVersionModel(data, self._client)

    def create(
        self,
        *,
        dataset_id: str,
        columns: List[Dict[str, Any]],
        status: str = "draft",
        parsing_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> DatasetSchemaVersionModel:
        """Create a new schema version.

        Args:
            dataset_id: The ID of the dataset.
            columns: List of column definitions.
            status: Initial status. Defaults to "draft".
            parsing_options: Optional parsing configuration.
            **kwargs: Additional properties.

        Returns:
            The created schema version model.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "datasetId": dataset_id,
            "columns": columns,
            "status": status,
            **kwargs,
        }

        if parsing_options is not None:
            body["parsingOptions"] = parsing_options

        data = self._post("/dataset-schema-versions", body=body)
        return DatasetSchemaVersionModel(data, self._client)

    def update(
        self,
        schema_version_id: str,
        *,
        status: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        parsing_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> DatasetSchemaVersionModel:
        """Update an existing schema version.

        Args:
            schema_version_id: The ID of the schema version to update.
            status: New status.
            columns: Updated column definitions.
            parsing_options: Updated parsing options.
            **kwargs: Additional properties to update.

        Returns:
            The updated schema version model.

        Raises:
            NotFoundError: If the schema version doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if status is not None:
            body["status"] = status
        if columns is not None:
            body["columns"] = columns  # API expects 'columns', not 'columnsJson'
        if parsing_options is not None:
            body["parsingOptions"] = parsing_options

        data = self._patch(f"/dataset-schema-versions/{schema_version_id}", body=body)
        return DatasetSchemaVersionModel(data, self._client)
