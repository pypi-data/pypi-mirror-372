"""Async files resource for the Moderately AI API."""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import aiofiles
import httpx

from ..exceptions import APIError
from ..models.file_async import FileAsyncModel
from ._base import AsyncBaseResource


class AsyncFiles(AsyncBaseResource):
    """Manage files in your teams (async version).

    All methods return FileAsyncModel instances which provide rich functionality
    for file operations like downloading, deleting, and checking file properties.

    Examples:
        ```python
        # List all files (returns raw data)
        files = await client.files.list()

        # Get a file with rich functionality
        file = await client.files.retrieve("file_123")

        # Upload a new file and get FileAsyncModel
        file = await client.files.upload(
            file_path="/path/to/document.pdf",
            name="Important Document"
        )

        # Use rich file operations
        if file.is_ready() and file.is_document():
            content = await file.download()  # Download to memory
            await file.download(path="./local_copy.pdf")  # Download to disk

        # Check file properties
        print(f"File: {file.name} ({file.file_size} bytes)")
        print(f"Type: {file.mime_type}, Extension: {file.get_extension()}")

        # Update file metadata
        file = await client.files.update(
            "file_123",
            name="Updated Document Name"
        )

        # Delete file using rich model
        await file.delete()
        ```
    """

    async def list(
        self,
        *,
        dataset_id: Optional[str] = None,
        status: Optional[str] = None,
        mime_type: Optional[str] = None,
        file_hashes: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
    ) -> Dict[str, Any]:
        """List all files with pagination.

        Note: Results are automatically filtered to the team specified in the client.

        Args:
            dataset_id: Filter files by dataset ID.
            status: Filter files by status (e.g., "uploaded", "processing", "ready", "error").
            mime_type: Filter files by MIME type (e.g., "text/csv", "application/pdf").
            file_hashes: Filter files by SHA256 hash. Can be a single hash string.
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page. Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Paginated list of files for the client's team.
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        if dataset_id is not None:
            query["dataset_id"] = dataset_id
        if status is not None:
            query["status"] = status
        if mime_type is not None:
            query["mime_type"] = mime_type
        if file_hashes is not None:
            query["fileHashes"] = file_hashes

        response = await self._get("/files", options={"query": query})

        # Convert items to FileAsyncModel instances
        if "items" in response:
            response["items"] = [
                FileAsyncModel(item, self._client) for item in response["items"]
            ]

        return response

    async def retrieve(self, file_id: str) -> FileAsyncModel:
        """Retrieve a specific file by ID.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            The file model with rich functionality.

        Raises:
            NotFoundError: If the file doesn't exist.
        """
        data = await self._get(f"/files/{file_id}")
        return FileAsyncModel(data, self._client)

    async def upload(
        self,
        file: Union[str, Path, bytes, Any],
        *,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> FileAsyncModel:
        """Upload a file using secure presigned URL workflow (async version).

        Accepts files in multiple convenient formats and handles all the complexity
        of secure upload automatically, including SHA256 hashing, MIME type detection,
        and presigned URL generation.

        Supported file inputs:
        - File paths (str or Path objects)
        - Raw bytes data
        - File-like objects with .read() method (buffers, streams)

        Args:
            file: The file to upload in any supported format
            name: Custom display name for the file. If not provided, uses the
                 filename from path or defaults to a generic name.
            metadata: Additional metadata dictionary to store with the file.
            **kwargs: Additional file properties.

        Returns:
            FileAsyncModel instance representing the uploaded file with rich async operations.

        Raises:
            ValueError: If file is invalid, not found, or unsupported format.
            APIError: If upload process fails at any step.
            NotFoundError: If the dataset doesn't exist.
        """

        # Step 1: Process the file input to get bytes and metadata
        file_data: bytes
        file_name: str

        if isinstance(file, (str, Path)):
            # Handle file path
            file_path = Path(file)
            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()

            # If custom name provided, preserve the original extension
            if name:
                file_extension = file_path.suffix
                if not name.endswith(file_extension):
                    file_name = f"{name}{file_extension}"
                else:
                    file_name = name
            else:
                file_name = file_path.name

        elif isinstance(file, bytes):
            # Handle raw bytes
            file_data = file
            file_name = name or "uploaded_file"

        elif hasattr(file, "read"):
            # Handle file-like object (buffer)
            file_data = file.read()
            if isinstance(file_data, str):
                file_data = file_data.encode("utf-8")

            # Try to get filename from buffer object
            buffer_name = getattr(file, "name", None)
            if buffer_name and not name:
                file_name = Path(buffer_name).name
            else:
                file_name = name or "uploaded_file"

        else:
            raise ValueError(
                f"Unsupported file type: {type(file)}. Must be str, Path, bytes, or file-like object."
            )

        # Step 2: Calculate file properties
        import hashlib
        import mimetypes

        file_size = len(file_data)
        file_hash = hashlib.sha256(file_data).hexdigest()

        # Auto-detect MIME type
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = "application/octet-stream"

        # Step 3: Get presigned upload URL
        upload_request = {
            "fileName": file_name,
            "fileSize": file_size,
            "fileHash": file_hash,
            "mimeType": mime_type,
            "teamId": self._client.team_id,
        }

        if metadata:
            upload_request["metadata"] = metadata

        # Get the presigned URL
        upload_response = await self._post("/files/upload-url", body=upload_request)

        file_info = upload_response["file"]
        presigned_url = upload_response["uploadUrl"]
        file_id = file_info["fileId"]

        # Step 4: Upload file to presigned URL
        try:
            async with httpx.AsyncClient() as client:
                upload_result = await client.put(
                    presigned_url,
                    content=file_data,
                    headers={"Content-Type": mime_type},
                )
                upload_result.raise_for_status()
        except Exception as e:
            raise APIError(f"Failed to upload file to presigned URL: {e}") from e

        # Step 5: Mark upload as complete
        try:
            complete_response = await self._post(
                f"/files/{file_id}/complete",
                body={"fileSize": file_size, "fileHash": file_hash},
            )
            return FileAsyncModel(complete_response, self._client)
        except Exception as e:
            raise APIError(f"Failed to complete file upload: {e}") from e

    async def update(
        self,
        file_id: str,
        *,
        name: Optional[str] = None,
        dataset_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> FileAsyncModel:
        """Update an existing file's metadata.

        Args:
            file_id: The ID of the file to update.
            name: New file name.
            dataset_id: New dataset ID to associate with.
            metadata: Updated metadata.
            **kwargs: Additional properties to update.

        Returns:
            The updated file model with rich functionality.

        Raises:
            NotFoundError: If the file doesn't exist.
            ValidationError: If the request data is invalid.
        """
        body = {**kwargs}
        if name is not None:
            body["name"] = name
        if dataset_id is not None:
            body["dataset_id"] = dataset_id
        if metadata is not None:
            body["metadata"] = metadata

        data = await self._patch(f"/files/{file_id}", body=body)
        return FileAsyncModel(data, self._client)

    async def delete(self, file_id: str) -> None:
        """Delete a file.

        Args:
            file_id: The ID of the file to delete.

        Raises:
            NotFoundError: If the file doesn't exist.
        """
        await self._delete(f"/files/{file_id}")

    async def download(self, file_id: str) -> bytes:
        """Download file content.

        Args:
            file_id: The ID of the file to download.

        Returns:
            The file content as bytes.

        Raises:
            NotFoundError: If the file doesn't exist.
        """
        # This would typically return the raw file content
        # For now, we'll make a request to a download endpoint
        response = await self._client._make_request(
            "GET", f"/files/{file_id}/download", cast_type=dict
        )

        # In a real implementation, this might return binary data directly
        # or a download URL that needs to be fetched separately
        if isinstance(response, dict) and "downloadUrl" in response:
            # If API returns a download URL, we'd need to fetch it
            import httpx

            async with httpx.AsyncClient() as client:
                download_response = await client.get(response["downloadUrl"])
                return download_response.content
        elif isinstance(response, dict) and "content" in response:
            # If API returns base64 encoded content
            import base64

            return base64.b64decode(response["content"])
        else:
            # Assume response is already binary data
            return response if isinstance(response, bytes) else str(response).encode()

    async def get_upload_url(
        self,
        *,
        filename: str,
        file_size: int,
        mime_type: Optional[str] = None,
        dataset_id: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Get a presigned upload URL for large file uploads.

        This is useful for uploading large files directly to cloud storage.

        Args:
            filename: Name of the file to upload.
            file_size: Size of the file in bytes.
            mime_type: MIME type of the file.
            dataset_id: Optional dataset ID to associate the file with.
            **kwargs: Additional upload parameters.

        Returns:
            Upload URL and metadata.

        Raises:
            ValidationError: If the request data is invalid.
        """
        body = {
            "filename": filename,
            "file_size": file_size,
            "team_id": self._client.team_id,
            **kwargs,
        }

        if mime_type is not None:
            body["mime_type"] = mime_type
        if dataset_id is not None:
            body["dataset_id"] = dataset_id

        return await self._client._make_request(
            "POST", "/files/upload-url", cast_type=dict, body=body
        )
