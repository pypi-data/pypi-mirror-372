#!/usr/bin/env python3
"""
Advanced Jenkins pipeline example with plugins and VCS.
Demonstrates WorkflowForge capabilities for complex Jenkins pipelines.
"""

from workflowforge import (
    agent_docker,
    archive_artifacts,
    docker_run,
    email_notify,
    git_checkout,
    pipeline,
    publish_junit,
    slack_notify,
    stage,
)

# Create advanced Jenkins pipeline
jp = pipeline()

# Add shared library
jp.add_library("my-shared-library@main")

# Add parameters
jp.add_parameter(
    "string", "BRANCH_NAME", defaultValue="main", description="Branch to build"
)
jp.add_parameter(
    "choice",
    "ENVIRONMENT",
    choices=["dev", "staging", "prod"],
    description="Target environment",
)

# Set Docker agent
jp.set_agent(agent_docker("maven:3.9.3-eclipse-temurin-17"))

# Environment variables
jp.set_env("MAVEN_OPTS", "-Xmx2048m")
jp.set_env("DOCKER_REGISTRY", "my-registry.com")

# Tools
jp.add_tool("maven", "3.9.3")
jp.add_tool("jdk", "17")

# Checkout stage with VCS
checkout_stage = stage("Checkout")
git_config = git_checkout(
    url="https://github.com/myorg/myrepo.git",
    branch="${params.BRANCH_NAME}",
    credentials_id="github-credentials",
)
checkout_stage.add_step(git_config.to_step())
jp.add_stage(checkout_stage)

# Build stage
build_stage = stage("Build")
build_stage.add_step("echo 'Building application...'")
build_stage.add_step("mvn clean compile")
build_stage.add_step(archive_artifacts("target/*.jar", allow_empty=False))
jp.add_stage(build_stage)

# Test stage with JUnit
test_stage = stage("Test")
test_stage.add_step("echo 'Running tests...'")
test_stage.add_step("mvn test")
test_stage.add_step(publish_junit("target/surefire-reports/*.xml"))
jp.add_stage(test_stage)

# Docker build stage
docker_stage = stage("Docker Build")
docker_stage.set_when("expression { params.ENVIRONMENT != 'dev' }")
docker_stage.add_step("echo 'Building Docker image...'")
docker_stage.add_step(
    docker_run(
        "docker:latest",
        "docker build -t myapp:${BUILD_NUMBER} .",
        args="-v /var/run/docker.sock:/var/run/docker.sock",
    )
)
jp.add_stage(docker_stage)

# Deploy stage
deploy_stage = stage("Deploy")
deploy_stage.set_when("expression { params.ENVIRONMENT == 'prod' }")
deploy_stage.add_step("echo 'Deploying to production...'")
deploy_stage.add_step("kubectl apply -f k8s/")
jp.add_stage(deploy_stage)

# Post actions with notifications
jp.post = {
    "success": [
        slack_notify("#builds", "✅ Build ${BUILD_NUMBER} succeeded!", color="good"),
        email_notify(
            "team@company.com", "Build Success", "Build completed successfully"
        ),
    ],
    "failure": [
        slack_notify("#builds", "❌ Build ${BUILD_NUMBER} failed!", color="danger"),
        email_notify("team@company.com", "Build Failed", "Build failed - check logs"),
    ],
    "always": ["echo 'Cleaning up workspace...'", "cleanWs()"],
}

# Generate pipeline
if __name__ == "__main__":
    print("Generating advanced Jenkins pipeline...")
    jenkinsfile_content = jp.to_jenkinsfile()
    print(jenkinsfile_content)

    jp.save("Jenkinsfile.advanced")
    print("Advanced Jenkinsfile saved!")
