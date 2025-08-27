"""Tests for validation utilities."""

import pytest
import yaml

from workflowforge import (
    validate_job_name,
    validate_secret_name,
    validate_step_name,
    validate_workflow_yaml,
)


def test_validate_job_name():
    """Test job name validation."""
    assert validate_job_name("test") == True
    assert validate_job_name("test_job") == True
    assert validate_job_name("test-job") == True
    assert validate_job_name("123test") == False
    assert validate_job_name("test job") == False


def test_validate_secret_name():
    """Test secret name validation."""
    assert validate_secret_name("MY_SECRET") == True
    assert validate_secret_name("API_TOKEN") == True
    assert validate_secret_name("my_secret") == False
    assert validate_secret_name("123SECRET") == False


def test_validate_workflow_yaml():
    """Test workflow YAML validation."""
    # Test basic validation functionality
    invalid_yaml = "invalid: yaml: content: ["

    errors = validate_workflow_yaml(invalid_yaml)
    assert len(errors) > 0
    assert any("YAML syntax error" in error for error in errors)
