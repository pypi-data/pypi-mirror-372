"""
WorkflowForge - A robust and flexible library for creating GitHub Actions workflows.

This library allows you to create GitHub Actions workflows programmatically,
with type validation, autocompletion, and an intuitive API.
"""

# Platform-specific modules
from . import codebuild as aws_codebuild
from . import github_actions_module as github_actions
from . import jenkins as jenkins_platform
from .ai_documentation import (
    OllamaClient,
    ai_documentation_client,
    generate_workflow_readme,
)
from .codebuild import (
    BuildArtifacts,
    BuildCache,
    BuildEnvironment,
    BuildPhase,
    BuildSpec,
    artifacts,
    buildspec,
    cache,
    environment,
    phase,
)
from .environment import Environment, environment
from .jenkins import (
    JenkinsAgent,
    JenkinsPipeline,
    JenkinsStage,
    agent_any,
    agent_docker,
    agent_label,
    pipeline,
    stage,
)
from .jenkins_plugins import (
    ArtifactArchiver,
    DockerPlugin,
    EmailNotification,
    GitCheckout,
    JUnitPublisher,
    SlackNotification,
    archive_artifacts,
    docker_run,
    email_notify,
    git_checkout,
    publish_junit,
    slack_notify,
)
from .job import Job
from .schema_validation import validate_github_actions_schema, validate_workflow_yaml
from .secrets import (  # GitHub Actions; Jenkins; AWS CodeBuild
    CodeBuildEnvVar,
    CodeBuildParameter,
    CodeBuildSecret,
    GitHubContext,
    JenkinsCredential,
    JenkinsEnvVar,
    JenkinsParam,
    Secret,
    Variable,
    codebuild_env,
    codebuild_parameter,
    codebuild_secret,
    github_context,
    jenkins_credential,
    jenkins_env,
    jenkins_param,
    secret,
    variable,
)
from .step import ActionStep, RunStep, Step, action, run
from .strategy import Matrix, Strategy, matrix, strategy
from .templates import (
    docker_build_template,
    node_ci_template,
    python_ci_template,
    release_template,
)
from .triggers import (
    PullRequestTrigger,
    PushTrigger,
    ReleaseTrigger,
    ScheduleTrigger,
    WorkflowDispatchTrigger,
    on_pull_request,
    on_push,
    on_release,
    on_schedule,
    on_workflow_dispatch,
)
from .validation import (
    ValidationError,
    validate_job_name,
    validate_secret_name,
    validate_step_name,
)
from .visualization import PipelineVisualizer, visualizer
from .workflow import Workflow

__version__ = "1.0b2"
__all__ = [
    "Workflow",
    "Job",
    "Step",
    "ActionStep",
    "RunStep",
    "action",
    "run",
    "PushTrigger",
    "PullRequestTrigger",
    "ScheduleTrigger",
    "WorkflowDispatchTrigger",
    "ReleaseTrigger",
    "on_push",
    "on_pull_request",
    "on_schedule",
    "on_workflow_dispatch",
    "on_release",
    "Strategy",
    "Matrix",
    "matrix",
    "strategy",
    "Environment",
    "environment",
    "JenkinsPipeline",
    "JenkinsStage",
    "JenkinsAgent",
    "agent_any",
    "agent_docker",
    "agent_label",
    "stage",
    "pipeline",
    "GitCheckout",
    "DockerPlugin",
    "SlackNotification",
    "EmailNotification",
    "ArtifactArchiver",
    "JUnitPublisher",
    "git_checkout",
    "docker_run",
    "slack_notify",
    "email_notify",
    "archive_artifacts",
    "publish_junit",
    "BuildSpec",
    "BuildPhase",
    "BuildEnvironment",
    "BuildArtifacts",
    "BuildCache",
    "buildspec",
    "phase",
    "environment",
    "artifacts",
    "cache",
    # Secrets and variables
    "Secret",
    "Variable",
    "GitHubContext",
    "secret",
    "variable",
    "github_context",
    "JenkinsCredential",
    "JenkinsEnvVar",
    "JenkinsParam",
    "jenkins_credential",
    "jenkins_env",
    "jenkins_param",
    "CodeBuildSecret",
    "CodeBuildParameter",
    "CodeBuildEnvVar",
    "codebuild_secret",
    "codebuild_parameter",
    "codebuild_env",
    # AI Documentation
    "OllamaClient",
    "generate_workflow_readme",
    "ai_documentation_client",
    # Visualization
    "PipelineVisualizer",
    "visualizer",
    # Validation
    "validate_job_name",
    "validate_step_name",
    "validate_secret_name",
    "ValidationError",
    # Templates
    "python_ci_template",
    "docker_build_template",
    "node_ci_template",
    "release_template",
    # Schema validation
    "validate_github_actions_schema",
    "validate_workflow_yaml",
    # Platform modules
    "github_actions",
    "jenkins_platform",
    "aws_codebuild",
]
