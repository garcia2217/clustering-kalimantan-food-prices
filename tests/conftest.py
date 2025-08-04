"""Shared fixtures for all test packages.

This file contains fixtures that are used across multiple test packages.
Package-specific fixtures should be placed in the respective package's conftest.py file.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    # This assumes we're running from the project root
    return Path.cwd()


@pytest.fixture
def global_temp_directory():
    """Provide a temporary directory for cross-package testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_global_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


# Add more global fixtures here as needed for integration tests