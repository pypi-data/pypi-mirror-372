"""Dataset schema version models with user-friendly functionality.

This module provides DatasetSchemaVersionModel and SchemaBuilder classes for
managing dataset schemas with a user-friendly API that simplifies the complex
underlying schema structure.

Example:
    ```python
    from moderatelyai_sdk import ModeratelyAI

    client = ModeratelyAI(api_key="your_key", team_id="your_team")
    dataset = client.datasets.retrieve("dataset_123")

    # Simple schema creation
    schema = dataset.create_schema([
        {"name": "id", "type": "int", "required": True},
        {"name": "name", "type": "string"},
        {"name": "created_at", "type": "datetime"}
    ])

    # Auto-inference from CSV
    schema = dataset.create_schema_from_sample("data.csv")

    # Advanced fluent API
    schema = (dataset.schema_builder()
        .add_column("user_id", "int", required=True)
        .add_column("email", "string")
        .with_parsing(delimiter=",", header_row=1)
        .as_current()
        .create())
    ```
"""

from typing import Any, Dict, List, Optional, Union

from ._base import BaseModel


class DatasetSchemaVersionModel(BaseModel):
    """Model representing a dataset schema version with rich functionality.

    A schema version defines the structure and data types for a dataset's columns.
    This model provides methods for managing schema versions, including activation,
    column manipulation, and updates.

    Key Features:
    - Activate/archive schema versions
    - Add/remove columns dynamically
    - Update schema properties
    - Rich column access and validation

    Attributes:
        dataset_schema_version_id: Unique identifier for this schema version
        dataset_id: ID of the parent dataset
        version_no: Version number (incremental)
        columns: List of column definitions
        status: Schema status (draft, current, archived)
        parsing_options: Data parsing configuration
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        ```python
        # Get current schema
        schema = dataset.get_current_schema()

        # Add a new column
        schema.add_column("new_field", "string", required=False)

        # Activate the schema
        schema.activate()

        # Access column information
        user_id_col = schema.get_column("user_id")
        print(f"Column: {user_id_col['name']} ({user_id_col['type']})")
        ```
    """

    @property
    def dataset_schema_version_id(self) -> str:
        """The unique identifier for this schema version."""
        return self._data["datasetSchemaVersionId"]

    @property
    def dataset_id(self) -> str:
        """The dataset this schema version belongs to."""
        return self._data["datasetId"]

    @property
    def version_no(self) -> int:
        """The version number."""
        return self._data["versionNo"]

    @property
    def columns(self) -> List[Dict[str, Any]]:
        """The column definitions for this schema."""
        return self._data["columnsJson"]

    @property
    def status(self) -> str:
        """The status of this schema version (draft, current, archived)."""
        return self._data["status"]

    @property
    def parsing_options(self) -> Optional[Dict[str, Any]]:
        """Parsing options for data processing."""
        return self._data.get("parsingOptions")

    @property
    def created_at(self) -> str:
        """When this schema version was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this schema version was last updated."""
        return self._data["updatedAt"]

    def activate(self) -> "DatasetSchemaVersionModel":
        """Make this schema version the current/active one.

        Returns:
            Updated schema version model.
        """
        return self.update(status="current")

    def archive(self) -> "DatasetSchemaVersionModel":
        """Archive this schema version.

        Returns:
            Updated schema version model.
        """
        return self.update(status="archived")

    def update(
        self,
        *,
        status: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        parsing_options: Optional[Dict[str, Any]] = None,
    ) -> "DatasetSchemaVersionModel":
        """Update this schema version.

        Args:
            status: New status ('draft', 'current', 'archived').
            columns: Updated column definitions.
            parsing_options: Updated parsing options.

        Returns:
            Updated schema version model.
        """
        body = {}
        if status is not None:
            body["status"] = status
        if columns is not None:
            body["columns"] = columns  # API expects 'columns', not 'columnsJson'
        if parsing_options is not None:
            body["parsingOptions"] = parsing_options

        updated_data = self._client._request(
            method="PATCH",
            path=f"/dataset-schema-versions/{self.dataset_schema_version_id}",
            body=body,
            cast_type=dict,
        )

        # Update our internal data and return self
        self._data = updated_data
        return self

    def add_column(
        self,
        name: str,
        column_type: str,
        *,
        required: bool = True,
        description: Optional[str] = None,
        position: Optional[int] = None,
        **kwargs: Any,
    ) -> "DatasetSchemaVersionModel":
        """Add a new column to this schema version.

        Args:
            name: Column name.
            column_type: Column type ('string', 'integer', 'float', 'datetime', 'boolean').
            required: Whether the column is required (not nullable).
            description: Optional column description.
            position: Position in the schema (1-based). If None, adds to end.
            **kwargs: Additional column properties.

        Returns:
            Updated schema version model.
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

        # Create new column definition
        new_column = {
            "name": name,
            "type": api_type,
            "nullable": not required,
            **kwargs,
        }

        if description:
            new_column["description"] = description

        # Add position if specified
        columns = self.columns.copy()
        if position is not None:
            new_column["pos"] = position
            # Insert at specified position (convert from 1-based to 0-based)
            columns.insert(position - 1, new_column)
        else:
            # Add to end with next position
            max_pos = max((col.get("pos", 0) for col in columns), default=0)
            new_column["pos"] = max_pos + 1
            columns.append(new_column)

        return self.update(columns=columns)

    def remove_column(self, name: str) -> "DatasetSchemaVersionModel":
        """Remove a column from this schema version.

        Args:
            name: Name of the column to remove.

        Returns:
            Updated schema version model.

        Raises:
            ValueError: If column doesn't exist.
        """
        columns = self.columns.copy()
        original_length = len(columns)

        # Remove column by name
        columns = [col for col in columns if col.get("name") != name]

        if len(columns) == original_length:
            raise ValueError(f"Column '{name}' not found in schema")

        return self.update(columns=columns)

    def get_column(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a column definition by name.

        Args:
            name: Column name to find.

        Returns:
            Column definition dictionary or None if not found.
        """
        for column in self.columns:
            if column.get("name") == name:
                return column
        return None

    def _refresh(self) -> None:
        """Refresh this schema version from the API."""
        response = self._client._request(
            method="GET",
            path=f"/dataset-schema-versions/{self.dataset_schema_version_id}",
            cast_type=dict,
        )
        self._data = response


class SchemaBuilder:
    """Fluent API builder for creating dataset schema versions.

    SchemaBuilder provides a chainable interface for constructing complex dataset
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
        schema = (dataset.schema_builder()
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
            .create())      # Execute the creation

        print(f"Created schema version {schema.version_no}")
        ```
    """

    def __init__(self, dataset_id: str, client):
        """Initialize schema builder.

        Args:
            dataset_id: The dataset to create schema for.
            client: The API client instance.
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
    ) -> "SchemaBuilder":
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
    ) -> "SchemaBuilder":
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

    def as_draft(self) -> "SchemaBuilder":
        """Set the schema status to draft.

        Returns:
            This builder for method chaining.
        """
        self._status = "draft"
        return self

    def as_current(self) -> "SchemaBuilder":
        """Set the schema status to current (active).

        Returns:
            This builder for method chaining.
        """
        self._status = "current"
        return self

    def create(self) -> DatasetSchemaVersionModel:
        """Create the schema version with the configured settings.

        Returns:
            The created schema version model.

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

        # Create the schema version
        response = self._client._request(
            method="POST",
            path="/dataset-schema-versions",
            body=body,
            cast_type=dict,
        )

        return DatasetSchemaVersionModel(response, self._client)
