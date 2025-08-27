#!/usr/bin/env python3
"""
Basic WorkflowForge usage example.
Creates a simple CI/CD workflow for a Python application.
"""

from workflowforge import (
    Job,
    Workflow,
    action,
    matrix,
    on_pull_request,
    on_push,
    run,
    strategy,
)

# Create main workflow
workflow = Workflow(
    name="CI/CD Pipeline",
    on=[on_push(branches=["main", "develop"]), on_pull_request(branches=["main"])],
)

# Testing job with matrix
test_job = (
    Job(
        runs_on="ubuntu-latest",
        strategy=strategy(
            matrix=matrix(
                python_version=["3.8", "3.9", "3.10", "3.11"],
                os=["ubuntu-latest", "windows-latest", "macos-latest"],
            )
        ),
    )
    .add_step(action("actions/checkout@v4", name="Checkout code"))
    .add_step(
        action(
            "actions/setup-python@v4",
            name="Setup Python",
            python_version="${{ matrix.python-version }}",
        )
    )
    .add_step(run("pip install -r requirements.txt", name="Install dependencies"))
    .add_step(run("pytest", name="Run tests"))
)

# Build job (depends on test)
build_job = (
    Job(runs_on="ubuntu-latest")
    .set_needs("test")
    .add_step(action("actions/checkout@v4", name="Checkout code"))
    .add_step(
        action("actions/setup-python@v4", name="Setup Python", python_version="3.11")
    )
    .add_step(run("pip install build", name="Install build tools"))
    .add_step(run("python -m build", name="Build package"))
    .add_step(
        action(
            "actions/upload-artifact@v3", name="Upload build artifacts", path="dist/"
        )
    )
)

# Add jobs to workflow
workflow.add_job("test", test_job)
workflow.add_job("build", build_job)

# Generate and save workflow
if __name__ == "__main__":
    print("Generating workflow...")
    print(workflow.to_yaml())

    # Save to file
    workflow.save(".github/workflows/ci.yml")
    print("Workflow saved to .github/workflows/ci.yml")
