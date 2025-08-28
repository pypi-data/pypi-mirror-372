"""Tests for the AsyncModeratelyAI client."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from moderatelyai_sdk import AsyncModeratelyAI
from moderatelyai_sdk.exceptions import AuthenticationError


@pytest.mark.asyncio
class TestAsyncModeratelyAI:
    """Test cases for AsyncModeratelyAI client."""

    async def test_client_initialization(self):
        """Test async client initialization with default parameters."""
        client = AsyncModeratelyAI(team_id="test-team", api_key="test-key")

        assert client.api_key == "test-key"
        assert client.team_id == "test-team"
        assert client.base_url == "https://api.moderately.ai"

    async def test_client_context_manager(self):
        """Test client as async context manager."""
        async with AsyncModeratelyAI(team_id="test-team", api_key="test-key") as client:
            assert isinstance(client, AsyncModeratelyAI)

    @patch("moderatelyai_sdk.client_async.httpx.AsyncClient")
    async def test_dataset_list_success(self, mock_httpx_client):
        """Test successful dataset list request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"datasetId": "ds_123", "name": "Test Dataset"}],
            "pagination": {"page": 1, "total_items": 1}
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = AsyncModeratelyAI(team_id="test-team", api_key="test-key")
        result = await client.datasets.list()

        assert "items" in result
        assert len(result["items"]) == 1
        assert result["items"][0]["name"] == "Test Dataset"

    @patch("moderatelyai_sdk.client_async.httpx.AsyncClient")
    async def test_agent_create_success(self, mock_httpx_client):
        """Test successful agent creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "agent_123",
            "name": "Test Agent",
            "team_id": "test-team"
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = AsyncModeratelyAI(team_id="test-team", api_key="test-key")
        result = await client.agents.create(name="Test Agent")

        assert result["id"] == "agent_123"
        assert result["name"] == "Test Agent"
        assert result["team_id"] == "test-team"

    @patch("moderatelyai_sdk.client_async.httpx.AsyncClient")
    async def test_authentication_error(self, mock_httpx_client):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401

        mock_client_instance = AsyncMock()
        mock_client_instance.request.return_value = mock_response
        mock_httpx_client.return_value = mock_client_instance

        client = AsyncModeratelyAI(team_id="test-team", api_key="invalid-key")

        with pytest.raises(AuthenticationError):
            await client.users.list()

    def test_environment_variable_support(self):
        """Test initialization from environment variables."""
        with patch.dict("os.environ", {
            "MODERATELY_API_KEY": "env-api-key",
            "MODERATELY_TEAM_ID": "env-team-id"
        }):
            client = AsyncModeratelyAI()
            assert client.api_key == "env-api-key"
            assert client.team_id == "env-team-id"

    def test_missing_credentials_error(self):
        """Test error when credentials are missing."""
        with pytest.raises(ValueError, match="api_key.*must be set"):
            AsyncModeratelyAI(team_id="test-team")

        with pytest.raises(ValueError, match="team_id.*must be set"):
            AsyncModeratelyAI(api_key="test-key")


@pytest.mark.asyncio
async def test_async_dataset_model_rich_operations():
    """Test that async dataset models can be created (basic smoke test)."""
    from moderatelyai_sdk._base_client_async import AsyncBaseClient
    from moderatelyai_sdk.models.dataset_async import DatasetAsyncModel

    # Create a mock client
    mock_client = Mock(spec=AsyncBaseClient)

    # Create a dataset model with test data
    test_data = {
        "datasetId": "ds_123",
        "name": "Test Dataset",
        "teamId": "team_123",
        "createdAt": "2023-01-01T00:00:00Z",
        "updatedAt": "2023-01-01T00:00:00Z"
    }

    dataset = DatasetAsyncModel(test_data, mock_client)

    # Test properties work
    assert dataset.dataset_id == "ds_123"
    assert dataset.name == "Test Dataset"
    assert dataset.team_id == "team_123"

    # Test rich methods exist (we won't call them since they need real async client)
    assert hasattr(dataset, "upload_data")
    assert hasattr(dataset, "download_data")
    assert hasattr(dataset, "create_schema")
    assert hasattr(dataset, "create_schema_from_sample")

    # Test async methods are coroutines
    import inspect
    assert inspect.iscoroutinefunction(dataset.upload_data)
    assert inspect.iscoroutinefunction(dataset.download_data)
    assert inspect.iscoroutinefunction(dataset.create_schema)
