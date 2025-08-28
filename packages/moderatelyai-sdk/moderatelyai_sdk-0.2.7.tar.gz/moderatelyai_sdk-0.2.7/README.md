# Moderately AI Python SDK

The official Python SDK for the Moderately AI platform, providing programmatic access to agents, datasets, pipelines, and team management.

## Features

- **Python 3.8+ Support**: Compatible with Python 3.8 and later versions
- **Type Safety**: Full type annotations with mypy support
- **Async/Await**: Built-in support for asynchronous operations
- **Team-scoped Operations**: Automatic filtering and scoping to your team
- **Resource Management**: Agents, datasets, pipelines, files, and users
- **Error Handling**: Comprehensive exception handling for different error scenarios
- **Rate Limiting**: Built-in rate limit handling and retry logic
- **Modern Tooling**: Uses PDM for dependency management, Ruff for linting, and pytest for testing

## Installation

```bash
pip install moderatelyai-sdk
```

## Quick Start

### Synchronous Client

```python
import moderatelyai_sdk

# Initialize with environment variables (recommended)
client = moderatelyai_sdk.ModeratelyAI()  # reads MODERATELY_API_KEY and MODERATELY_TEAM_ID

# Or initialize with explicit parameters
client = moderatelyai_sdk.ModeratelyAI(
    team_id="your-team-id",
    api_key="your-api-key"
)

# Use the client - all operations are automatically scoped to your team
users = client.users.list()
dataset = client.datasets.create(name="My Dataset")
agents = client.agents.list()
```

### Asynchronous Client

```python
import asyncio
import moderatelyai_sdk

async def main():
    # Initialize async client
    async with moderatelyai_sdk.AsyncModeratelyAI() as client:
        # Same operations, just with await
        users = await client.users.list()
        dataset = await client.datasets.create(name="My Dataset")
        agents = await client.agents.list()

asyncio.run(main())
```

## Usage

### Working with Datasets

```python
from moderatelyai_sdk import ModeratelyAI

client = ModeratelyAI(team_id="your-team-id", api_key="your-api-key")

# Create a dataset
dataset = client.datasets.create(
    name="Customer Data",
    description="Customer interaction dataset"
)

# Upload data to the dataset
version = dataset.upload_data("/path/to/data.csv")
print(f"Uploaded version {version.version_no} with {version.row_count} rows")

# List all datasets
datasets = client.datasets.list()
```

### Working with Agents

```python
# List all agents in your team
agents = client.agents.list()

# Create and run an agent execution
execution = client.agent_executions.create(
    agent_id="agent_123",
    input_data={"query": "Process this data"}
)
```

### Working with Pipelines

```python
# Create a pipeline
pipeline = client.pipelines.create(
    name="Document Processing Pipeline",
    description="Processes legal documents and extracts key information"
)

# Create a configuration version with workflow logic
config_version = client.pipeline_configuration_versions.create(
    pipeline_id=pipeline["pipelineId"],
    configuration={
        "id": "doc-processor",
        "name": "Document Processor",
        "version": "1.0.0",
        "blocks": {
            "input": {
                "id": "input",
                "type": "input",
                "config": {"json_schema": {"type": "object"}}
            },
            "llm": {
                "id": "llm",
                "type": "llm", 
                "config": {
                    "provider": "anthropic",
                    "model": "small",
                    "temperature": 0.2
                }
            },
            "output": {
                "id": "output",
                "type": "output",
                "config": {"name": "results"}
            }
        }
    }
)

# Execute the pipeline
execution = client.pipeline_executions.create(
    pipeline_configuration_version_id=config_version["pipelineConfigurationVersionId"],
    pipeline_input={"documents": ["doc1.pdf", "doc2.pdf"]},
    pipeline_input_summary="Process 2 legal documents"
)

# Monitor execution status
status = client.pipeline_executions.retrieve(execution["pipelineExecutionId"])
print(f"Execution status: {status['status']}")

# Get execution results when completed
if status["status"] == "completed":
    output = client.pipeline_executions.get_output(execution["pipelineExecutionId"]) 
    print(f"Results: {output}")

# List all pipelines in your team
pipelines = client.pipelines.list()
```

### Using Context Manager

```python
from moderatelyai_sdk import ModeratelyAI

with ModeratelyAI(team_id="your-team-id", api_key="your-api-key") as client:
    users = client.users.list()
    print(f"Found {len(users)} users")
```

### Async Support

The SDK provides full async support with `AsyncModeratelyAI`. All methods have identical interfaces - just add `await`:

```python
import asyncio
from moderatelyai_sdk import AsyncModeratelyAI

async def main():
    # Use async context manager (recommended)
    async with AsyncModeratelyAI() as client:  # reads environment variables
        # All the same operations, just with await
        users = await client.users.list()
        dataset = await client.datasets.create(name="Async Dataset")
        agents = await client.agents.list()
        
        # File operations work the same way
        file = await client.files.upload(
            file="data.csv",
            name="Training Data"
        )
        
        if file.is_ready():
            content = await file.download()
            await file.delete()

asyncio.run(main())
```

### File Operations

The SDK provides rich file upload, download, and management capabilities with automatic presigned URL handling:

```python
from moderatelyai_sdk import ModeratelyAI

client = ModeratelyAI()

# Upload a file (multiple input types supported)
file = client.files.upload(
    file="/path/to/document.pdf",      # File path
    name="Important Document",
    metadata={"category": "legal", "priority": "high"}
)

# Upload from bytes or file-like objects also supported
with open("data.csv", "rb") as f:
    file = client.files.upload(
        file=f.read(),                 # Raw bytes
        name="Dataset"
    )

# Rich file model with convenience methods
print(f"File: {file.name} ({file.file_size} bytes)")
print(f"Type: {file.mime_type}")
print(f"Ready: {file.is_ready()}")
print(f"Is CSV: {file.is_csv()}")
print(f"Is Document: {file.is_document()}")

# Download files
content = file.download()                    # Download to memory
file.download(path="./local_copy.pdf")       # Download to disk

# List files with filtering
files_response = client.files.list(
    mime_type="application/pdf",
    page_size=20,
    order_direction="desc"
)

files = files_response["items"]  # List of FileModel instances
for file in files:
    if file.is_ready():
        print(f"Ready: {file.name} ({file.file_size} bytes)")

# Delete files
file.delete()  # Permanent deletion
```

#### Async File Operations

File operations work identically in async mode:

```python
import asyncio
from moderatelyai_sdk import AsyncModeratelyAI

async def file_operations():
    async with AsyncModeratelyAI() as client:
        # Same interface, just add await
        file = await client.files.upload(
            file="document.pdf",
            name="Async Upload"
        )
        
        # All the same rich methods available
        if file.is_ready() and file.is_document():
            content = await file.download()      # Download to memory  
            await file.download(path="./copy.pdf")  # Download to disk
            await file.delete()                  # Clean up

asyncio.run(file_operations())
```

### Error Handling

```python
from moderatelyai_sdk import ModeratelyAI, APIError, AuthenticationError

client = ModeratelyAI(team_id="your-team-id", api_key="your-api-key")

try:
    dataset = client.datasets.create(name="Test Dataset")
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
    if hasattr(e, 'status_code'):
        print(f"Status code: {e.status_code}")
```

## Configuration

The client can be configured with various options:

```python
client = ModeratelyAI(
    team_id="your-team-id",
    api_key="your-api-key",
    base_url="https://api.moderately.ai",  # Custom API endpoint
    timeout=30,                            # Request timeout in seconds
    max_retries=3                          # Maximum retry attempts
)
```

## Examples

Complete working examples are available in the `examples/` directory:

- **[File Operations](examples/01-file-operations/)** - Complete file upload, download, and management workflows
  - `main.py` - Synchronous file operations example  
  - `main_async.py` - Asynchronous file operations example
  - Demonstrates upload, list, download, and delete operations
  - Shows both FileModel and resource-level approaches
  - Includes REST API to SDK method mappings

To run the examples:
```bash
cd examples/01-file-operations
dotenvx run -- python main.py        # Sync version
dotenvx run -- python main_async.py  # Async version
```

## Development

This project uses PDM for dependency management. To set up the development environment:

```bash
# Install PDM
pip install pdm

# Install dependencies
pdm install

# Install pre-commit hooks
pdm run pre-commit install

# Run tests
pdm run pytest

# Run linting
pdm run ruff check .
pdm run ruff format .

# Type checking
pdm run mypy src/
```

## API Reference

### ModeratelyAI

The main client class for interacting with the Moderately AI API.

### AsyncModeratelyAI  

The async client class with identical interface to `ModeratelyAI`. All methods are async and return awaitable objects.

#### Resource Groups

- `client.users`: Manage users in your team
- `client.teams`: Manage team settings and information
- `client.agents`: Manage AI agents
- `client.agent_executions`: Create and monitor agent executions
- `client.datasets`: Manage datasets with rich functionality (upload, download, schema management)
- `client.pipelines`: Manage pipeline metadata (create, update, delete pipelines)
- `client.pipeline_configuration_versions`: Manage pipeline workflow configurations and logic
- `client.pipeline_executions`: Execute pipelines and monitor execution status
- `client.files`: Upload and manage files

### Exceptions

- `ModeratelyAIError`: Base exception class
- `APIError`: Raised for API-related errors
- `AuthenticationError`: Raised for authentication failures
- `ConflictError`: Raised for resource conflicts
- `NotFoundError`: Raised when resources are not found
- `RateLimitError`: Raised when rate limits are exceeded
- `TimeoutError`: Raised for request timeouts
- `UnprocessableEntityError`: Raised for validation errors
- `ValidationError`: Raised for input validation errors

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please visit our [GitHub repository](https://github.com/moderately-ai/platform-sdk) or contact us at sdk@moderately.ai.