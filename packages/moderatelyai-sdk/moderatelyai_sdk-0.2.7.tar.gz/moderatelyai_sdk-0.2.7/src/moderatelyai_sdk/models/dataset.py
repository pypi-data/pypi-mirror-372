"""Dataset models with rich functionality for data operations.

This module provides the DatasetModel and DatasetDataVersionModel classes for
working with datasets and their data versions. These models offer rich functionality
for uploading data, creating schemas, and managing dataset versions.

Example:
    ```python
    from moderatelyai_sdk import ModeratelyAI

    client = ModeratelyAI(api_key="your_key", team_id="your_team")

    # Create a dataset
    dataset = client.datasets.create(
        name="Sales Data",
        description="Monthly sales records"
    )

    # Upload data
    data_version = dataset.upload_data("sales.csv")

    # Create a schema from sample data
    schema = dataset.create_schema_from_sample("sales.csv")

    # Download processed data
    content = data_version.download()
    ```
"""

import csv
import hashlib
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import httpx

from ..exceptions import APIError
from ._base import BaseModel
from ._shared.dataset_operations import DatasetOperations

if TYPE_CHECKING:
    from .dataset_schema_version import DatasetSchemaVersionModel, SchemaBuilder


class DatasetDataVersionModel(BaseModel):
    """Model representing a dataset data version.

    A data version represents a specific upload of data to a dataset. Each time
    you upload new data to a dataset, a new data version is created. This model
    provides access to version metadata and download functionality.

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
        data_version = dataset.get_data_version("version_id")

        print(f"Version {data_version.version_no}: {data_version.file_type}")
        print(f"Rows: {data_version.row_count}, Size: {data_version.file_size_bytes}")

        # Download the data
        content = data_version.download()
        data_version.download(path="./local_data.csv")
        ```
    """

    @property
    def dataset_data_version_id(self) -> str:
        """The unique identifier for this data version."""
        return self._data["datasetDataVersionId"]

    @property
    def dataset_id(self) -> str:
        """The dataset this version belongs to."""
        return self._data["datasetId"]

    @property
    def version_no(self) -> int:
        """The version number."""
        return self._data["versionNo"]

    @property
    def file_type(self) -> str:
        """The file type (csv, xlsx)."""
        return self._data["fileType"]

    @property
    def file_hash(self) -> Optional[str]:
        """The SHA256 hash of the file."""
        return self._data.get("fileHash")

    @property
    def row_count(self) -> Optional[int]:
        """The number of rows in the dataset."""
        return self._data.get("rowCount")

    @property
    def file_size_bytes(self) -> Optional[int]:
        """The size of the file in bytes."""
        return self._data.get("fileSizeBytes")

    @property
    def status(self) -> str:
        """The status of this version (draft, current, archived)."""
        return self._data["status"]

    @property
    def created_at(self) -> str:
        """When this version was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this version was last updated."""
        return self._data["updatedAt"]

    def download(self, *, path: Optional[Union[str, Path]] = None) -> Optional[bytes]:
        """Download the data for this version.

        Args:
            path: Optional path to save the file. If provided, saves to this location.
                 If not provided, returns the file content as bytes.

        Returns:
            If path is provided: None (file is saved to disk)
            If path is not provided: The file content as bytes
        """
        # Get download URL
        response = self._client._request(
            method="GET",
            path=f"/dataset-data-versions/{self.dataset_data_version_id}/download",
            cast_type=dict,
        )

        download_url = response["downloadUrl"]

        # Download the file
        try:
            with httpx.Client() as client:
                download_response = client.get(download_url)
                download_response.raise_for_status()
                file_data = download_response.content
        except httpx.HTTPError as e:
            raise APIError(f"Failed to download data version from URL: {e}") from e

        # Save to file or return bytes
        if path is not None:
            file_path = Path(path)
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(file_data)
            return None
        else:
            return file_data

    def _refresh(self) -> None:
        """Refresh this data version from the API."""
        response = self._client._request(
            method="GET",
            path=f"/dataset-data-versions/{self.dataset_data_version_id}",
            cast_type=dict,
        )
        self._data = response


class DatasetModel(BaseModel):
    """Model representing a dataset with rich data operations.

    DatasetModel provides a high-level interface for working with datasets in the
    Moderately AI platform. It offers rich functionality for data upload, schema
    management, and version control.

    Key Features:
    - Upload data in various formats (CSV, Excel)
    - Automatic schema inference from sample data
    - Schema builder with fluent API
    - Data version management and downloads
    - Rich metadata access

    This class is returned by dataset operations like:
    - `client.datasets.create()`
    - `client.datasets.retrieve()`
    - `client.datasets.list()` (returns list of DatasetModel instances)

    Attributes:
        dataset_id: Unique identifier for the dataset
        name: Dataset display name
        description: Optional dataset description
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
        dataset = client.datasets.create(
            name="Customer Data",
            description="Customer information and metrics"
        )

        # Upload data with automatic schema inference
        data_version = dataset.upload_data("customers.csv")
        schema = dataset.create_schema_from_sample("customers.csv")

        # Use schema builder for complex schemas
        schema = (dataset.schema_builder()
            .add_column("id", "int", required=True)
            .add_column("name", "string")
            .add_column("signup_date", "datetime")
            .as_current()
            .create())

        # Access dataset information
        print(f"Dataset: {dataset.name} ({dataset.record_count} records)")

        # Download current data
        content = dataset.download_data()
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

    def upload_data(
        self,
        file: Union[str, Path, bytes, Any],
        *,
        file_type: Optional[str] = None,
        status: str = "current",
        **kwargs: Any,
    ) -> DatasetDataVersionModel:
        """Upload data to this dataset, creating a new data version.

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
        # Step 1: Process the file input to get bytes and metadata
        file_data: bytes
        file_name: str

        if isinstance(file, (str, Path)):
            # Handle file path
            file_path = Path(file)
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            with open(file_path, "rb") as f:
                file_data = f.read()
            file_name = file_path.name

        elif isinstance(file, bytes):
            # Handle raw bytes
            file_data = file
            file_name = kwargs.get("filename", "uploaded_data")

        elif hasattr(file, "read"):
            # Handle file-like object (buffer)
            file_data = file.read()
            if isinstance(file_data, str):
                file_data = file_data.encode("utf-8")

            # Try to get filename from buffer object
            buffer_name = getattr(file, "name", None)
            if buffer_name:
                file_name = Path(buffer_name).name
            else:
                file_name = kwargs.get("filename", "uploaded_data")

        else:
            raise ValueError(
                f"Unsupported file type: {type(file)}. Must be str, Path, bytes, or file-like object."
            )

        # Step 2: Auto-detect file type if not provided
        if file_type is None:
            file_extension = Path(file_name).suffix.lower()
            if file_extension == ".csv":
                file_type = "csv"
            elif file_extension in [".xlsx", ".xls"]:
                file_type = "xlsx"
            else:
                raise ValueError(
                    f"Could not auto-detect file type from '{file_name}'. "
                    "Please specify file_type as 'csv' or 'xlsx'."
                )

        # Step 3: Calculate file properties
        file_size = len(file_data)
        file_hash = hashlib.sha256(file_data).hexdigest()

        # Rough row count estimation for CSV (not perfect but useful)
        row_count = None
        if file_type == "csv":
            try:
                # Simple row count by counting newlines (minus header)
                text_data = file_data.decode("utf-8")
                row_count = max(0, text_data.count("\n") - 1)  # Subtract header row
            except UnicodeDecodeError:
                # If we can't decode, skip row counting
                pass

        # Step 4: Create data version with upload URL
        create_response = self._client._request(
            method="POST",
            path="/dataset-data-versions",
            body={
                "datasetId": self.dataset_id,
                "fileName": file_name,
                "fileType": file_type,
                "status": status,
            },
            cast_type=dict,
        )

        data_version_data = create_response["dataVersion"]
        upload_url = create_response["uploadUrl"]
        data_version_id = data_version_data["datasetDataVersionId"]

        # Step 5: Upload file to presigned URL
        try:
            # Determine content type
            content_type = "text/csv" if file_type == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            with httpx.Client() as client:
                upload_result = client.put(
                    upload_url,
                    content=file_data,
                    headers={"Content-Type": content_type},
                )
                upload_result.raise_for_status()
        except Exception as e:
            raise APIError(f"Failed to upload data to presigned URL: {e}") from e

        # Step 6: Mark upload as complete
        try:
            complete_response = self._client._request(
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
            return DatasetDataVersionModel(complete_response, self._client)

        except Exception as e:
            raise APIError(f"Failed to complete data version upload: {e}") from e

    def download_data(
        self,
        *,
        version_id: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
    ) -> Optional[bytes]:
        """Download data from this dataset.

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
        version_model = DatasetDataVersionModel(version_data, self._client)

        return version_model.download(path=path)

    def list_data_versions(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
    ) -> List[DatasetDataVersionModel]:
        """List data versions for this dataset.

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

        response = self._client._request(
            method="GET",
            path="/dataset-data-versions",
            cast_type=dict,
            options={"query": query},
        )

        # Convert response items to models
        versions = []
        for item in response.get("items", []):
            versions.append(DatasetDataVersionModel(item, self._client))

        return versions

    def get_data_version(self, version_id: str) -> DatasetDataVersionModel:
        """Get a specific data version by ID.

        Args:
            version_id: The data version ID to retrieve.

        Returns:
            The data version model.
        """
        response = self._client._request(
            method="GET",
            path=f"/dataset-data-versions/{version_id}",
            cast_type=dict,
        )
        return DatasetDataVersionModel(response, self._client)

    def update(
        self,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        should_process: Optional[bool] = None,
        **kwargs: Any,
    ) -> "DatasetModel":
        """Update this dataset.

        Args:
            name: New dataset name.
            description: New dataset description.
            should_process: Whether to trigger dataset processing workflow.
            **kwargs: Additional properties to update.

        Returns:
            Updated dataset model.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if should_process is not None:
            body["shouldProcess"] = should_process

        updated_data = self._client._request(
            method="PATCH",
            path=f"/datasets/{self.dataset_id}",
            body=body,
            cast_type=dict,
        )

        # Update our internal data and return self
        self._data = updated_data
        return self

    def delete(self) -> None:
        """Delete this dataset."""
        self._client._request(
            method="DELETE",
            path=f"/datasets/{self.dataset_id}",
            cast_type=dict,
        )

    def _refresh(self) -> None:
        """Refresh this dataset from the API."""
        response = self._client._request(
            method="GET",
            path=f"/datasets/{self.dataset_id}",
            cast_type=dict,
        )
        self._data = response

    # Schema Version Methods

    def create_schema(
        self,
        columns: List[Dict[str, Any]],
        *,
        status: str = "draft",
        parsing_options: Optional[Dict[str, Any]] = None,
    ) -> "DatasetSchemaVersionModel":
        """Create a schema version with simple column definitions.

        Args:
            columns: List of column definitions. Each dict should have:
                     - name: Column name (required)
                     - type: Column type (required) - 'string', 'int', 'float', 'datetime', 'bool'
                     - required: Whether column is required (optional, defaults to True)
                     - description: Column description (optional)
            status: Initial status ('draft' or 'current'). Defaults to 'draft'.
            parsing_options: Optional parsing configuration.

        Returns:
            The created schema version model.

        Example:
            ```python
            schema = dataset.create_schema([
                {"name": "user_id", "type": "int", "required": True},
                {"name": "email", "type": "string", "description": "User email address"},
                {"name": "signup_date", "type": "datetime"},
            ])
            ```
        """
        # Convert simple column definitions to full API format
        api_columns = []
        for i, col in enumerate(columns, 1):
            if "name" not in col or "type" not in col:
                raise ValueError("Each column must have 'name' and 'type' fields")

            # Convert user-friendly types to API types
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
        from ..resources.dataset_schema_versions import DatasetSchemaVersions

        # Create using internal resource
        schema_versions = DatasetSchemaVersions(self._client)
        return schema_versions.create(
            dataset_id=self.dataset_id,
            columns=api_columns,
            status=status,
            parsing_options=parsing_options,
        )

    def create_schema_from_sample(
        self,
        sample_file: Union[str, Path, bytes],
        *,
        status: str = "draft",
        header_row: int = 1,
        sample_size: int = 100,
    ) -> "DatasetSchemaVersionModel":
        """Create a schema by analyzing a sample data file.

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
            ValueError: If file format is not supported or file is invalid.
        """
        # Prepare sample file using shared logic
        file_data, file_name, file_type, _, _, _ = DatasetOperations.validate_and_prepare_file(
            sample_file
        )

        # Infer schema using shared logic
        inferred_columns = DatasetOperations.infer_schema_from_sample(
            file_data, file_type, sample_size
        )

        # Create schema with inferred columns
        return self.create_schema(
            columns=inferred_columns,
            status=status,
        )

    def _infer_column_type(self, values: List[str]) -> str:
        """Infer the data type of a column from sample values."""

        if not values:
            return "string"

        # Try integer
        int_count = 0
        for value in values:
            try:
                int(value)
                int_count += 1
            except ValueError:
                pass

        if int_count == len(values):
            return "integer"

        # Try float
        float_count = 0
        for value in values:
            try:
                float(value)
                float_count += 1
            except ValueError:
                pass

        if float_count == len(values):
            return "float"

        # Try boolean
        bool_values = {"true", "false", "1", "0", "yes", "no", "y", "n"}
        bool_count = sum(1 for v in values if v.lower() in bool_values)
        if bool_count == len(values):
            return "boolean"

        # Try datetime (simple patterns)
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
        ]

        datetime_count = 0
        for value in values:
            if any(re.match(pattern, value) for pattern in datetime_patterns):
                datetime_count += 1

        if datetime_count >= len(values) * 0.8:  # 80% match threshold
            return "datetime"

        # Default to string
        return "string"

    def schema_builder(self) -> "SchemaBuilder":
        """Get a schema builder for creating complex schemas with fluent API.

        Returns:
            Schema builder instance for this dataset.

        Example:
            ```python
            schema = (dataset.schema_builder()
                .add_column("id", "int", required=True)
                .add_column("name", "string")
                .with_parsing(delimiter=",", header_row=1)
                .as_current()
                .create())
            ```
        """
        from .dataset_schema_version import SchemaBuilder
        return SchemaBuilder(self.dataset_id, self._client)

    def list_schema_versions(
        self,
        *,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> List["DatasetSchemaVersionModel"]:
        """List schema versions for this dataset.

        Args:
            status: Filter by status ('draft', 'current', 'archived').
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.

        Returns:
            List of schema version models.
        """
        # Import here to avoid circular imports
        from ..resources.dataset_schema_versions import DatasetSchemaVersions

        schema_versions = DatasetSchemaVersions(self._client)
        return schema_versions.list(
            dataset_ids=[self.dataset_id],
            status=status,
            page=page,
            page_size=page_size,
        )

    def get_current_schema(self) -> Optional["DatasetSchemaVersionModel"]:
        """Get the current (active) schema version for this dataset.

        Returns:
            The current schema version model, or None if no current schema exists.
        """
        current_schemas = self.list_schema_versions(status="current", page_size=1)
        return current_schemas[0] if current_schemas else None

    def get_schema_version(self, schema_version_id: str) -> "DatasetSchemaVersionModel":
        """Get a specific schema version by ID.

        Args:
            schema_version_id: The schema version ID to retrieve.

        Returns:
            The schema version model.
        """
        # Import here to avoid circular imports
        from ..resources.dataset_schema_versions import DatasetSchemaVersions

        schema_versions = DatasetSchemaVersions(self._client)
        return schema_versions.retrieve(schema_version_id)
