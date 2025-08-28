"""Pytest configuration and fixtures."""

import os
import tempfile
import pytest
from pathlib import Path
from dotenv import load_dotenv
from datapress import DataPressClient

# Load test environment variables
load_dotenv("test.env")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration from environment variables."""
    api_key = os.getenv("TEST_DATAPRESS_API_KEY")
    instance = os.getenv("TEST_DATAPRESS_INSTANCE")
    dataset_id = os.getenv("TEST_DATAPRESS_DATASET_ID")

    if not all([api_key, instance, dataset_id]):
        pytest.skip(
            "Integration tests require TEST_DATAPRESS_API_KEY, "
            "TEST_DATAPRESS_INSTANCE, and TEST_DATAPRESS_DATASET_ID environment variables"
        )

    return {"api_key": api_key, "instance": instance, "dataset_id": dataset_id}


@pytest.fixture(scope="session")
def client(test_config):
    """DataPress client for testing."""
    return DataPressClient(api_key=test_config["api_key"], base_url=test_config["instance"])


@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing."""
    content = """name,age,city
Alice,30,New York
Bob,25,San Francisco
Charlie,35,London
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_csv_file_updated():
    """Create an updated temporary CSV file for testing."""
    content = """name,age,city,country
Alice,31,New York,USA
Bob,25,San Francisco,USA
Charlie,36,London,UK
David,28,Toronto,Canada
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def large_csv_file():
    """Create a large CSV file (>5MB) for chunking tests."""
    content = "name,age,city,description\n"
    # Generate ~500k rows to exceed 5MB
    rows = [f"Person{i},{20+i % 50},City{i % 100},{'X'*50}" for i in range(100000)]
    content += "\n".join(rows)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    yield temp_path

    if temp_path.exists():
        temp_path.unlink()
