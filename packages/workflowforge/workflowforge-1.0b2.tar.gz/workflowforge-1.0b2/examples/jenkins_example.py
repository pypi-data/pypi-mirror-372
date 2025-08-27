#!/usr/bin/env python3
"""
Jenkins pipeline example using WorkflowForge.
Creates a complete CI/CD pipeline for Jenkins.
"""

from workflowforge import JenkinsPipeline, agent_any, agent_docker, pipeline, stage

# Create Jenkins pipeline
jenkins_pipeline = pipeline()

# Set agent and environment
jenkins_pipeline.set_agent(agent_docker("maven:3.9.3-eclipse-temurin-17"))
jenkins_pipeline.set_env("MAVEN_OPTS", "-Xmx1024m")
jenkins_pipeline.add_tool("maven", "3.9.3")

# Build stage
build_stage = stage("Build")
build_stage.add_step("echo 'Starting build...'")
build_stage.add_step("mvn clean compile")

# Test stage
test_stage = stage("Test")
test_stage.add_step("echo 'Running tests...'")
test_stage.add_step("mvn test")
test_stage.add_step("junit 'target/surefire-reports/*.xml'")

# Deploy stage with condition
deploy_stage = stage("Deploy")
deploy_stage.set_when("branch 'main'")
deploy_stage.add_step("echo 'Deploying to production...'")
deploy_stage.add_step("mvn deploy")

# Add stages to pipeline
jenkins_pipeline.add_stage(build_stage)
jenkins_pipeline.add_stage(test_stage)
jenkins_pipeline.add_stage(deploy_stage)

# Add post actions
jenkins_pipeline.post = {
    "always": ["echo 'Pipeline completed'"],
    "success": ["echo 'Build successful!'"],
    "failure": ["echo 'Build failed!'"],
}

# Generate and save Jenkinsfile
if __name__ == "__main__":
    print("Generating Jenkins pipeline...")
    jenkinsfile_content = jenkins_pipeline.to_jenkinsfile()
    print(jenkinsfile_content)

    # Save to Jenkinsfile
    jenkins_pipeline.save("Jenkinsfile")
    print("Jenkinsfile saved successfully!")
