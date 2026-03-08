"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_fixture():
    """Example fixture - customize as needed."""
    return {"example": "data"}
