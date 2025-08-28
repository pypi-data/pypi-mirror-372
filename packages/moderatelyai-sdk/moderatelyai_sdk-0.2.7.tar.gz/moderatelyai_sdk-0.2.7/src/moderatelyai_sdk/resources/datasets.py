"""Datasets resource for the Moderately AI API."""

from typing import List, Optional

from ..models.dataset import DatasetModel
from ..types import PaginatedResponse
from ._base import BaseResource


class Datasets(BaseResource):
    """Manage datasets in your teams.

    Examples:
        ```python
        # List all datasets (still returns raw data)
        datasets = client.datasets.list()

        # Get a dataset with rich functionality
        dataset = client.datasets.retrieve("dataset_123")

        # Create a new dataset
        dataset = client.datasets.create(
            name="Customer Data",
            description="Customer interaction dataset"
        )

        # Now use rich methods on the dataset object:

        # Upload data to the dataset
        version = dataset.upload_data("/path/to/sales_data.csv")
        print(f"Uploaded version {version.version_no} with {version.row_count} rows")

        # Download current data
        data_bytes = dataset.download_data()
        dataset.download_data(path="/save/local_copy.csv")

        # Work with specific versions
        versions = dataset.list_data_versions()
        old_data = dataset.download_data(version_id="version_123")

        # Schema management (NEW!)
        # Simple schema creation
        schema = dataset.create_schema([
            {"name": "user_id", "type": "int", "required": True},
            {"name": "email", "type": "string"},
            {"name": "signup_date", "type": "datetime"},
        ])

        # Auto-infer schema from sample data
        schema = dataset.create_schema_from_sample("sample.csv")

        # Advanced schema with fluent API
        schema = (dataset.schema_builder()
            .add_column("id", "int", required=True)
            .add_column("name", "string", description="User name")
            .with_parsing(delimiter=",", header_row=1)
            .as_current()
            .create())

        # Access dataset metadata
        print(f"Dataset has {dataset.record_count} records")
        print(f"Processing status: {dataset.processing_status}")
        current_schema = dataset.get_current_schema()

        # Update dataset
        dataset.update(name="Updated Dataset Name", should_process=True)

        # Delete dataset
        dataset.delete()
        ```
    """

    def list(
        self,
        *,
        dataset_ids: Optional[List[str]] = None,
        name_like: Optional[str] = None,
        name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "createdAt",
        order_direction: str = "desc",
    ) -> PaginatedResponse:
        """List all datasets with pagination.

        Note: Results are automatically filtered to the team specified in the client.

        Args:
            dataset_ids: Filter by specific dataset IDs.
            name_like: Filter by datasets with names containing this text.
            name: Filter by exact dataset name.
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by ("createdAt", "updatedAt", "name"). Defaults to "createdAt".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of datasets for the client's team.
        """
        query = {
            "page": page,
            "pageSize": page_size,
            "orderBy": order_by,
            "orderDirection": order_direction,
        }
        if dataset_ids is not None:
            query["datasetIds"] = dataset_ids
        if name_like is not None:
            query["nameLike"] = name_like
        if name is not None:
            query["name"] = name

        response = self._get(
            "/datasets",
            options={"query": query},
        )

        # Convert items to DatasetModel instances
        if "items" in response:
            response["items"] = [
                DatasetModel(item, self._client) for item in response["items"]
            ]

        return response

    def retrieve(self, dataset_id: str) -> DatasetModel:
        """Retrieve a specific dataset by ID.

        Args:
            dataset_id: The ID of the dataset to retrieve.

        Returns:
            The dataset model with rich functionality.

        Raises:
            NotFoundError: If the dataset doesn't exist.
        """
        data = self._get(f"/datasets/{dataset_id}")
        return DatasetModel(data, self._client)

    def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> DatasetModel:
        """Create a new dataset.

        Note: The dataset will be created in the team specified in the client.

        Args:
            name: The dataset's name.
            description: The dataset's description.
            **kwargs: Additional dataset properties.

        Returns:
            The created dataset model with rich functionality.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "name": name,
            "teamId": self._client.team_id,  # Use client's team_id with camelCase
            **kwargs,
        }
        if description is not None:
            body["description"] = description

        data = self._post("/datasets", body=body)
        return DatasetModel(data, self._client)

    def update(
        self,
        dataset_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        should_process: Optional[bool] = None,
        **kwargs,
    ) -> DatasetModel:
        """Update an existing dataset.

        Args:
            dataset_id: The ID of the dataset to update.
            name: New dataset name.
            description: New dataset description.
            should_process: Whether to trigger dataset processing workflow.
            **kwargs: Additional properties to update.

        Returns:
            The updated dataset model with rich functionality.

        Raises:
            NotFoundError: If the dataset doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if should_process is not None:
            body["shouldProcess"] = should_process

        data = self._patch(f"/datasets/{dataset_id}", body=body)
        return DatasetModel(data, self._client)

    def delete(self, dataset_id: str) -> None:
        """Delete a dataset.

        Args:
            dataset_id: The ID of the dataset to delete.

        Raises:
            NotFoundError: If the dataset doesn't exist.
        """
        self._delete(f"/datasets/{dataset_id}")

