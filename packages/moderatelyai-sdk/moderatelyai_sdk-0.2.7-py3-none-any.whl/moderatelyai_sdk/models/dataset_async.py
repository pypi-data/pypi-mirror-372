"""Async dataset models with rich functionality for data operations.

This module provides the DatasetAsyncModel and DatasetDataVersionAsyncModel classes for
working with datasets and their data versions asynchronously. These models offer rich functionality
for uploading data, creating schemas, and managing dataset versions.

Example:
    ```python
    import asyncio
    from moderatelyai_sdk import AsyncModeratelyAI

    async def main():
        async with AsyncModeratelyAI(api_key="your_key", team_id="your_team") as client:
            # Create a dataset
            dataset = await client.datasets.create(
                name="Sales Data",
                description="Monthly sales records"
            )

            # Upload data
            data_version = await dataset.upload_data("sales.csv")

            # Create a schema from sample data
            schema = await dataset.create_schema_from_sample("sales.csv")

            # Download processed data
            content = await data_version.download()

    asyncio.run(main())
    ```
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import aiofiles
import httpx

from ..exceptions import APIError
from ._base_async import BaseAsyncModel

if TYPE_CHECKING:
    from .dataset_schema_version_async import AsyncSchemaBuilder, DatasetSchemaVersionAsyncModel

from ._shared.dataset_operations import DatasetOperations


class DatasetDataVersionAsyncModel(BaseAsyncModel):
    """Async model representing a dataset data version.

    A data version represents a specific upload of data to a dataset. Each time
    you upload new data to a dataset, a new data version is created. This model
    provides access to version metadata and async download functionality.

    Attributes:
        dataset_data_version_id: Unique identifier for this data version
        dataset_id: ID of the parent dataset
        version_no: Version number (incremental)
        file_type: Type of uploaded file (csv, xlsx)
        file_hash: SHA256 hash of the uploaded file
        row_count: Number of data rows
        file_size_bytes: Size of the uploaded file
        status: Processing status (draft, current, archived)
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        ```python
        # Get the current data version
        data_version = await dataset.get_data_version("version_id")

        print(f"Version {data_version.version_no}: {data_version.file_type}")
        print(f"Rows: {data_version.row_count}, Size: {data_version.file_size_bytes}")

        # Download the data
        content = await data_version.download()
        await data_version.download(path="./local_data.csv")
        ```
    """

    @property
    def dataset_data_version_id(self) -> str:
        """The unique identifier for this data version."""
        return self._data["datasetDataVersionId"]

    @property
    def dataset_id(self) -> str:
        """The ID of the parent dataset."""
        return self._data["datasetId"]

    @property
    def version_no(self) -> int:
        """The version number (incremental)."""
        return self._data["versionNo"]

    @property
    def file_type(self) -> str:
        """The file type ('csv' or 'xlsx')."""
        return self._data["fileType"]

    @property
    def file_hash(self) -> Optional[str]:
        """The SHA256 hash of the uploaded file."""
        return self._data.get("fileHash")

    @property
    def row_count(self) -> Optional[int]:
        """The number of data rows."""
        return self._data.get("rowCount")

    @property
    def file_size_bytes(self) -> Optional[int]:
        """The size of the uploaded file in bytes."""
        return self._data.get("fileSizeBytes")

    @property
    def status(self) -> str:
        """The processing status ('draft', 'current', 'archived')."""
        return self._data["status"]

    @property
    def created_at(self) -> str:
        """When this data version was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this data version was last updated."""
        return self._data["updatedAt"]

    async def download(self, *, path: Optional[Union[str, Path]] = None) -> Optional[bytes]:
        """Download the data for this version (async).

        Args:
            path: Optional path to save the file. If provided, saves to this location.
                 If not provided, returns the file content as bytes.

        Returns:
            If path is provided: None (file is saved to disk)
            If path is not provided: The file content as bytes

        Raises:
            APIError: If download fails.
        """
        # Get download URL from API
        download_response = await self._client._request(
            method="GET",
            path=f"/dataset-data-versions/{self.dataset_data_version_id}/download",
            cast_type=dict,
        )

        download_url = download_response.get("downloadUrl")
        if not download_url:
            raise APIError("No download URL provided in API response")

        try:
            # Download the file using httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(download_url)
                response.raise_for_status()
                content = response.content

            if path:
                # Save to file asynchronously
                file_path = Path(path)
                file_path.parent.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(content)
                return None
            else:
                # Return content as bytes
                return content

        except Exception as e:
            raise APIError(f"Failed to download data version: {e}") from e

    async def _refresh(self) -> None:
        """Refresh this data version from the API."""
        fresh_data = await self._client._request(
            method="GET",
            path=f"/dataset-data-versions/{self.dataset_data_version_id}",
            cast_type=dict,
        )
        self._data = fresh_data


class DatasetAsyncModel(BaseAsyncModel):
    """Async model representing a dataset with rich functionality.

    This model wraps a dataset API response and provides rich methods for
    working with the dataset, including uploading data, creating schemas,
    and managing data versions.

    All properties return the current values from the API response. Methods
    that modify the dataset will update the internal data automatically.

    Attributes:
        dataset_id: Unique identifier for this dataset
        name: Dataset name
        description: Dataset description
        team_id: Team that owns this dataset
        record_count: Number of records in current data version
        total_size_bytes: Total size of dataset data
        current_schema_version_id: ID of current schema version
        current_data_version_id: ID of current data version
        processing_status: Data processing status
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        ```python
        # Create a dataset
        dataset = await client.datasets.create(
            name="Customer Data",
            description="Customer information and metrics"
        )

        # Upload data with automatic schema inference
        data_version = await dataset.upload_data("customers.csv")
        schema = await dataset.create_schema_from_sample("customers.csv")

        # Use schema builder for complex schemas
        schema = await (dataset.schema_builder()
            .add_column("id", "int", required=True)
            .add_column("name", "string")
            .add_column("signup_date", "datetime")
            .as_current()
            .create())

        # Access dataset information
        print(f"Dataset: {dataset.name} ({dataset.record_count} records)")

        # Download current data
        content = await dataset.download_data()
        ```
    """

    @property
    def dataset_id(self) -> str:
        """The unique identifier for this dataset."""
        return self._data["datasetId"]

    @property
    def name(self) -> str:
        """The dataset name."""
        return self._data["name"]

    @property
    def description(self) -> Optional[str]:
        """The dataset description."""
        return self._data.get("description")

    @property
    def team_id(self) -> str:
        """The team this dataset belongs to."""
        return self._data["teamId"]

    @property
    def record_count(self) -> Optional[int]:
        """Number of records in current data version."""
        return self._data.get("recordCount")

    @property
    def total_size_bytes(self) -> Optional[int]:
        """Total size in bytes."""
        return self._data.get("totalSizeBytes")

    @property
    def current_schema_version_id(self) -> Optional[str]:
        """Current schema version ID."""
        return self._data.get("currentSchemaVersionId")

    @property
    def current_data_version_id(self) -> Optional[str]:
        """Current data version ID."""
        return self._data.get("currentDataVersionId")

    @property
    def processing_status(self) -> Optional[str]:
        """Processing status: completed, failed, in_progress, needs-processing."""
        return self._data.get("processingStatus")

    @property
    def created_at(self) -> str:
        """When this dataset was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this dataset was last updated."""
        return self._data["updatedAt"]

    async def upload_data(
        self,
        file: Union[str, Path, bytes, Any],
        *,
        file_type: Optional[str] = None,
        status: str = "current",
        **kwargs: Any,
    ) -> DatasetDataVersionAsyncModel:
        """Upload data to this dataset, creating a new data version (async).

        Args:
            file: The file to upload - can be a path, bytes, or file-like object
            file_type: File type ('csv' or 'xlsx'). Auto-detected if not provided.
            status: Version status ('draft' or 'current'). Defaults to 'current'.
            **kwargs: Additional upload options.

        Returns:
            The created data version model.

        Raises:
            ValueError: If file is invalid or not found.
            APIError: If upload process fails.
        """
        # Step 1: Use shared business logic to validate and prepare file
        file_data, file_name, file_type, file_size, file_hash, row_count = DatasetOperations.validate_and_prepare_file(
            file, file_type, **kwargs
        )

        # Step 2: Create data version with upload URL
        create_body = DatasetOperations.build_create_data_version_body(
            self.dataset_id, file_name, file_type, status
        )

        create_response = await self._client._request(
            method="POST",
            path="/dataset-data-versions",
            body=create_body,
            cast_type=dict,
        )

        data_version_data = create_response["dataVersion"]
        upload_url = create_response["uploadUrl"]
        data_version_id = data_version_data["datasetDataVersionId"]

        # Step 3: Upload the file to the presigned URL (async)
        try:
            content_type = "text/csv" if file_type == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            async with httpx.AsyncClient() as client:
                upload_result = await client.put(
                    upload_url,
                    content=file_data,
                    headers={"Content-Type": content_type},
                )
                upload_result.raise_for_status()
        except Exception as e:
            raise APIError(f"Failed to upload data to presigned URL: {e}") from e

        # Step 4: Mark upload as complete
        try:
            complete_response = await self._client._request(
                method="POST",
                path=f"/dataset-data-versions/{data_version_id}/complete",
                body={
                    "fileHash": file_hash,
                    "fileSizeBytes": file_size,
                    "rowCount": row_count,
                },
                cast_type=dict,
            )

            # Return the completed data version as a model
            return DatasetDataVersionAsyncModel(complete_response, self._client)

        except Exception as e:
            raise APIError(f"Failed to complete data version upload: {e}") from e

    async def download_data(
        self,
        *,
        version_id: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
    ) -> Optional[bytes]:
        """Download data from this dataset (async).

        Args:
            version_id: Specific version to download. If not provided, downloads current version.
            path: Optional path to save the file. If provided, saves to this location.
                 If not provided, returns the file content as bytes.

        Returns:
            If path is provided: None (file is saved to disk)
            If path is not provided: The file content as bytes

        Raises:
            ValueError: If no data version exists.
            APIError: If download fails.
        """
        # Use provided version_id or fall back to current version
        target_version_id = version_id or self.current_data_version_id

        if not target_version_id:
            raise ValueError("No data version specified and dataset has no current version")

        # Create a data version model and use its download method
        version_data = {"datasetDataVersionId": target_version_id}
        version_model = DatasetDataVersionAsyncModel(version_data, self._client)

        return await version_model.download(path=path)

    async def list_data_versions(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[DatasetDataVersionAsyncModel]:
        """List data versions for this dataset (async).

        Args:
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            status: Filter by status ('draft', 'current', 'archived').

        Returns:
            List of data version models.
        """
        query = {
            "datasetIds": [self.dataset_id],
            "page": page,
            "pageSize": page_size,
        }
        if status is not None:
            query["status"] = status

        response = await self._client._request(
            method="GET",
            path="/dataset-data-versions",
            cast_type=dict,
            options={"query": query},
        )

        # Convert response items to models
        versions = []
        for item in response.get("items", []):
            versions.append(DatasetDataVersionAsyncModel(item, self._client))

        return versions

    async def get_data_version(self, version_id: str) -> DatasetDataVersionAsyncModel:
        """Get a specific data version by ID (async).

        Args:
            version_id: The ID of the data version to retrieve.

        Returns:
            The data version model.

        Raises:
            NotFoundError: If the version doesn't exist.
        """
        data = await self._client._request(
            method="GET",
            path=f"/dataset-data-versions/{version_id}",
            cast_type=dict,
        )
        return DatasetDataVersionAsyncModel(data, self._client)

    async def update(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        should_process: Optional[bool] = None,
        **kwargs: Any,
    ) -> "DatasetAsyncModel":
        """Update this dataset (async).

        Args:
            name: New dataset name.
            description: New dataset description.
            should_process: Whether to trigger data processing.
            **kwargs: Additional properties to update.

        Returns:
            Updated dataset model (self).

        Raises:
            ValidationError: If the request data is invalid.
            APIError: If update fails.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if should_process is not None:
            body["shouldProcess"] = should_process

        updated_data = await self._client._request(
            method="PATCH",
            path=f"/datasets/{self.dataset_id}",
            body=body,
            cast_type=dict,
        )

        # Update internal data
        self._data = updated_data
        return self

    async def delete(self) -> None:
        """Delete this dataset (async).

        Raises:
            APIError: If deletion fails.
        """
        await self._client._request(
            method="DELETE",
            path=f"/datasets/{self.dataset_id}",
            cast_type=dict,
        )

    async def _refresh(self) -> None:
        """Refresh this dataset from the API."""
        fresh_data = await self._client._request(
            method="GET",
            path=f"/datasets/{self.dataset_id}",
            cast_type=dict,
        )
        self._data = fresh_data

    async def create_schema(
        self,
        columns: List[Dict[str, Any]],
        *,
        status: str = "draft",
        parsing_options: Optional[Dict[str, Any]] = None,
    ) -> "DatasetSchemaVersionAsyncModel":
        """Create a schema version with simple column definitions (async).

        Args:
            columns: List of column definitions. Each dict should have:
                     - name: Column name (required)
                     - type: Column type (required) - 'string', 'int', 'float', 'datetime', 'bool'
                     - required: Whether column is required (optional, defaults to True)
                     - description: Column description (optional)
            status: Initial status ('draft' or 'current'). Defaults to 'draft'.
            parsing_options: Optional parsing configuration (delimiter, header_row, etc.)

        Returns:
            The created schema version model.

        Raises:
            ValueError: If column definitions are invalid.
            APIError: If schema creation fails.
        """
        # Convert simple column definitions to full API format (same as sync version)
        api_columns = []
        for i, col in enumerate(columns, 1):
            if "name" not in col or "type" not in col:
                raise ValueError("Each column must have 'name' and 'type' fields")

            # Convert user-friendly types to API types (same mapping as sync version)
            type_mapping = {
                "str": "string",
                "int": "integer", 
                "float": "float",
                "datetime": "datetime",
                "bool": "boolean",
                "date": "datetime",
            }
            api_type = type_mapping.get(col["type"], col["type"])

            api_column = {
                "pos": i,
                "name": col["name"],
                "type": api_type,
                "nullable": not col.get("required", True),
            }

            if "description" in col:
                api_column["description"] = col["description"]

            api_columns.append(api_column)

        # Import here to avoid circular imports
        from ..resources_async.dataset_schema_versions import AsyncDatasetSchemaVersions

        # Create using internal async resource (same pattern as sync version)
        schema_versions = AsyncDatasetSchemaVersions(self._client)
        return await schema_versions.create(
            dataset_id=self.dataset_id,
            columns=api_columns,
            status=status,
            parsing_options=parsing_options,
        )

    async def create_schema_from_sample(
        self,
        sample_file: Union[str, Path, bytes],
        *,
        status: str = "draft",
        header_row: int = 1,
        sample_size: int = 100,
    ) -> "DatasetSchemaVersionAsyncModel":
        """Create a schema by analyzing a sample data file (async).

        Args:
            sample_file: Sample data to analyze. Can be:
                        - str/Path: Path to CSV file  
                        - bytes: Raw CSV data as bytes
            status: Initial status ('draft' or 'current'). Defaults to 'draft'.
            header_row: Row containing column headers (1-based). Defaults to 1.
            sample_size: Number of rows to sample for type inference. Defaults to 100.

        Returns:
            The created schema version model.

        Raises:
            ValueError: If schema cannot be inferred.
            APIError: If schema creation fails.
        """
        # Prepare sample file
        file_data, file_name, file_type, _, _, _ = DatasetOperations.validate_and_prepare_file(
            sample_file
        )

        # Infer schema using shared logic
        inferred_columns = DatasetOperations.infer_schema_from_sample(
            file_data, file_type, sample_size
        )

        # Create schema with inferred columns
        return await self.create_schema(
            columns=inferred_columns,
            status=status,
        )

    def schema_builder(self) -> "AsyncSchemaBuilder":
        """Get an async schema builder for creating complex schemas with fluent API.

        Returns:
            Async schema builder instance for this dataset.

        Example:
            ```python
            schema = await (dataset.schema_builder()
                .add_column("id", "int", required=True)
                .add_column("name", "string")
                .with_parsing(delimiter=",", header_row=1)
                .as_current()
                .create())
            ```
        """
        from .dataset_schema_version_async import AsyncSchemaBuilder
        return AsyncSchemaBuilder(self.dataset_id, self._client)

    async def list_schema_versions(
        self,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List["DatasetSchemaVersionAsyncModel"]:
        """List schema versions for this dataset (async).

        Args:
            status: Filter by status ('draft', 'current', 'archived').
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.

        Returns:
            List of async schema version models.
        """
        # Import here to avoid circular imports
        from ..resources_async.dataset_schema_versions import AsyncDatasetSchemaVersions

        schema_versions = AsyncDatasetSchemaVersions(self._client)
        return await schema_versions.list(
            dataset_ids=[self.dataset_id],
            status=status,
            page=page,
            page_size=page_size,
        )

    async def get_current_schema(self) -> Optional["DatasetSchemaVersionAsyncModel"]:
        """Get the current (active) schema version for this dataset (async).

        Returns:
            The current async schema version model, or None if no current schema exists.
        """
        current_schemas = await self.list_schema_versions(status="current", page_size=1)
        return current_schemas[0] if current_schemas else None

    async def get_schema_version(self, schema_version_id: str) -> "DatasetSchemaVersionAsyncModel":
        """Get a specific schema version by ID (async).

        Args:
            schema_version_id: The schema version ID to retrieve.

        Returns:
            The async schema version model.
        """
        # Import here to avoid circular imports
        from ..resources_async.dataset_schema_versions import AsyncDatasetSchemaVersions

        schema_versions = AsyncDatasetSchemaVersions(self._client)
        return await schema_versions.retrieve(schema_version_id)
