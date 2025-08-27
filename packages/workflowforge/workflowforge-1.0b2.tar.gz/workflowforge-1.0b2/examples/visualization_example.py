#!/usr/bin/env python3
"""Example demonstrating pipeline visualization with WorkflowForge."""

from workflowforge import (  # GitHub Actions; Jenkins; CodeBuild; Visualization
    Job,
    Workflow,
    action,
    agent_docker,
    buildspec,
    environment,
    matrix,
    on_pull_request,
    on_push,
    phase,
    pipeline,
    run,
    stage,
    strategy,
    visualizer,
)


def create_github_workflow():
    """Create a GitHub Actions workflow with dependencies."""
    workflow = Workflow(
        name="CI/CD Pipeline with Visualization",
        on=[on_push(branches=["main"]), on_pull_request()],
    )

    # Test job with matrix
    test_job = Job(
        runs_on="ubuntu-latest",
        strategy=strategy(matrix=matrix(python_version=["3.11", "3.12", "3.13"])),
    )
    test_job.add_step(action("actions/checkout@v4", name="Checkout"))
    test_job.add_step(action("actions/setup-python@v5", name="Setup Python"))
    test_job.add_step(run("pytest tests/", name="Run tests"))

    # Build job (depends on test)
    build_job = Job(runs_on="ubuntu-latest")
    build_job.set_needs("test")
    build_job.add_step(action("actions/checkout@v4", name="Checkout"))
    build_job.add_step(run("python -m build", name="Build package"))

    # Deploy job (depends on build)
    deploy_job = Job(runs_on="ubuntu-latest")
    deploy_job.set_needs("build")
    deploy_job.add_step(run("echo 'Deploying...'", name="Deploy"))

    workflow.add_job("test", test_job)
    workflow.add_job("build", build_job)
    workflow.add_job("deploy", deploy_job)

    return workflow


def create_jenkins_pipeline():
    """Create a Jenkins pipeline with multiple stages."""
    jp = pipeline()
    jp.set_agent(agent_docker("python:3.11"))
    jp.set_description("Multi-stage Jenkins Pipeline")

    # Stages
    checkout_stage = stage("Checkout")
    checkout_stage.add_step("git checkout main")
    jp.add_stage(checkout_stage)

    test_stage = stage("Test")
    test_stage.add_step("pip install -r requirements.txt")
    test_stage.add_step("pytest tests/")
    jp.add_stage(test_stage)

    build_stage = stage("Build")
    build_stage.add_step("python -m build")
    jp.add_stage(build_stage)

    deploy_stage = stage("Deploy")
    deploy_stage.add_step("echo 'Deploying application'")
    jp.add_stage(deploy_stage)

    return jp


def create_codebuild_spec():
    """Create a CodeBuild spec with multiple phases."""
    spec = buildspec()

    # Environment
    env = environment()
    env.add_variable("PYTHON_VERSION", "3.11")
    env.add_variable("BUILD_ENV", "production")
    spec.set_env(env)

    # Install phase
    install_phase = phase()
    install_phase.add_runtime("python", "3.11")
    install_phase.add_command("pip install --upgrade pip")
    spec.set_install_phase(install_phase)

    # Pre-build phase
    pre_build_phase = phase()
    pre_build_phase.add_command("pip install -r requirements.txt")
    pre_build_phase.add_command("pip install pytest")
    spec.set_pre_build_phase(pre_build_phase)

    # Build phase
    build_phase = phase()
    build_phase.add_command("pytest tests/")
    build_phase.add_command("python -m build")
    spec.set_build_phase(build_phase)

    # Post-build phase
    post_build_phase = phase()
    post_build_phase.add_command("echo 'Build completed successfully'")
    spec.set_post_build_phase(post_build_phase)

    return spec


def demonstrate_visualization():
    """Demonstrate pipeline visualization for all platforms."""
    print("=== WorkflowForge Pipeline Visualization Demo ===")

    # Create visualizer
    viz = visualizer(output_format="png")

    # GitHub Actions
    print("\n1. GitHub Actions Workflow")
    workflow = create_github_workflow()
    github_diagram = workflow.generate_diagram("png")
    print(f"   📊 Diagram saved: {github_diagram}")

    # Jenkins Pipeline
    print("\n2. Jenkins Pipeline")
    jenkins_pipeline = create_jenkins_pipeline()
    jenkins_diagram = jenkins_pipeline.generate_diagram("png")
    print(f"   📊 Diagram saved: {jenkins_diagram}")

    # CodeBuild Spec
    print("\n3. AWS CodeBuild Spec")
    codebuild_spec = create_codebuild_spec()
    codebuild_diagram = codebuild_spec.generate_diagram("png")
    print(f"   📊 Diagram saved: {codebuild_diagram}")

    # Save with automatic diagram generation
    print("\n4. Automatic Diagram Generation")
    workflow.save("demo_workflow.yml", generate_diagram=True)
    jenkins_pipeline.save("demo_Jenkinsfile", generate_diagram=True)
    codebuild_spec.save("demo_buildspec.yml", generate_diagram=True)

    print("\n🎉 All pipeline diagrams generated!")
    print("\nGenerated files:")
    print("- GitHub: demo_workflow.yml + diagram")
    print("- Jenkins: demo_Jenkinsfile + diagram")
    print("- CodeBuild: demo_buildspec.yml + diagram")

    print("\n💡 Note: Install Graphviz for PNG/SVG output:")
    print("   macOS: brew install graphviz")
    print("   Ubuntu: sudo apt-get install graphviz")
    print("   Windows: choco install graphviz")
    print("   Without Graphviz: .dot files are generated instead")


if __name__ == "__main__":
    try:
        demonstrate_visualization()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: Visualization requires Graphviz for image output")
