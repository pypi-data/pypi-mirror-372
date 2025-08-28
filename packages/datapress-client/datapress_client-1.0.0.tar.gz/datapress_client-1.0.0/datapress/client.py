"""
DataPress client for Python.
"""

import os
import requests
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
import math


class DataPressError(Exception):
    """Base exception for DataPress client errors."""

    pass


class AuthenticationError(DataPressError):
    """Raised when authentication fails."""

    pass


class NotFoundError(DataPressError):
    """Raised when a resource is not found."""

    pass


class PermissionError(DataPressError):
    """Raised when insufficient permissions."""

    pass


class DataPressClient:
    """
    Client for interacting with the DataPress API.

    Args:
        api_key: API key for authentication. If not provided, reads from DATAPRESS_API_KEY environment variable.
        base_url: Base URL of the DataPress server. If not provided, reads from DATAPRESS_URL environment variable.
    """

    CHUNK_SIZE = 5 * 1024 * 1024  # 5MB chunks for uploads

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("DATAPRESS_API_KEY")
        self.base_url = (base_url or os.getenv("DATAPRESS_URL", "")).rstrip("/")

        if not self.api_key:
            raise ValueError(
                "API key is required. Set DATAPRESS_API_KEY environment variable or pass api_key parameter."
            )

        if not self.base_url:
            raise ValueError(
                "Base URL is required. Set DATAPRESS_URL environment variable or pass base_url parameter."
            )

        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": self.api_key, "User-Agent": "datapress-python/1.0.0"}
        )

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{path}"

        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise DataPressError(f"Request failed: {e}")

        if response.status_code >= 400:
            try:
                error_data = response.json()
                if response.status_code == 403:
                    raise PermissionError(error_data)
                elif response.status_code == 404:
                    raise NotFoundError(error_data)
                else:
                    raise DataPressError(error_data)
            except ValueError:
                # Not JSON response
                raise DataPressError(f"HTTP {response.status_code}: {response.text}")

        return response

    def whoami(self) -> Dict[str, Any]:
        """
        Get information about the current user.

        Returns:
            Dict containing user information including id, title, email, admin status, and team memberships.

        Raises:
            AuthenticationError: If the API key is invalid.
        """
        response = self._request("GET", "/api/v3/whoami")
        data = response.json()

        if data is None:
            raise AuthenticationError("Not logged in - invalid API key")

        return data

    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Retrieve a dataset by ID.

        Args:
            dataset_id: The 5-character dataset ID (e.g., "ab12x")

        Returns:
            Dict containing the full dataset JSON structure.

        Raises:
            NotFoundError: If the dataset doesn't exist.
            PermissionError: If you don't have permission to access the dataset.
        """
        response = self._request("GET", f"/api/v3/dataset/{dataset_id}")
        return response.json()

    def upload_file(
        self,
        dataset_id: str,
        file_path: Union[str, Path],
        resource_id: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        order: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file to a dataset using chunked uploads.

        Args:
            dataset_id: The 5-character dataset ID
            file_path: Path to the file to upload
            resource_id: Optional resource ID to replace an existing file
            title: Optional title for the file
            description: Optional description for the file
            order: Optional position in the dataset file list

        Returns:
            Dict containing the upload response with dataset info and new resource details.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            PermissionError: If you don't have editor permissions on the dataset.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        num_chunks = math.ceil(file_size / self.CHUNK_SIZE)

        # Create upload session
        create_payload = {"filename": file_path.name, "parts": num_chunks}

        if resource_id:
            create_payload["resource_id"] = resource_id
        if title:
            create_payload["title"] = title
        if description:
            create_payload["description"] = description
        if order is not None:
            create_payload["order"] = order

        create_response = self._request(
            "POST", f"/api/v3/dataset/{dataset_id}/upload", json=create_payload
        )

        upload_urls = create_response.json()
        url_chunk = upload_urls["urlChunk"]
        url_complete = upload_urls["urlComplete"]

        # Upload chunks
        with open(file_path, "rb") as f:
            for chunk_num in range(num_chunks):
                chunk_data = f.read(self.CHUNK_SIZE)

                # Use the full URL from the response
                chunk_response = self.session.post(
                    url_chunk,
                    headers={"Authorization": self.api_key},
                    files={"file": chunk_data},
                    data={"part": chunk_num},
                )

                if chunk_response.status_code >= 400:
                    try:
                        error_data = chunk_response.json()
                        raise DataPressError(f"Chunk {chunk_num} upload failed: {error_data}")
                    except ValueError:
                        raise DataPressError(
                            f"Chunk {chunk_num} upload failed: HTTP {chunk_response.status_code}"
                        )

        # Complete upload
        complete_response = self.session.post(url_complete, headers={"Authorization": self.api_key})

        if complete_response.status_code >= 400:
            try:
                error_data = complete_response.json()
                raise DataPressError(f"Upload completion failed: {error_data}")
            except ValueError:
                raise DataPressError(
                    f"Upload completion failed: HTTP {complete_response.status_code}"
                )

        return complete_response.json()

    def download_file(self, dataset_id: str, resource_id: str) -> bytes:
        """
        Download a file from a dataset resource with authentication.

        Args:
            dataset_id: The 5-character dataset ID
            resource_id: The resource ID within the dataset

        Returns:
            Bytes content of the downloaded file.

        Raises:
            DataPressError: If the download fails.
            NotFoundError: If the dataset or resource doesn't exist.
            PermissionError: If you don't have permission to access the file.
        """
        # Get the dataset to find the resource URL
        dataset = self.get_dataset(dataset_id)

        if resource_id not in dataset["resources"]:
            raise NotFoundError(f"Resource {resource_id} not found in dataset {dataset_id}")

        resource_url = dataset["resources"][resource_id]["url"]
        response = self.session.get(resource_url)

        if response.status_code >= 400:
            if response.status_code == 403:
                raise PermissionError("Access denied to file")
            elif response.status_code == 404:
                raise NotFoundError("File not found")
            else:
                raise DataPressError(f"Download failed: HTTP {response.status_code}")

        return response.content

    def patch_dataset(self, dataset_id: str, patch: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply a JSON Patch to a dataset.

        Args:
            dataset_id: The 5-character dataset ID (e.g., "ab12x")
            patch: List of JSON Patch operations (e.g., [{"op": "replace", "path": "/title", "value": "New Title"}])

        Returns:
            Dict containing the updated dataset JSON structure.

        Raises:
            ValueError: If the patch is invalid.
            NotFoundError: If the dataset doesn't exist.
            PermissionError: If you don't have editor permissions on the dataset.
            DataPressError: If the patch operation fails.
        """
        # Client-side validation
        self._validate_patch(patch)

        response = self._request("PATCH", f"/api/v3/dataset/{dataset_id}", json=patch)
        return response.json()

    def _validate_patch(self, patch: List[Dict[str, Any]]) -> None:
        """
        Validate a JSON Patch operation client-side.

        Args:
            patch: List of JSON Patch operations to validate

        Raises:
            ValueError: If the patch is invalid
        """
        if not isinstance(patch, list):
            raise ValueError("Patch must be a list of operations")

        if not patch:
            raise ValueError("Patch cannot be empty")

        valid_ops = {"add", "remove", "replace", "move", "copy", "test"}

        for i, operation in enumerate(patch):
            if not isinstance(operation, dict):
                raise ValueError(f"Operation {i} must be a dictionary")

            if "op" not in operation:
                raise ValueError(f"Operation {i} missing required 'op' field")

            if operation["op"] not in valid_ops:
                raise ValueError(
                    f"Operation {i} has invalid op '{operation['op']}'. Valid ops: {', '.join(valid_ops)}"
                )

            if "path" not in operation:
                raise ValueError(f"Operation {i} missing required 'path' field")

            if not isinstance(operation["path"], str) or not operation["path"].startswith("/"):
                raise ValueError(f"Operation {i} 'path' must be a string starting with '/'")

            # Value is required for add, replace, and test operations
            if operation["op"] in {"add", "replace", "test"} and "value" not in operation:
                raise ValueError(
                    f"Operation {i} with op '{operation['op']}' requires 'value' field"
                )

            # From is required for move and copy operations
            if operation["op"] in {"move", "copy"} and "from" not in operation:
                raise ValueError(f"Operation {i} with op '{operation['op']}' requires 'from' field")

            # Basic path validation for common mistakes
            if (
                operation["path"] == "/title"
                and operation["op"] in {"add", "replace"}
                and "value" in operation
            ):
                if not isinstance(operation["value"], str) or not operation["value"].strip():
                    raise ValueError(f"Operation {i}: title cannot be empty")
