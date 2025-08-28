"""File model with rich functionality for file operations.

This module provides the FileModel class, which represents a file with rich
functionality for file operations like downloading, deleting, and checking
file properties.

Example:
    ```python
    from moderatelyai_sdk import ModeratelyAI

    client = ModeratelyAI(api_key="your_key", team_id="your_team")

    # Upload a file and get a FileModel instance
    file = client.files.upload("document.pdf", name="Important Document")

    # Use rich file operations
    if file.is_ready() and file.is_document():
        content = file.download()  # Download to memory
        file.download(path="./local_copy.pdf")  # Download to disk

    # Check file properties
    print(f"File: {file.name} ({file.file_size} bytes)")
    print(f"Type: {file.mime_type}, Extension: {file.get_extension()}")

    # Delete when done
    file.delete()
    ```
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx

from ..exceptions import APIError
from ._base import BaseModel


class FileModel(BaseModel):
    """Model representing a file with rich file operations.

    FileModel provides a high-level interface for working with files in the
    Moderately AI platform. Instead of working with raw dictionaries, you get
    a rich object with methods for common file operations.

    This class is returned by file operations like:
    - `client.files.upload()`
    - `client.files.retrieve()`
    - `client.files.list()` (returns list of FileModel instances)

    Attributes:
        file_id: Unique identifier for the file
        name: Display name of the file
        original_name: Original filename when uploaded
        mime_type: MIME type (e.g., "text/csv", "application/pdf")
        file_size: Size in bytes
        file_hash: SHA256 hash of file content
        team_id: Team that owns this file
        dataset_id: Associated dataset ID (if any)
        status: Upload/processing status
        metadata: Additional file metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp

    Example:
        ```python
        # Get a file and check its properties
        file = client.files.retrieve("file_123")

        if file.is_csv() and file.is_ready():
            print(f"Ready CSV file: {file.name} ({file.file_size} bytes)")

            # Download to memory
            content = file.download()

            # Or download to disk
            file.download(path="./data.csv")
        ```
    """

    @property
    def file_id(self) -> str:
        """The unique identifier for this file."""
        return self._data["fileId"]

    @property
    def name(self) -> str:
        """The file name."""
        return self._data["fileName"]

    @property
    def original_name(self) -> Optional[str]:
        """The original filename when uploaded."""
        return self._data.get("originalName")

    @property
    def mime_type(self) -> str:
        """The MIME type of the file."""
        return self._data["mimeType"]

    @property
    def file_size(self) -> Optional[int]:
        """The size of the file in bytes."""
        return self._data.get("fileSize")

    @property
    def file_hash(self) -> Optional[str]:
        """The SHA256 hash of the file."""
        return self._data.get("fileHash")

    @property
    def team_id(self) -> str:
        """The team this file belongs to."""
        return self._data["teamId"]

    @property
    def dataset_id(self) -> Optional[str]:
        """The dataset this file is associated with, if any."""
        return self._data.get("datasetId")

    @property
    def status(self) -> str:
        """The file status (uploaded, processing, ready, error)."""
        return self._data.get("uploadStatus", "unknown")

    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        """Additional metadata for the file."""
        return self._data.get("metadata")

    @property
    def created_at(self) -> str:
        """When this file was created."""
        return self._data["createdAt"]

    @property
    def updated_at(self) -> str:
        """When this file was last updated."""
        return self._data["updatedAt"]

    def download(self, *, path: Optional[Union[str, Path]] = None) -> Optional[bytes]:
        """Download the file content.

        Downloads the file content either to memory or to a local file. This method
        handles the presigned URL workflow automatically and creates parent directories
        as needed when saving to disk.

        Args:
            path: Optional path to save the file. If provided, saves to this location
                 and creates parent directories if they don't exist. If not provided,
                 returns the file content as bytes.

        Returns:
            If path is provided: None (file is saved to disk)
            If path is not provided: The file content as bytes

        Raises:
            APIError: If the download fails or the file is not ready
            IOError: If unable to write to the specified path

        Example:
            ```python
            # Download to memory
            content = file.download()
            print(f"Downloaded {len(content)} bytes")

            # Download to disk
            file.download(path="./downloads/myfile.pdf")

            # Download with automatic directory creation
            file.download(path="./new_folder/subfolder/file.csv")
            ```
        """
        # Get download URL
        response = self._client._request(
            method="GET",
            path=f"/files/{self.file_id}/download",
            cast_type=dict,
        )

        # Handle different response formats
        file_data: bytes
        if "downloadUrl" in response:
            # Download from presigned URL
            download_url = response["downloadUrl"]
            try:
                with httpx.Client() as client:
                    download_response = client.get(download_url)
                    download_response.raise_for_status()
                    file_data = download_response.content
            except httpx.HTTPError as e:
                raise APIError(f"Failed to download file from URL: {e}") from e
        elif "content" in response:
            # Base64 encoded content
            import base64
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


    def delete(self) -> None:
        """Delete this file permanently.

        This operation cannot be undone. The file will be removed from both
        the database and cloud storage.

        Raises:
            APIError: If the deletion fails
            NotFoundError: If the file doesn't exist

        Example:
            ```python
            # Delete a file
            file.delete()
            # File is now permanently deleted
            ```
        """
        self._client._request(
            method="DELETE",
            path=f"/files/{self.file_id}",
            cast_type=type(None),
        )


    def is_ready(self) -> bool:
        """Check if the file is ready for use (processing complete).

        Files may need processing after upload. Use this method to check if
        a file is ready for operations like downloading or analysis.

        Returns:
            True if the file status is 'ready' or 'completed', False otherwise.

        Example:
            ```python
            if file.is_ready():
                content = file.download()
                print("File is ready and downloaded!")
            else:
                print("File is still processing...")
            ```
        """
        return self.status in ("ready", "completed")

    def is_processing(self) -> bool:
        """Check if the file is currently being processed.

        Returns:
            True if the file status is 'processing', False otherwise.

        Example:
            ```python
            if file.is_processing():
                print("Please wait, file is being processed...")
            ```
        """
        return self.status == "processing"

    def has_error(self) -> bool:
        """Check if the file has an error status.

        Returns:
            True if the file status is 'error', False otherwise.

        Example:
            ```python
            if file.has_error():
                print(f"File {file.name} failed to process")
                # Handle error case
            ```
        """
        return self.status == "error"

    def get_extension(self) -> str:
        """Get the file extension from the filename.

        Returns:
            The file extension (including the dot), or empty string if none.

        Example:
            ```python
            ext = file.get_extension()
            if ext == '.pdf':
                print("This is a PDF file")
            ```
        """
        return Path(self.name).suffix

    def is_image(self) -> bool:
        """Check if this file is an image based on MIME type.

        Detects common image formats like JPEG, PNG, GIF, SVG, etc.

        Returns:
            True if the MIME type indicates an image.

        Example:
            ```python
            if file.is_image():
                print(f"Image file: {file.name} ({file.mime_type})")
                # Handle image-specific logic
            ```
        """
        return self.mime_type.startswith("image/")

    def is_document(self) -> bool:
        """Check if this file is a document (PDF, Word, etc.).

        Detects common document formats including:
        - PDF files
        - Microsoft Word documents (.doc, .docx)
        - Microsoft Excel spreadsheets (.xls, .xlsx)
        - Microsoft PowerPoint presentations (.ppt, .pptx)

        Returns:
            True if the MIME type indicates a document.

        Example:
            ```python
            if file.is_document():
                print(f"Document: {file.name}")
                # Process document
            ```
        """
        document_types = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }
        return self.mime_type in document_types

    def is_text(self) -> bool:
        """Check if this file is a text file.

        Detects all text-based files including plain text, CSV, JSON, XML, etc.

        Returns:
            True if the MIME type indicates a text file.

        Example:
            ```python
            if file.is_text():
                content = file.download().decode('utf-8')
                print(f"Text content: {content[:100]}...")
            ```
        """
        return self.mime_type.startswith("text/")

    def is_csv(self) -> bool:
        """Check if this file is a CSV file.

        Specifically detects CSV (Comma-Separated Values) files, which are
        commonly used for tabular data.

        Returns:
            True if the MIME type indicates a CSV file.

        Example:
            ```python
            if file.is_csv():
                print(f"CSV file with {file.file_size} bytes of data")
                # Process as structured data
            ```
        """
        return self.mime_type == "text/csv"

    def _refresh(self) -> None:
        """Refresh this file from the API."""
        response = self._client._request(
            method="GET",
            path=f"/files/{self.file_id}",
            cast_type=dict,
        )
        self._data = response
