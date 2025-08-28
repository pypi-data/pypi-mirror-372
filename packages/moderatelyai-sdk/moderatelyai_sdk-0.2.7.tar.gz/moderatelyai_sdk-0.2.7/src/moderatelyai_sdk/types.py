"""Type definitions for the Moderately AI SDK."""

from typing import Any, Dict, List, Literal, Optional, Union

from typing_extensions import TypedDict

# HTTP Method types
HTTPMethod = Literal["GET", "POST", "PATCH", "PUT", "DELETE"]

# JSON serializable types
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class APIResponse(TypedDict):
    """Standard API response structure."""

    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    message: Optional[str]


class PaginationInfo(TypedDict):
    """Pagination metadata for list responses."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next_page: bool
    has_previous_page: bool


class PaginatedResponse(TypedDict):
    """Response structure for paginated endpoints."""

    items: List[Dict[str, Any]]
    pagination: PaginationInfo


class ErrorDetail(TypedDict):
    """Detailed error information for validation errors."""

    field: str
    message: str
    value: Optional[Any]


class APIError(TypedDict):
    """Error response structure."""

    code: str
    message: str
    details: Optional[List[ErrorDetail]]
    path: Optional[str]
    timestamp: Optional[str]
    request_id: Optional[str]


# Resource types based on the API
class User(TypedDict, total=False):
    """User resource type."""

    userId: str
    fullName: str
    nickname: Optional[str]
    createdAt: str
    updatedAt: str


class Team(TypedDict, total=False):
    """Team resource type."""

    teamId: str
    name: str
    createdAt: str
    updatedAt: str


class Agent(TypedDict, total=False):
    """Agent resource type."""

    agentId: str
    teamId: str
    name: str
    description: Optional[str]
    createdAt: str
    updatedAt: str
    lastRunAt: Optional[str]
    totalRuns: float
    successfulRuns: float
    successRate: float


class AgentExecution(TypedDict, total=False):
    """Agent execution resource type."""

    agentExecutionId: str
    agentConfigurationVersionId: str
    agentInput: Optional[Dict[str, Any]]
    agentInputSchema: Optional[Any]
    agentInputSummary: Optional[str]
    agentOutput: Optional[Dict[str, Any]]
    agentOutputSchema: Optional[Any]
    agentOutputSummary: Optional[str]
    status: str
    thoughts: List[Dict[str, Any]]
    maxActions: Optional[int]
    currentStep: Optional[int]
    planningInterval: Optional[int]
    createdAt: str
    updatedAt: str
    startedAt: Optional[str]
    completedAt: Optional[str]
    failedAt: Optional[str]
    cancelledAt: Optional[str]
    pausedAt: Optional[str]


class Dataset(TypedDict, total=False):
    """Dataset resource type."""

    dataset_id: str  # API uses datasetId, but kept snake_case for SDK consistency
    name: str
    description: Optional[str]
    team_id: str
    record_count: Optional[int]  # Number of records in current data version
    total_size_bytes: Optional[int]  # Total size in bytes
    current_schema_version_id: Optional[str]  # Current schema version ID
    current_data_version_id: Optional[str]  # Current data version ID
    active_data_schema_version_id: Optional[str]  # Active schema version ID
    active_data_version_id: Optional[str]  # Active data version ID
    processing_status: Optional[str]  # Processing status: completed, failed, in_progress, needs-processing
    created_at: str
    updated_at: str


class Pipeline(TypedDict, total=False):
    """Pipeline resource type - basic pipeline metadata."""

    pipelineId: str
    teamId: str
    name: str
    description: Optional[str]
    createdAt: Optional[str]
    updatedAt: Optional[str]
    lastRunAt: Optional[str]
    totalRuns: float
    successfulRuns: float
    successRate: float


class PipelineConfigurationVersion(TypedDict, total=False):
    """Pipeline configuration version resource type - contains the actual pipeline logic."""

    pipelineConfigurationVersionId: str
    pipelineId: str
    configuration: Dict[str, Any]
    createdAt: Optional[str]
    updatedAt: Optional[str]
    status: Optional[str]
    version: Optional[str]


class PipelineExecution(TypedDict, total=False):
    """Pipeline execution resource type - runtime execution instances."""

    pipelineExecutionId: str
    pipelineConfigurationVersionId: str
    pipelineInput: Dict[str, Any]
    pipelineInputSummary: str
    pipelineOutput: Optional[Dict[str, Any]]
    pipelineOutputSummary: Optional[str]
    status: str  # pending, running, completed, failed, cancelled, paused
    progressData: Dict[str, Any]
    pipelineOutputFileUri: Optional[str]
    currentStep: Optional[int]
    totalSteps: Optional[int]
    createdAt: Optional[str]
    updatedAt: Optional[str]
    startedAt: Optional[str]
    completedAt: Optional[str]
    failedAt: Optional[str]
    cancelledAt: Optional[str]
    pausedAt: Optional[str]


class File(TypedDict, total=False):
    """File resource type."""

    fileId: str
    fileName: str
    originalName: Optional[str]
    teamId: str
    datasetId: Optional[str]
    fileSize: Optional[int]
    mimeType: Optional[str]
    uploadStatus: Optional[str]
    uploadUrl: Optional[str]
    downloadUrl: Optional[str]
    metadata: Optional[Dict[str, Any]]
    createdAt: str
    updatedAt: str
