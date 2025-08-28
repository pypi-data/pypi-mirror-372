"""Integration tests for DataPress client.

These tests run against a real DataPress instance and require environment variables:
- TEST_DATAPRESS_API_KEY
- TEST_DATAPRESS_INSTANCE
- TEST_DATAPRESS_DATASET_ID

The tests run sequentially as they depend on each other's state.
"""

import pytest
import requests
from pathlib import Path
from datapress.client import AuthenticationError


class TestAuthentication:
    """Test authentication and user info."""

    def test_whoami_success(self, client):
        """Test successful whoami call."""
        user_info = client.whoami()

        assert "id" in user_info
        assert "title" in user_info
        assert "email" in user_info
        assert "admin" in user_info
        assert "memberships" in user_info
        assert isinstance(user_info["id"], int)
        assert isinstance(user_info["admin"], bool)
        assert isinstance(user_info["memberships"], list)

    def test_whoami_invalid_key(self, test_config):
        """Test whoami with invalid API key."""
        from datapress import DataPressClient

        bad_client = DataPressClient(api_key="invalid-key", base_url=test_config["instance"])

        with pytest.raises(AuthenticationError, match="Not logged in"):
            bad_client.whoami()


class TestDatasetAccess:
    """Test dataset retrieval."""

    def test_get_dataset_success(self, client, test_config):
        """Test successful dataset retrieval."""
        dataset = client.get_dataset(test_config["dataset_id"])

        assert "id" in dataset
        assert "title" in dataset
        assert "resources" in dataset
        assert dataset["title"] == "Test Dataset"
        assert dataset["id"] == test_config["dataset_id"]
        assert isinstance(dataset["resources"], dict)


@pytest.mark.order(1)
class TestFileUploadSequence:
    """Sequential integration tests for file upload workflow.

    These tests must run in order and share state.
    """

    # Class-level variable to store resource_id between tests
    uploaded_resource_id = None

    def test_01_upload_initial_file(self, client, test_config, temp_csv_file):
        """Test initial file upload."""
        result = client.upload_file(
            dataset_id=test_config["dataset_id"],
            file_path=temp_csv_file,
            title="Test CSV Upload",
            description="Initial test file upload",
        )

        assert "dataset" in result
        assert "resource_id" in result
        assert "new_key" in result

        # Store resource_id for subsequent tests
        TestFileUploadSequence.uploaded_resource_id = result["resource_id"]

        # Verify the file appears in dataset
        dataset = result["dataset"]
        resources = dataset["resources"]
        resource_id = result["resource_id"]

        assert resource_id in resources
        resource = resources[resource_id]
        assert resource["title"] == "Test CSV Upload"
        assert resource["description"] == "Initial test file upload"
        assert resource["format"] == "csv"

    def test_02_verify_file_in_dataset(self, client, test_config):
        """Test that uploaded file appears in dataset."""
        dataset = client.get_dataset(test_config["dataset_id"])
        resource_id = TestFileUploadSequence.uploaded_resource_id

        assert resource_id in dataset["resources"]
        resource = dataset["resources"][resource_id]
        assert resource["title"] == "Test CSV Upload"
        assert resource["format"] == "csv"
        assert "url" in resource
        assert "hash" in resource
        assert "size" in resource

    def test_02b_verify_initial_csv_content(self, client, test_config):
        """Test that uploaded CSV content matches expected data."""
        resource_id = TestFileUploadSequence.uploaded_resource_id

        # Download the CSV file using client method
        downloaded_bytes = client.download_file(test_config["dataset_id"], resource_id)
        downloaded_content = downloaded_bytes.decode("utf-8")

        # Expected content from temp_csv_file fixture
        expected_lines = [
            "name,age,city",
            "Alice,30,New York",
            "Bob,25,San Francisco",
            "Charlie,35,London",
        ]

        downloaded_lines = [line.strip() for line in downloaded_content.strip().split("\n")]
        assert downloaded_lines == expected_lines

    def test_03_replace_existing_file(self, client, test_config, temp_csv_file_updated):
        """Test replacing existing file."""
        resource_id = TestFileUploadSequence.uploaded_resource_id

        result = client.upload_file(
            dataset_id=test_config["dataset_id"],
            file_path=temp_csv_file_updated,
            resource_id=resource_id,  # Replace existing file
            title="Updated Test CSV",
            description="Updated test file",
        )

        assert result["resource_id"] == resource_id

        # Verify the file was updated
        dataset = result["dataset"]
        resource = dataset["resources"][resource_id]
        assert resource["title"] == "Updated Test CSV"
        assert resource["description"] == "Updated test file"

    def test_04_verify_file_replacement(self, client, test_config):
        """Test that file replacement worked correctly."""
        dataset = client.get_dataset(test_config["dataset_id"])
        resource_id = TestFileUploadSequence.uploaded_resource_id

        resource = dataset["resources"][resource_id]
        assert resource["title"] == "Updated Test CSV"
        assert resource["description"] == "Updated test file"

    def test_04b_verify_updated_csv_content(self, client, test_config):
        """Test that updated CSV content matches expected data."""
        resource_id = TestFileUploadSequence.uploaded_resource_id

        # Download the updated CSV file using client method
        downloaded_bytes = client.download_file(test_config["dataset_id"], resource_id)
        downloaded_content = downloaded_bytes.decode("utf-8")

        # Expected content from temp_csv_file_updated fixture
        expected_lines = [
            "name,age,city,country",
            "Alice,31,New York,USA",
            "Bob,25,San Francisco,USA",
            "Charlie,36,London,UK",
            "David,28,Toronto,Canada",
        ]

        downloaded_lines = [line.strip() for line in downloaded_content.strip().split("\n")]
        assert downloaded_lines == expected_lines

    def test_05_upload_large_file(self, client, test_config, large_csv_file):
        """Test uploading a larger file to trigger chunking."""
        result = client.upload_file(
            dataset_id=test_config["dataset_id"],
            file_path=large_csv_file,
            title="Large Test File",
            description="Test file for chunked upload (>5MB)",
        )

        assert "resource_id" in result
        assert "dataset" in result

        # Verify file appears in dataset
        resource_id = result["resource_id"]
        resource = result["dataset"]["resources"][resource_id]
        assert resource["title"] == "Large Test File"
        assert resource["size"] > 5000000  # Should be >5MB

        # Store the large file resource_id for cleanup
        TestFileUploadSequence.large_file_resource_id = result["resource_id"]


@pytest.mark.order(2)
class TestCleanup:
    """Clean up test files from the dataset using patch operations."""

    def test_cleanup_uploaded_files(self, client, test_config):
        """Remove all uploaded test files using patch operations."""
        # Get current dataset state
        dataset = client.get_dataset(test_config["dataset_id"])

        # Collect resource IDs to remove
        resource_ids_to_remove = []

        if (
            hasattr(TestFileUploadSequence, "uploaded_resource_id")
            and TestFileUploadSequence.uploaded_resource_id
        ):
            if TestFileUploadSequence.uploaded_resource_id in dataset["resources"]:
                resource_ids_to_remove.append(TestFileUploadSequence.uploaded_resource_id)

        if (
            hasattr(TestFileUploadSequence, "large_file_resource_id")
            and TestFileUploadSequence.large_file_resource_id
        ):
            if TestFileUploadSequence.large_file_resource_id in dataset["resources"]:
                resource_ids_to_remove.append(TestFileUploadSequence.large_file_resource_id)

        # Remove each resource using patch operations
        for resource_id in resource_ids_to_remove:
            patch_ops = [{"op": "remove", "path": f"/resources/{resource_id}"}]

            result = client.patch_dataset(test_config["dataset_id"], patch_ops)

            # Verify the resource was removed
            assert resource_id not in result["dataset"]["resources"]

        # Verify final dataset state - no test files remain
        final_dataset = client.get_dataset(test_config["dataset_id"])
        for resource_id in resource_ids_to_remove:
            assert resource_id not in final_dataset["resources"]
