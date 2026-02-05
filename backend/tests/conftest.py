"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
