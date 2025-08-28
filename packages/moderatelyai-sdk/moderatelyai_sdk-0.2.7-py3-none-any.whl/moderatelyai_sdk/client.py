"""Synchronous client for the Moderately AI API."""

import logging
import os
from typing import Any, Dict, Optional, Union

import httpx

from ._base_client import BaseClient, RetryConfig
from .resources import (
    AgentExecutions,
    Agents,
    Datasets,
    Files,
    PipelineConfigurationVersions,
    PipelineExecutions,
    Pipelines,
    Teams,
    Users,
)
from .types import HTTPMethod

logger = logging.getLogger(__name__)


class ModeratelyAI(BaseClient):
    """Synchronous client for the Moderately AI API.

    The main client for interacting with the Moderately AI platform. Provides access
    to all platform resources through resource groups like files, datasets, agents,
    and pipelines. All operations are automatically scoped to your team.

    Attributes:
        users: User management operations
        teams: Team settings and information
        agents: AI agent management and execution
        agent_executions: Agent execution monitoring
        datasets: Dataset upload, management, and schema operations
        pipelines: Pipeline creation and configuration management
        pipeline_configuration_versions: Pipeline workflow configuration
        pipeline_executions: Pipeline execution and monitoring
        files: File upload, download, and management

    Args:
        api_key: Your API key. If not provided, reads from MODERATELY_API_KEY environment variable.
        team_id: Your team ID. If not provided, reads from MODERATELY_TEAM_ID environment variable.
        base_url: API base URL. Defaults to https://api.moderately.ai
        timeout: Request timeout in seconds. Defaults to 30.0.
        max_retries: Maximum retry attempts. Defaults to 3.
        retry_config: Custom retry configuration. Optional.
        default_headers: Additional headers to include in all requests. Optional.
        default_query: Additional query parameters to include in all requests. Optional.
        http_client: Custom HTTP client instance. Optional.

    Example:
        ```python
        import moderatelyai_sdk

        # Initialize with environment variables (recommended)
        client = moderatelyai_sdk.ModeratelyAI()  # reads MODERATELY_API_KEY and MODERATELY_TEAM_ID

        # Or initialize with explicit parameters
        client = moderatelyai_sdk.ModeratelyAI(
            team_id="your-team-id",
            api_key="your-api-key"
        )

        # Advanced configuration
        client = moderatelyai_sdk.ModeratelyAI(
            team_id="your-team-id",
            api_key="your-api-key",
            timeout=60,
            max_retries=5
        )

        # Use the client - all operations are automatically scoped to your team
        users = client.users.list()                    # User management
        dataset = client.datasets.create(name="Data")  # Dataset operations
        agents = client.agents.list()                  # AI agent management
        pipeline = client.pipelines.create(name="ML")  # Pipeline operations
        file = client.files.upload(file="data.csv")    # File management
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
        max_retries: int = 3,
        retry_config: Optional[RetryConfig] = None,
        default_headers: Optional[Dict[str, str]] = None,
        default_query: Optional[Dict[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        """Initialize the Moderately AI client.

        Args:
            team_id: The team ID to scope all API requests to. If not provided, will read from MODERATELY_TEAM_ID environment variable.
            api_key: Your API key. If not provided, will read from MODERATELY_API_KEY environment variable.
            base_url: Override the default base URL for the API. Defaults to https://api.moderately.ai.
            timeout: Request timeout in seconds. Defaults to 30 seconds.
            max_retries: Maximum number of retries. Defaults to 3.
            retry_config: Advanced retry configuration. If provided, max_retries is ignored.
            default_headers: Default headers to include with every request.
            default_query: Default query parameters to include with every request.
            http_client: Custom httpx client instance. If provided, other HTTP options are ignored.

        Raises:
            ValueError: If no API key or team ID is provided via parameter or environment variable.
        """
        if api_key is None:
            logger.debug(
                "No api_key provided, using MODERATELY_API_KEY from environment"
            )
            api_key = os.environ.get("MODERATELY_API_KEY")
            if not api_key:
                logger.error(
                    'You must provide either a "api_key" client option or set the MODERATELY_API_KEY environment variable'
                )
                raise ValueError(
                    "The api_key client option must be set either by passing api_key to the client or by setting the MODERATELY_API_KEY environment variable"
                )
        api_key_with_asterisk = api_key[:4] + "*" * (len(api_key) - 4)
        logger.debug(f"api key is set to {api_key_with_asterisk}")

        if team_id is None:
            logger.debug(
                "No team_id provided, using MODERATELY_TEAM_ID from environment"
            )
            team_id = os.environ.get("MODERATELY_TEAM_ID")
            if not team_id:
                logger.error(
                    'You must provide either a "team_id" client option or set the MODERATELY_TEAM_ID environment variable'
                )
                raise ValueError(
                    "The team_id client option must be set either by passing team_id to the client or by setting the MODERATELY_TEAM_ID environment variable"
                )
        logger.debug(f"team id is set to {team_id}")

        if base_url is None:
            base_url = os.environ.get(
                "MODERATELY_BASE_URL", "https://api.moderately.ai"
            )
        logger.debug(f"base url is set to {base_url}")

        if timeout is None:
            timeout = 30.0
        logger.debug(f"timeout is set to {timeout}")

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
            retry_config=retry_config,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            team_id=team_id,
        )

        # Initialize resource groups
        self.users = Users(self)
        self.teams = Teams(self)
        self.agents = Agents(self)
        self.agent_executions = AgentExecutions(self)
        self.datasets = Datasets(self)
        self.pipelines = Pipelines(self)
        self.pipeline_configuration_versions = PipelineConfigurationVersions(self)
        self.pipeline_executions = PipelineExecutions(self)
        self.files = Files(self)

    def _make_request(
        self,
        method: HTTPMethod,
        path: str,
        *,
        cast_type: type,
        body: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a synchronous HTTP request."""
        return self._request(
            method=method,
            path=path,
            cast_type=cast_type,
            body=body,
            options=options or {},
        )

    def __enter__(self) -> "ModeratelyAI":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if hasattr(self, "_client"):
            self._client.close()
