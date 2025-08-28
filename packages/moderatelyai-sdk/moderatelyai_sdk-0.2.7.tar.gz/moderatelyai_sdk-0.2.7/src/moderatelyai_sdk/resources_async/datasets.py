"""Async datasets resource for the Moderately AI API."""

from typing import TYPE_CHECKING, List, Optional

from ..models._shared.dataset_operations import DatasetOperations
from ..types import PaginatedResponse
from ._base import AsyncBaseResource

if TYPE_CHECKING:
    from ..models.dataset_async import DatasetAsyncModel


class AsyncDatasets(AsyncBaseResource):
    """Manage datasets in your teams (async version).

    Examples:
        ```python
        import asyncio
        import moderatelyai_sdk

        async def main():
            async with moderatelyai_sdk.AsyncModeratelyAI() as client:
                # List all datasets (still returns raw data)
                datasets = await client.datasets.list()

                # Get a dataset with rich functionality
                dataset = await client.datasets.retrieve("dataset_123")

                # Create a new dataset
                dataset = await client.datasets.create(
                    name="Customer Data",
                    description="Customer interaction dataset"
                )

                # Now use rich methods on the dataset object:

                # Upload data to the dataset
                version = await dataset.upload_data("/path/to/sales_data.csv")
                print(f"Uploaded version {version.version_no} with {version.row_count} rows")

                # Download current data
                data_bytes = await dataset.download_data()
                await dataset.download_data(path="/save/local_copy.csv")

                # Work with specific versions
                versions = await dataset.list_data_versions()
                old_data = await dataset.download_data(version_id="version_123")

                # Schema management
                # Simple schema creation
                schema = await dataset.create_schema([
                    {"name": "user_id", "type": "int", "required": True},
                    {"name": "email", "type": "string"},
                    {"name": "signup_date", "type": "datetime"},
                ])

                # Auto-infer schema from sample data
                schema = await dataset.create_schema_from_sample("sample.csv")

        asyncio.run(main())
        ```
    """

    async def list(
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
        """List all datasets with pagination (async).

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
        query = DatasetOperations.build_list_query(
            dataset_ids=dataset_ids,
            name_like=name_like,
            name=name,
            page=page,
            page_size=page_size,
            order_by=order_by,
            order_direction=order_direction,
        )

        response = await self._get(
            "/datasets",
            options={"query": query},
        )

        # Convert items to DatasetAsyncModel instances
        if "items" in response:
            from ..models.dataset_async import DatasetAsyncModel
            response["items"] = [
                DatasetAsyncModel(item, self._client) for item in response["items"]
            ]

        return response

    async def retrieve(self, dataset_id: str) -> "DatasetAsyncModel":
        """Retrieve a specific dataset by ID (async).

        Args:
            dataset_id: The ID of the dataset to retrieve.

        Returns:
            The dataset model with rich functionality.

        Raises:
            NotFoundError: If the dataset doesn't exist.
        """
        from ..models.dataset_async import DatasetAsyncModel

        data = await self._get(f"/datasets/{dataset_id}")
        return DatasetAsyncModel(data, self._client)

    async def create(
        self,
        *,
        name: str,
        description: Optional[str] = None,
        **kwargs,
    ) -> "DatasetAsyncModel":
        """Create a new dataset (async).

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
        from ..models.dataset_async import DatasetAsyncModel

        body = {
            "name": name,
            "teamId": self._client.team_id,  # Use client's team_id
            **kwargs,
        }
        if description is not None:
            body["description"] = description

        data = await self._post("/datasets", body=body)
        return DatasetAsyncModel(data, self._client)

    async def update(
        self,
        dataset_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        should_process: Optional[bool] = None,
        **kwargs,
    ) -> "DatasetAsyncModel":
        """Update an existing dataset (async).

        Args:
            dataset_id: The ID of the dataset to update.
            name: New dataset name.
            description: New dataset description.
            should_process: Whether to trigger dataset processing workflow.
            **kwargs: Additional properties to update.

        Returns:
            The updated dataset model.

        Raises:
            NotFoundError: If the dataset doesn't exist.
            ValidationError: If the request data is invalid.
        """
        from ..models.dataset_async import DatasetAsyncModel

        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if should_process is not None:
            body["shouldProcess"] = should_process

        data = await self._patch(f"/datasets/{dataset_id}", body=body)
        return DatasetAsyncModel(data, self._client)

    async def delete(self, dataset_id: str) -> None:
        """Delete a dataset (async).

        Args:
            dataset_id: The ID of the dataset to delete.

        Raises:
            NotFoundError: If the dataset doesn't exist.
        """
        await self._delete(f"/datasets/{dataset_id}")
