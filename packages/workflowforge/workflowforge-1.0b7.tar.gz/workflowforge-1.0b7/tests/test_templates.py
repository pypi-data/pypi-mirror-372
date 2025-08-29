"""Tests for workflow templates."""

import yaml

from workflowforge.templates import (
    docker_build_template,
    node_ci_template,
    python_ci_template,
)


def test_python_ci_template():
    """Test Python CI template."""
    workflow = python_ci_template(python_versions=["3.11", "3.12"])
    yaml_output = workflow.to_yaml()

    parsed = yaml.safe_load(yaml_output)
    assert parsed["name"] == "Python CI"
    assert "test" in parsed["jobs"]
    assert "strategy" in parsed["jobs"]["test"]


def test_docker_build_template():
    """Test Docker build template."""
    workflow = docker_build_template(image_name="my-app")
    yaml_output = workflow.to_yaml()

    parsed = yaml.safe_load(yaml_output)
    assert parsed["name"] == "Docker Build"
    assert "build" in parsed["jobs"]


def test_node_ci_template():
    """Test Node.js CI template."""
    workflow = node_ci_template(node_versions=["18", "20"])
    yaml_output = workflow.to_yaml()

    parsed = yaml.safe_load(yaml_output)
    assert parsed["name"] == "Node.js CI"
    assert "test" in parsed["jobs"]
