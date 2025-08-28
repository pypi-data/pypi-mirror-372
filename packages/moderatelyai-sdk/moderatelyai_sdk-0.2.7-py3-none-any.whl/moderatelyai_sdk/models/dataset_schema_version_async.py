"""Async dataset schema version model."""

from typing import Any, Dict, List, Optional, Union

from ._base_async import BaseAsyncModel


class DatasetSchemaVersionAsyncModel(BaseAsyncModel):
    """Async model representing a dataset schema version.

    A schema version defines the structure and data types for a dataset.
    This async model provides access to schema metadata and validation functionality.
    """

    @property
    def dataset_schema_version_id(self) -> str:
        """The unique identifier for this schema version."""
        return self._data["datasetSchemaVersionId"]

    @property
    def dataset_id(self) -> str:
        """The ID of the parent dataset."""
        return self._data["datasetId"]

    @property
    def version_no(self) -> int:
        """The schema version number (incremental)."""
        return self._data["versionNo"]

    @property
    def columns(self) -> List[Dict[str, Any]]:
        """The column definitions for this schema."""
        return self._data.get("columnsJson", [])

    @property
    def parsing_config(self) -> Optional[Dict[str, Any]]:
        """Parsing configuration for CSV files."""
        return self._data.get("parsingConfig")

    @property
    def status(self) -> str:
        """The status of this schema version (draft, current, archived)."""
        return self._data["status"]

    @property 
    def is_current(self) -> bool:
        """Whether this is the current schema version."""
        return self._data.get("isCurrent", False)

    @property
    def created_at(self) -> str:
        """When this schema version was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this schema version was last updated."""
        return self._data["updatedAt"]

    async def _refresh(self) -> None:
        """Refresh this schema version from the API."""
        fresh_data = await self._client._request(
            method="GET",
            path=f"/dataset-schema-versions/{self.dataset_schema_version_id}",
            cast_type=dict,
        )
        self._data = fresh_data


class AsyncSchemaBuilder:
    """Async fluent API builder for creating dataset schema versions.

    AsyncSchemaBuilder provides a chainable interface for constructing complex dataset
    schemas with parsing options and validation. It offers the most advanced level
    of schema creation with full control over column properties and data processing.

    The builder pattern allows you to:
    - Add columns with detailed specifications
    - Configure parsing options (delimiters, headers, encoding)
    - Set schema status (draft/current)
    - Create the final schema version

    Example:
        ```python
        # Build a comprehensive schema
        schema = await (dataset.schema_builder()
            .add_column("id", "int", required=True, description="Primary key")
            .add_column("email", "string", required=True)
            .add_column("signup_date", "datetime", required=False)
            .add_column("is_active", "bool", required=True)
            .with_parsing(
                delimiter=",",
                header_row=1,
                encoding="utf-8"
            )
            .as_current()  # Mark as active schema
            .create())      # Execute the creation (async)

        print(f"Created schema version {schema.version_no}")
        ```
    """

    def __init__(self, dataset_id: str, client):
        """Initialize async schema builder.

        Args:
            dataset_id: The dataset to create schema for.
            client: The async API client instance.
        """
        self._dataset_id = dataset_id
        self._client = client
        self._columns: List[Dict[str, Any]] = []
        self._parsing_options: Dict[str, Any] = {}
        self._status = "draft"

    def add_column(
        self,
        name: str,
        column_type: str,
        *,
        required: bool = True,
        description: Optional[str] = None,
        operations: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> "AsyncSchemaBuilder":
        """Add a column to the schema being built.

        Args:
            name: Column name.
            column_type: Column type ('string', 'integer', 'float', 'datetime', 'boolean').
            required: Whether the column is required (not nullable).
            description: Optional column description.
            operations: List of column operations (advanced).
            **kwargs: Additional column properties.

        Returns:
            This builder for method chaining.
        """
        # Convert user-friendly types to API types
        type_mapping = {
            "str": "string",
            "int": "integer",
            "float": "float",
            "datetime": "datetime",
            "bool": "boolean",
            "date": "datetime",
        }
        api_type = type_mapping.get(column_type, column_type)

        column = {
            "pos": len(self._columns) + 1,
            "name": name,
            "type": api_type,
            "nullable": not required,
            **kwargs,
        }

        if description:
            column["description"] = description
        if operations:
            column["operations"] = operations

        self._columns.append(column)
        return self

    def with_parsing(
        self,
        *,
        skip_rows: Optional[Union[int, List[int]]] = None,
        header_row: Optional[int] = None,
        delimiter: Optional[str] = None,
        encoding: Optional[str] = None,
    ) -> "AsyncSchemaBuilder":
        """Set parsing options for the schema.

        Args:
            skip_rows: Row indices to skip (0-based), or single row index.
            header_row: Row containing column headers (1-based).
            delimiter: Field delimiter (e.g., ',', '\t', ';').
            encoding: File encoding (e.g., 'utf-8', 'latin1').

        Returns:
            This builder for method chaining.
        """
        if skip_rows is not None:
            self._parsing_options["skipRows"] = skip_rows
        if header_row is not None:
            self._parsing_options["headerRow"] = header_row
        if delimiter is not None:
            self._parsing_options["delimiter"] = delimiter
        if encoding is not None:
            self._parsing_options["encoding"] = encoding

        return self

    def as_draft(self) -> "AsyncSchemaBuilder":
        """Set the schema status to draft.

        Returns:
            This builder for method chaining.
        """
        self._status = "draft"
        return self

    def as_current(self) -> "AsyncSchemaBuilder":
        """Set the schema status to current (active).

        Returns:
            This builder for method chaining.
        """
        self._status = "current"
        return self

    async def create(self) -> DatasetSchemaVersionAsyncModel:
        """Create the schema version with the configured settings (async).

        Returns:
            The created async schema version model.

        Raises:
            ValueError: If no columns have been added.
            APIError: If creation fails.
        """
        if not self._columns:
            raise ValueError("Cannot create schema with no columns. Use add_column() first.")

        # Build request body
        body = {
            "datasetId": self._dataset_id,
            "columns": self._columns,  # Note: API expects 'columns', not 'columnsJson'
            "status": self._status,
        }

        if self._parsing_options:
            body["parsingOptions"] = self._parsing_options

        # Create the schema version (async)
        response = await self._client._request(
            method="POST",
            path="/dataset-schema-versions",
            body=body,
            cast_type=dict,
        )

        return DatasetSchemaVersionAsyncModel(response, self._client)
