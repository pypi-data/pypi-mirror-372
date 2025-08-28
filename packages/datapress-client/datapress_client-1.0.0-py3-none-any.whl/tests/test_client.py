"""Unit tests for DataPress client."""

import pytest
from unittest.mock import Mock, patch
from datapress import DataPressClient
from datapress.client import DataPressError, AuthenticationError, NotFoundError, PermissionError


class TestClientInitialization:
    """Test client initialization and configuration."""

    def test_init_with_params(self):
        """Test client initialization with explicit parameters."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")
        assert client.api_key == "test-key"
        assert client.base_url == "https://test.example.com"

    def test_init_with_env_vars(self, monkeypatch):
        """Test client initialization with environment variables."""
        monkeypatch.setenv("DATAPRESS_API_KEY", "env-key")
        monkeypatch.setenv("DATAPRESS_URL", "https://env.example.com")

        client = DataPressClient()
        assert client.api_key == "env-key"
        assert client.base_url == "https://env.example.com"

    def test_init_missing_api_key(self, monkeypatch):
        """Test error when API key is missing."""
        monkeypatch.delenv("DATAPRESS_API_KEY", raising=False)

        with pytest.raises(ValueError, match="API key is required"):
            DataPressClient(base_url="https://test.example.com")

    def test_init_missing_base_url(self, monkeypatch):
        """Test error when base URL is missing."""
        monkeypatch.delenv("DATAPRESS_URL", raising=False)

        with pytest.raises(ValueError, match="Base URL is required"):
            DataPressClient(api_key="test-key")

    def test_base_url_trailing_slash_removed(self):
        """Test that trailing slashes are removed from base URL."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com/")
        assert client.base_url == "https://test.example.com"


class TestErrorHandling:
    """Test error handling for different HTTP responses."""

    def test_permission_error_with_json(self):
        """Test PermissionError with JSON error details."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "error": "Insufficient permissions",
            "details": "Editor access required",
        }

        with patch.object(client.session, "request", return_value=mock_response):
            with pytest.raises(PermissionError) as exc_info:
                client._request("GET", "/test")

            assert exc_info.value.args[0] == {
                "error": "Insufficient permissions",
                "details": "Editor access required",
            }

    def test_not_found_error_with_json(self):
        """Test NotFoundError with JSON error details."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Dataset not found", "id": "ab12x"}

        with patch.object(client.session, "request", return_value=mock_response):
            with pytest.raises(NotFoundError) as exc_info:
                client._request("GET", "/test")

            assert exc_info.value.args[0] == {"error": "Dataset not found", "id": "ab12x"}

    def test_generic_error_with_json(self):
        """Test generic DataPressError with JSON error details."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request", "field": "filename"}

        with patch.object(client.session, "request", return_value=mock_response):
            with pytest.raises(DataPressError) as exc_info:
                client._request("GET", "/test")

            assert exc_info.value.args[0] == {"error": "Invalid request", "field": "filename"}

    def test_error_without_json(self):
        """Test error handling when response is not JSON."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = "Internal Server Error"

        with patch.object(client.session, "request", return_value=mock_response):
            with pytest.raises(DataPressError, match="HTTP 500: Internal Server Error"):
                client._request("GET", "/test")


class TestPatchDataset:
    """Test dataset patch functionality."""

    def test_patch_dataset_success(self):
        """Test successful dataset patch."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "dataset": {
                "id": "ab12x",
                "title": "Updated Title",
                "description": "Updated description",
            }
        }

        patch_data = [
            {"op": "replace", "path": "/title", "value": "Updated Title"},
            {"op": "replace", "path": "/description", "value": "Updated description"},
        ]

        with patch.object(client.session, "request", return_value=mock_response) as mock_request:
            result = client.patch_dataset("ab12x", patch_data)

            mock_request.assert_called_once_with(
                "PATCH", "https://test.example.com/api/v3/dataset/ab12x", json=patch_data
            )
            assert result["dataset"]["title"] == "Updated Title"
            assert result["dataset"]["description"] == "Updated description"

    def test_patch_validation_not_list(self):
        """Test patch validation fails when patch is not a list."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Patch must be a list of operations"):
            client.patch_dataset("ab12x", {"op": "replace", "path": "/title", "value": "New Title"})

    def test_patch_validation_empty_list(self):
        """Test patch validation fails when patch is empty."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Patch cannot be empty"):
            client.patch_dataset("ab12x", [])

    def test_patch_validation_operation_not_dict(self):
        """Test patch validation fails when operation is not a dict."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0 must be a dictionary"):
            client.patch_dataset("ab12x", ["invalid"])

    def test_patch_validation_missing_op(self):
        """Test patch validation fails when operation is missing 'op' field."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0 missing required 'op' field"):
            client.patch_dataset("ab12x", [{"path": "/title", "value": "New Title"}])

    def test_patch_validation_invalid_op(self):
        """Test patch validation fails when operation has invalid 'op'."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0 has invalid op 'invalid'"):
            client.patch_dataset(
                "ab12x", [{"op": "invalid", "path": "/title", "value": "New Title"}]
            )

    def test_patch_validation_missing_path(self):
        """Test patch validation fails when operation is missing 'path' field."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0 missing required 'path' field"):
            client.patch_dataset("ab12x", [{"op": "replace", "value": "New Title"}])

    def test_patch_validation_invalid_path(self):
        """Test patch validation fails when path doesn't start with '/'."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(
            ValueError, match="Operation 0 'path' must be a string starting with '/'"
        ):
            client.patch_dataset(
                "ab12x", [{"op": "replace", "path": "title", "value": "New Title"}]
            )

    def test_patch_validation_missing_value_for_replace(self):
        """Test patch validation fails when replace operation is missing 'value'."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(
            ValueError, match="Operation 0 with op 'replace' requires 'value' field"
        ):
            client.patch_dataset("ab12x", [{"op": "replace", "path": "/title"}])

    def test_patch_validation_missing_from_for_move(self):
        """Test patch validation fails when move operation is missing 'from'."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0 with op 'move' requires 'from' field"):
            client.patch_dataset("ab12x", [{"op": "move", "path": "/title"}])

    def test_patch_validation_empty_title(self):
        """Test patch validation fails when trying to set title to empty string."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0: title cannot be empty"):
            client.patch_dataset("ab12x", [{"op": "replace", "path": "/title", "value": ""}])

    def test_patch_validation_whitespace_title(self):
        """Test patch validation fails when trying to set title to whitespace."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        with pytest.raises(ValueError, match="Operation 0: title cannot be empty"):
            client.patch_dataset("ab12x", [{"op": "replace", "path": "/title", "value": "   "}])

    def test_patch_validation_multiple_operations(self):
        """Test patch validation with multiple valid operations."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"dataset": {"id": "ab12x"}}

        patch_data = [
            {"op": "replace", "path": "/title", "value": "New Title"},
            {
                "op": "add",
                "path": "/links/new_link",
                "value": {"url": "https://example.com", "title": "Example"},
            },
            {"op": "remove", "path": "/description"},
            {"op": "test", "path": "/id", "value": "ab12x"},
        ]

        with patch.object(client.session, "request", return_value=mock_response):
            # Should not raise any validation errors
            client.patch_dataset("ab12x", patch_data)

    def test_patch_dataset_server_error_handling(self):
        """Test patch method handles server errors properly."""
        client = DataPressClient(api_key="test-key", base_url="https://test.example.com")

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "statusCode": 400,
            "message": "There are validation errors.\n* title: This field is required",
        }

        patch_data = [{"op": "replace", "path": "/title", "value": "Valid Title"}]

        with patch.object(client.session, "request", return_value=mock_response):
            with pytest.raises(DataPressError) as exc_info:
                client.patch_dataset("ab12x", patch_data)

            assert exc_info.value.args[0]["statusCode"] == 400
