"""Asynchronous client for the Moderately AI API."""

import os
from typing import Any, Dict, Optional, Union

import httpx

from ._base_client_async import AsyncBaseClient
from .resources_async import (
    AsyncAgentExecutions,
    AsyncAgents,
    AsyncDatasets,
    AsyncFiles,
    AsyncPipelineConfigurationVersions,
    AsyncPipelineExecutions,
    AsyncPipelines,
    AsyncTeams,
    AsyncUsers,
)
from .types import HTTPMethod


class AsyncModeratelyAI(AsyncBaseClient):
    """Asynchronous client for the Moderately AI API.

    The async client provides the same interface as the synchronous client,
    but all methods are async and return awaitable objects. Ideal for use in
    async frameworks like FastAPI, aiohttp, or asyncio applications.

    Attributes:
        users: User management operations (async)
        teams: Team settings and information (async)
        agents: AI agent management and execution (async)
        agent_executions: Agent execution monitoring (async)
        datasets: Dataset upload, management, and schema operations (async)
        pipelines: Pipeline creation and configuration management (async)
        pipeline_configuration_versions: Pipeline workflow configuration (async)
        pipeline_executions: Pipeline execution and monitoring (async)
        files: File upload, download, and management (async)

    Args:
        api_key: Your API key. If not provided, reads from MODERATELY_API_KEY environment variable.
        team_id: Your team ID. If not provided, reads from MODERATELY_TEAM_ID environment variable.
        base_url: API base URL. Defaults to https://api.moderately.ai
        timeout: Request timeout in seconds. Defaults to 10.0.
        max_retries: Maximum retry attempts. Defaults to 2.
        default_headers: Additional headers to include in all requests. Optional.
        default_query: Additional query parameters to include in all requests. Optional.
        http_client: Custom async HTTP client instance. Optional.

    Example:
        ```python
        import asyncio
        import moderatelyai_sdk

        async def main():
            # Use as async context manager (recommended)
            async with moderatelyai_sdk.AsyncModeratelyAI() as client:
                # All operations are awaitable and team-scoped
                users = await client.users.list()                    # User management
                dataset = await client.datasets.create(name="Data")  # Dataset operations
                agents = await client.agents.list()                  # AI agent management
                file = await client.files.upload(file="data.csv")    # File management

        asyncio.run(main())
        ```

        ```python
        # FastAPI integration example
        from fastapi import FastAPI, UploadFile
        import moderatelyai_sdk

        app = FastAPI()

        @app.post("/upload")
        async def upload_file(file: UploadFile):
            async with moderatelyai_sdk.AsyncModeratelyAI() as client:
                uploaded = await client.files.upload(
                    file=await file.read(),
                    name=file.filename
                )
                return {"file_id": uploaded.file_id, "name": uploaded.name}
        ```

    Raises:
        AuthenticationError: If API key is invalid or missing.
        ValidationError: If required parameters are missing or invalid.
    """

    def __init__(
        self,
        *,
        team_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None] = None,
        max_retries: int = 2,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        """Initialize the async Moderately AI client.

        Args:
            team_id: The team ID to scope all API requests to. If not provided, will read from MODERATELY_TEAM_ID environment variable.
            api_key: Your API key. If not provided, will read from MODERATELY_API_KEY environment variable.
            base_url: Override the default base URL for the API. Defaults to https://api.moderately.ai.
            timeout: Request timeout in seconds. Defaults to 10 seconds.
            max_retries: Maximum number of retries. Defaults to 2.
            default_headers: Default headers to include with every request.
            default_query: Default query parameters to include with every request.
            http_client: Custom httpx async client instance. If provided, other HTTP options are ignored.

        Raises:
            ValueError: If no API key or team ID is provided via parameter or environment variable.
        """
        if api_key is None:
            api_key = os.environ.get("MODERATELY_API_KEY")

        if team_id is None:
            team_id = os.environ.get("MODERATELY_TEAM_ID")

        if api_key is None:
            raise ValueError(
                "The api_key client option must be set either by passing api_key to the client or by setting the MODERATELY_API_KEY environment variable"
            )

        if team_id is None:
            raise ValueError(
                "The team_id client option must be set either by passing team_id to the client or by setting the MODERATELY_TEAM_ID environment variable"
            )

        if base_url is None:
            base_url = "https://api.moderately.ai"

        if timeout is None:
            timeout = 10.0

        # Store team_id for automatic filtering
        self.team_id = team_id

        # Add team_ids filter to default query parameters for list endpoints
        if default_query is None:
            default_query = {}

        # Add teamIds as a default query parameter (API expects camelCase)
        default_query = {**default_query, "teamIds": [team_id]}

        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            team_id=team_id,
        )

        # Initialize async resource groups
        self.users = AsyncUsers(self)
        self.teams = AsyncTeams(self)
        self.agents = AsyncAgents(self)
        self.agent_executions = AsyncAgentExecutions(self)
        self.datasets = AsyncDatasets(self)
        self.pipelines = AsyncPipelines(self)
        self.pipeline_configuration_versions = AsyncPipelineConfigurationVersions(self)
        self.pipeline_executions = AsyncPipelineExecutions(self)
        self.files = AsyncFiles(self)

    async def _make_request(
        self,
        method: HTTPMethod,
        path: str,
        *,
        cast_type: type,
        body: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an asynchronous HTTP request."""
        return await self._request(
            method=method,
            path=path,
            cast_type=cast_type,
            body=body,
            options=options or {},
        )

    async def __aenter__(self) -> "AsyncModeratelyAI":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if hasattr(self, "_client"):
            await self._client.aclose()
