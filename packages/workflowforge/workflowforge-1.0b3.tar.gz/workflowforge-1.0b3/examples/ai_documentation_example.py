#!/usr/bin/env python3
"""Example demonstrating AI documentation generation with WorkflowForge."""

from workflowforge import (
    Job,
    OllamaClient,
    Workflow,
    action,
    agent_docker,
    buildspec,
    environment,
    on_push,
    phase,
    pipeline,
    run,
    stage,
)


def github_workflow_with_readme():
    """Create GitHub Actions workflow with AI-generated README."""
    workflow = Workflow(name="Python CI with Tests", on=on_push(branches=["main"]))

    job = Job(runs_on="ubuntu-latest")
    job.add_step(action("actions/checkout@v4", name="Checkout code"))
    job.add_step(
        action(
            "actions/setup-python@v5",
            with_params={"python-version": "3.11"},
            name="Setup Python",
        )
    )
    job.add_step(run("pip install -r requirements.txt", name="Install dependencies"))
    job.add_step(run("pytest tests/", name="Run tests"))
    job.add_step(run("black --check .", name="Check formatting"))

    workflow.add_job("test", job)

    # Save with AI-generated README
    workflow.save(".github/workflows/ci.yml", generate_readme=True, use_ai=True)
    print("✓ GitHub workflow saved with AI README")


def jenkins_pipeline_with_readme():
    """Create Jenkins pipeline with AI-generated README."""
    jp = pipeline()
    jp.set_agent(agent_docker("python:3.11"))
    jp.set_description("Python CI Pipeline")

    # Build stage
    build_stage = stage("Build")
    build_stage.add_step("pip install -r requirements.txt")
    build_stage.add_step("python -m pytest tests/")
    jp.add_stage(build_stage)

    # Deploy stage
    deploy_stage = stage("Deploy")
    deploy_stage.add_step("echo 'Deploying application...'")
    jp.add_stage(deploy_stage)

    # Save with AI-generated README
    jp.save("Jenkinsfile", generate_readme=True, use_ai=True)
    print("✓ Jenkins pipeline saved with AI README")


def codebuild_spec_with_readme():
    """Create CodeBuild spec with AI-generated README."""
    spec = buildspec()

    # Environment
    env = environment()
    env.add_variable("PYTHON_VERSION", "3.11")
    spec.set_env(env)

    # Build phase
    build_phase = phase()
    build_phase.add_runtime("python", "3.11")
    build_phase.add_command("pip install -r requirements.txt")
    build_phase.add_command("pytest tests/")
    spec.set_build_phase(build_phase)

    # Save with AI-generated README
    spec.save("buildspec.yml", generate_readme=True, use_ai=True)
    print("✓ CodeBuild spec saved with AI README")


def check_ollama_status():
    """Check if Ollama is available for AI generation."""
    client = OllamaClient()

    if client.is_available():
        print("✅ Ollama is running and available for AI documentation")
        print(f"   Using model: {client.model}")
        print(f"   Server: {client.base_url}")
    else:
        print("❌ Ollama is not available")
        print("   Install Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("   Start Ollama: ollama serve")
        print("   Pull model: ollama pull llama3.2")
        print("   Fallback: Template-based README will be generated")


if __name__ == "__main__":
    print("=== WorkflowForge AI Documentation Example ===")

    # Check Ollama status
    check_ollama_status()
    print()

    # Generate workflows with AI documentation
    try:
        github_workflow_with_readme()
        jenkins_pipeline_with_readme()
        codebuild_spec_with_readme()

        print("\n🎉 All workflows generated with AI documentation!")
        print("\nGenerated files:")
        print("- .github/workflows/ci.yml + ci_README.md")
        print("- Jenkinsfile + Jenkinsfile_README.md")
        print("- buildspec.yml + buildspec_README.md")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(
            "Note: If Ollama is not available, template-based READMEs will be generated"
        )
