"""Shared dataset operations for both sync and async implementations."""

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class DatasetOperations:
    """Shared business logic for dataset operations."""

    @staticmethod
    def validate_and_prepare_file(
        file: Union[str, Path, bytes, Any],
        file_type: Optional[str] = None,
        **kwargs: Any
    ) -> Tuple[bytes, str, str, int, str, Optional[int]]:
        """Validate and prepare file for upload.

        Args:
            file: The file to upload - can be a path, bytes, or file-like object
            file_type: File type ('csv' or 'xlsx'). Auto-detected if not provided.
            **kwargs: Additional options including filename for bytes input.

        Returns:
            Tuple of (file_data, file_name, file_type, file_size, file_hash, row_count)

        Raises:
            ValueError: If file is invalid or not found.
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

        return file_data, file_name, file_type, file_size, file_hash, row_count

    @staticmethod
    def build_list_query(
        dataset_ids: Optional[List[str]] = None,
        name_like: Optional[str] = None,
        name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "createdAt",
        order_direction: str = "desc",
    ) -> Dict[str, Any]:
        """Build query parameters for dataset list operations.

        Args:
            dataset_ids: Filter by specific dataset IDs.
            name_like: Filter by datasets with names containing this text.
            name: Filter by exact dataset name.
            page: Page number (1-based).
            page_size: Number of items per page.
            order_by: Field to sort by.
            order_direction: Sort direction ("asc" or "desc").

        Returns:
            Dictionary of query parameters.
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }

        if dataset_ids:
            query["dataset_ids"] = dataset_ids
        if name_like:
            query["name_like"] = name_like
        if name:
            query["name"] = name

        return query

    @staticmethod
    def validate_schema_columns(columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and normalize schema column definitions.

        Args:
            columns: List of column definitions.

        Returns:
            Validated and normalized column definitions.

        Raises:
            ValueError: If column definitions are invalid.
        """
        if not columns:
            raise ValueError("Schema must have at least one column")

        valid_types = {
            "string", "int", "float", "boolean", "datetime", "date", "time"
        }

        validated_columns = []
        for i, col in enumerate(columns):
            if not isinstance(col, dict):
                raise ValueError(f"Column {i} must be a dictionary")

            if "name" not in col:
                raise ValueError(f"Column {i} must have a 'name' field")

            if "type" not in col:
                raise ValueError(f"Column {i} ({col['name']}) must have a 'type' field")

            if col["type"] not in valid_types:
                raise ValueError(
                    f"Column {i} ({col['name']}) has invalid type '{col['type']}'. "
                    f"Valid types: {', '.join(valid_types)}"
                )

            # Normalize column definition
            normalized_col = {
                "name": col["name"],
                "type": col["type"],
                "required": col.get("required", False),
                "description": col.get("description"),
            }

            # Remove None values
            validated_columns.append({k: v for k, v in normalized_col.items() if v is not None})

        return validated_columns

    @staticmethod
    def infer_schema_from_sample(file_data: bytes, file_type: str, sample_rows: int = 100) -> List[Dict[str, Any]]:
        """Infer schema from sample data (simplified version).

        This is a basic implementation. In practice, you might want more sophisticated
        type inference logic.

        Args:
            file_data: Raw file data.
            file_type: File type ('csv' or 'xlsx').
            sample_rows: Number of rows to sample for inference.

        Returns:
            List of inferred column definitions.

        Raises:
            ValueError: If schema cannot be inferred.
        """
        if file_type != "csv":
            raise ValueError("Schema inference currently only supports CSV files")

        try:
            text_data = file_data.decode("utf-8")
            lines = text_data.strip().split("\n")

            if len(lines) < 1:
                raise ValueError("File appears to be empty")

            # Get header row
            header_line = lines[0]
            columns = [col.strip().strip('"') for col in header_line.split(",")]

            if not columns or not columns[0]:
                raise ValueError("Could not parse header row from CSV")

            # Create basic schema with string types (can be enhanced with type inference)
            schema_columns = []
            for col_name in columns:
                if col_name:  # Skip empty column names
                    schema_columns.append({
                        "name": col_name,
                        "type": "string",  # Default to string type
                        "required": False,
                    })

            return schema_columns

        except UnicodeDecodeError as e:
            raise ValueError(f"Could not decode CSV file: {e}") from e
        except Exception as e:
            raise ValueError(f"Could not infer schema from file: {e}") from e

    @staticmethod
    def build_create_data_version_body(
        dataset_id: str,
        file_name: str,
        file_type: str,
        status: str = "current",
    ) -> Dict[str, Any]:
        """Build request body for creating a data version.

        Args:
            dataset_id: ID of the dataset.
            file_name: Name of the file being uploaded.
            file_type: Type of file ('csv' or 'xlsx').
            status: Version status ('draft' or 'current').

        Returns:
            Request body dictionary.
        """
        return {
            "datasetId": dataset_id,
            "fileName": file_name,
            "fileType": file_type,
            "status": status,
        }
