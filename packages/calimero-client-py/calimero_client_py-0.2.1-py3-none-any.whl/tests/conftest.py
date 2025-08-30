"""
Pytest configuration and fixtures for Calimero client testing.

This file demonstrates the new, cleaner Merobox testing API.
"""

import pytest
from pathlib import Path
from merobox.testing import run_workflow


# ============================================================================
# Main session-scoped fixtures for reuse across all tests
# ============================================================================


@run_workflow("tests/workflows/workflow-example.yml", scope="session")
def shared_workflow():
    """Main shared workflow for all tests - session scoped for maximum reuse"""
    pass


# ============================================================================
# Test fixtures that are actually used
# ============================================================================


@pytest.fixture
def workflow_environment(shared_workflow):
    """Provides the workflow environment with captured outputs."""
    # The shared_workflow IS the workflow environment
    return shared_workflow


@pytest.fixture
def workflow_result():
    """Provides the workflow execution result."""
    return True
