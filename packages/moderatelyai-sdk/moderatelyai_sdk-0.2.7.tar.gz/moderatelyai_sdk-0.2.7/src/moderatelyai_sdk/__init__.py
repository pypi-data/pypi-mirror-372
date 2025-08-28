"""Moderately AI Python SDK - First-class API client for the Moderately AI platform."""

__version__ = "0.2.7"
__author__ = "Moderately AI"
__email__ = "sdk@moderately.ai"

from ._base_client import RetryConfig
from .client import ModeratelyAI
from .client_async import AsyncModeratelyAI
from .exceptions import (
    APIError,
    AuthenticationError,
    ConflictError,
    ModeratelyAIError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    UnprocessableEntityError,
    ValidationError,
)
from .models import (
    DatasetDataVersionModel,
    DatasetModel,
    DatasetSchemaVersionModel,
    FileAsyncModel,
    FileModel,
    SchemaBuilder,
    UserAsyncModel,
    UserModel,
)
from .models.dataset_async import DatasetAsyncModel, DatasetDataVersionAsyncModel
from .models.dataset_schema_version_async import (
    AsyncSchemaBuilder,
    DatasetSchemaVersionAsyncModel,
)
from .models.pipeline_async import PipelineAsyncModel
from .models.pipeline_configuration_version_async import PipelineConfigurationVersionAsyncModel
from .models.pipeline_execution_async import PipelineExecutionAsyncModel
from .types import (
    APIResponse,
    Pipeline,
    PipelineConfigurationVersion,
    PipelineExecution,
)

__all__ = [
    # Main clients
    "ModeratelyAI",
    "AsyncModeratelyAI",
    # Configuration
    "RetryConfig",
    # Sync Models
    "DatasetModel",
    "DatasetDataVersionModel",
    "DatasetSchemaVersionModel",
    "SchemaBuilder",
    "FileModel",
    "UserModel",
    # Async Models
    "DatasetAsyncModel",
    "DatasetDataVersionAsyncModel",
    "DatasetSchemaVersionAsyncModel",
    "AsyncSchemaBuilder",
    "FileAsyncModel",
    "UserAsyncModel",
    "PipelineAsyncModel",
    "PipelineConfigurationVersionAsyncModel",
    "PipelineExecutionAsyncModel",
    # Exceptions
    "ModeratelyAIError",
    "APIError",
    "AuthenticationError",
    "ConflictError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "UnprocessableEntityError",
    "ValidationError",
    # Types
    "APIResponse",
    "Pipeline",
    "PipelineConfigurationVersion",
    "PipelineExecution",
]
