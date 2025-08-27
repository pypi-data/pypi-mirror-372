#!/usr/bin/env python3
"""
AWS CodeBuild BuildSpec example using WorkflowForge.
Creates a complete BuildSpec for CodeBuild projects.
"""

from workflowforge import artifacts, buildspec, cache, environment, phase

# Create BuildSpec
spec = buildspec()

# Environment configuration
env = environment()
env.add_variable("JAVA_HOME", "/usr/lib/jvm/java-17-openjdk-amd64")
env.add_variable("MAVEN_OPTS", "-Xmx1024m")
env.add_parameter_store("DB_PASSWORD", "/myapp/db/password")
env.exported_variables = ["BUILD_VERSION"]
spec.set_env(env)

# Install phase
install_phase = phase()
install_phase.add_runtime("java", "corretto17")
install_phase.add_runtime("nodejs", "18")
install_phase.add_command("echo Installing dependencies...")
install_phase.add_command("apt-get update -y")
install_phase.add_command("apt-get install -y maven")
install_phase.finally_commands = ["echo Install phase completed"]
spec.set_install_phase(install_phase)

# Pre-build phase
pre_build_phase = phase()
pre_build_phase.add_command("echo Logging in to Amazon ECR...")
pre_build_phase.add_command(
    "aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
)
pre_build_phase.add_command("echo Running tests...")
pre_build_phase.add_command("mvn test")
spec.set_pre_build_phase(pre_build_phase)

# Build phase
build_phase = phase()
build_phase.set_on_failure("ABORT")
build_phase.add_command("echo Build started on `date`")
build_phase.add_command("mvn clean package")
build_phase.add_command("export BUILD_VERSION=$(date +%Y%m%d-%H%M%S)")
build_phase.add_command("echo Building Docker image...")
build_phase.add_command("docker build -t $IMAGE_REPO_NAME:$BUILD_VERSION .")
build_phase.add_command(
    "docker tag $IMAGE_REPO_NAME:$BUILD_VERSION $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$BUILD_VERSION"
)
spec.set_build_phase(build_phase)

# Post-build phase
post_build_phase = phase()
post_build_phase.add_command("echo Build completed on `date`")
post_build_phase.add_command("echo Pushing Docker image...")
post_build_phase.add_command(
    "docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$BUILD_VERSION"
)
post_build_phase.add_command("echo Writing image definitions file...")
post_build_phase.add_command(
    'printf \'[{"name":"myapp","imageUri":"%s"}]\' $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$BUILD_VERSION > imagedefinitions.json'
)
spec.set_post_build_phase(post_build_phase)

# Artifacts
build_artifacts = artifacts(["target/*.jar", "imagedefinitions.json"])
build_artifacts.name = "myapp-artifacts"
build_artifacts.discard_paths = False
spec.set_artifacts(build_artifacts)

# Cache
build_cache = cache(["/root/.m2/**/*", "node_modules/**/*"])
build_cache.key = "cache-key-$CODEBUILD_BUILD_NUMBER"
build_cache.fallback_keys = ["cache-key-", "cache-"]
spec.set_cache(build_cache)

# Reports (optional)
spec.reports = {
    "test-reports": {
        "files": ["target/surefire-reports/*.xml"],
        "file-format": "JUNITXML",
        "base-directory": "target/surefire-reports",
    }
}

# Generate and save BuildSpec
if __name__ == "__main__":
    print("Generating CodeBuild BuildSpec...")
    buildspec_content = spec.to_yaml()
    print(buildspec_content)

    # Save to buildspec.yml
    spec.save("buildspec.yml")
    print("BuildSpec saved to buildspec.yml")
