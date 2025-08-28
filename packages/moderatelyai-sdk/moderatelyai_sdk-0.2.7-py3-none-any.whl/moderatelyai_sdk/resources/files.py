"""Files resource for the Moderately AI API."""

import base64
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx

from ..exceptions import APIError
from ..models.file import FileModel
from ._base import BaseResource


class Files(BaseResource):
    """Manage files in your team.

    The Files resource provides methods for uploading, downloading, listing, and
    managing files. All methods return FileModel instances which provide rich
    functionality for file operations.

    Key Features:
    - Upload files with automatic MIME type detection
    - Download files to memory or disk
    - List and filter files with pagination
    - Rich file type detection (CSV, images, documents, etc.)
    - Automatic presigned URL handling for secure transfers

    Examples:
        ```python
        # Upload a file and get a FileModel instance
        file = client.files.upload(
            file="/path/to/data.csv",
            name="Dataset"
        )

        # Use rich FileModel methods
        if file.is_ready() and file.is_csv():
            content = file.download()  # Download to memory
            file.download(path="./local_copy.csv")  # Download to disk

        # List files with filtering
        files_response = client.files.list(
            mime_type="text/csv",
            page_size=20
        )
        csv_files = files_response["items"]  # List of FileModel instances

        # Get a specific file
        file = client.files.retrieve("file_123")
        print(f"File: {file.name} ({file.file_size} bytes)")

        # Delete files
        file.delete()  # Using FileModel method
        # OR
        client.files.delete("file_123")  # Using resource method
        ```
    """

    def list(
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
        """List all files with pagination and filtering.

        Returns a paginated response containing FileModel instances. Results are
        automatically filtered to the team specified in the client configuration.

        Args:
            dataset_id: Filter files by dataset ID.
            status: Filter files by status (e.g., "completed", "processing", "error").
            mime_type: Filter files by MIME type (e.g., "text/csv", "application/pdf").
            file_hashes: Filter files by SHA256 hash. Can be a single hash string.
            page: Page number (1-based). Defaults to 1.
            page_size: Number of items per page (max 100). Defaults to 10.
            order_by: Field to sort by. Defaults to "created_at".
            order_direction: Sort direction ("asc" or "desc"). Defaults to "desc".

        Returns:
            Dictionary with "items" (list of FileModel instances) and "pagination" info.

        Example:
            ```python
            # List recent CSV files
            response = client.files.list(
                mime_type="text/csv",
                page_size=20,
                order_direction="desc"
            )

            csv_files = response["items"]  # List of FileModel instances
            for file in csv_files:
                if file.is_ready():
                    print(f"Ready: {file.name} ({file.file_size} bytes)")
            ```
        """
        query = {
            "page": page,
            "page_size": page_size,
            "order_by": order_by,
            "order_direction": order_direction,
        }
        # Don't add team_ids here since it's handled by default_query in client
        if dataset_id is not None:
            query["dataset_id"] = dataset_id
        if status is not None:
            query["status"] = status
        if mime_type is not None:
            query["mime_type"] = mime_type
        if file_hashes is not None:
            query["fileHashes"] = file_hashes

        response = self._get(
            "/files",
            options={"query": query},
        )

        # Convert items to FileModel instances
        if "items" in response:
            response["items"] = [
                FileModel(item, self._client) for item in response["items"]
            ]

        return response

    def retrieve(self, file_id: str) -> FileModel:
        """Retrieve a specific file by ID.

        Args:
            file_id: The ID of the file to retrieve.

        Returns:
            FileModel instance with rich file operations.

        Raises:
            NotFoundError: If the file doesn't exist.

        Example:
            ```python
            file = client.files.retrieve("file_123")
            print(f"File: {file.name} ({file.mime_type})")

            if file.is_ready():
                content = file.download()
            ```
        """
        data = self._get(f"/files/{file_id}")
        return FileModel(data, self._client)

    def upload(
        self,
        file: Union[str, Path, bytes, Any],
        *,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> FileModel:
        """Upload a file using secure presigned URL workflow.

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
            FileModel instance representing the uploaded file with rich operations.

        Raises:
            ValueError: If file is invalid, not found, or unsupported format.
            APIError: If upload process fails at any step.

        Examples:
            ```python
            # Upload from file path
            file = client.files.upload("/path/to/document.pdf")

            # Upload with custom name and metadata
            file = client.files.upload(
                file="data.csv",
                name="Customer Data",
                metadata={"category": "sales", "quarter": "Q1"}
            )

            # Upload raw bytes
            with open("image.jpg", "rb") as f:
                file = client.files.upload(
                    file=f.read(),
                    name="Profile Picture"
                )

            # Upload from file-like object
            import io
            buffer = io.BytesIO(b"Hello, World!")
            file = client.files.upload(buffer, name="greeting.txt")

            # Use the returned FileModel
            if file.is_ready():
                print(f"Uploaded: {file.name} ({file.file_size} bytes)")
            ```
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
        upload_response = self._post("/files/upload-url", body=upload_request)

        file_info = upload_response["file"]
        presigned_url = upload_response["uploadUrl"]
        file_id = file_info["fileId"]

        # Step 4: Upload file to presigned URL
        try:
            with httpx.Client() as client:
                upload_result = client.put(
                    presigned_url,
                    content=file_data,
                    headers={"Content-Type": mime_type},
                )
                upload_result.raise_for_status()
        except Exception as e:
            raise APIError(f"Failed to upload file to presigned URL: {e}") from e

        # Step 5: Mark upload as complete
        try:
            complete_response = self._post(
                f"/files/{file_id}/complete",
                body={"fileSize": file_size, "fileHash": file_hash},
            )
            return FileModel(complete_response, self._client)
        except Exception as e:
            raise APIError(f"Failed to complete file upload: {e}") from e


    def delete(self, file_id: str) -> None:
        """Delete a file permanently.

        This operation cannot be undone. The file will be removed from both
        the database and cloud storage. Consider using FileModel.delete()
        for better ergonomics.

        Args:
            file_id: The ID of the file to delete.

        Raises:
            NotFoundError: If the file doesn't exist.
            APIError: If deletion fails.

        Example:
            ```python
            # Delete using resource method
            client.files.delete("file_123")

            # OR delete using FileModel (recommended)
            file = client.files.retrieve("file_123")
            file.delete()
            ```
        """
        self._delete(f"/files/{file_id}")

    def download(
        self, file_id: str, *, path: Optional[Union[str, Path]] = None
    ) -> Optional[bytes]:
        """Download file content.

        Note: Consider using FileModel.download() instead for better ergonomics:
            file = client.files.retrieve(file_id)
            content = file.download(path=path)

        Args:
            file_id: The ID of the file to download.
            path: Optional path to save the file. If provided, saves to this location.
                 If not provided, returns the file content as bytes.

        Returns:
            If path is provided: None (file is saved to disk)
            If path is not provided: The file content as bytes

        Raises:
            NotFoundError: If the file doesn't exist.
            IOError: If unable to write to the specified path.
        """
        # Get the file content from the API
        response = self._get(f"/files/{file_id}/download")

        # Parse the response to get file content
        file_data: bytes
        if isinstance(response, dict) and "downloadUrl" in response:
            # If API returns a download URL, we need to fetch it
            try:
                with httpx.Client() as client:
                    download_response = client.get(response["downloadUrl"])
                    download_response.raise_for_status()
                    file_data = download_response.content
            except httpx.HTTPError as e:
                raise APIError(f"Failed to download file from URL: {e}") from e
        elif isinstance(response, dict) and "content" in response:
            # If API returns base64 encoded content
            file_data = base64.b64decode(response["content"])
        else:
            # Assume response is already binary data
            file_data = (
                response if isinstance(response, bytes) else str(response).encode()
            )

        # Save to file or return bytes
        if path is not None:
            file_path = Path(path)
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(file_data)
            return None
        else:
            return file_data
