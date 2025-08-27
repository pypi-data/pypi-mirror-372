# WorkflowForge 🔨

A robust and flexible library for creating GitHub Actions workflows, Jenkins pipelines, and AWS CodeBuild BuildSpecs programmatically in Python.

## ✨ Features

- **Intuitive API**: Fluent and easy-to-use syntax
- **Type Validation**: Built on Pydantic for automatic validation
- **IDE Support**: Full autocompletion with type hints
- **Multi-Platform**: GitHub Actions, Jenkins, AWS CodeBuild
- **AI Documentation**: Optional AI-powered README generation with Ollama
- **Pipeline Visualization**: Automatic diagram generation with Graphviz
- **Secrets Support**: Secure credential handling across all platforms
- **Templates**: Pre-built workflows for common use cases
- **Validation**: Schema validation and best practices checking

## 🚀 Installation

```bash
pip install workflowforge
```

## 🤖 AI Documentation (Optional)

WorkflowForge can automatically generate comprehensive README documentation for your workflows using **Ollama** (free local AI):

```bash
# Install Ollama (one-time setup)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull llama3.2
```

```python
# Generate workflow with AI documentation and diagram
workflow.save(".github/workflows/ci.yml", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: ci.yml + ci_README.md + CI_Pipeline_workflow.png

# Or generate README separately
readme = workflow.generate_readme(use_ai=True, ai_model="llama3.2")
print(readme)
```

**Features:**

- ✅ **Completely free** - no API keys or cloud services
- ✅ **Works offline** - local AI processing
- ✅ **Optional** - gracefully falls back to templates if Ollama not available
- ✅ **Comprehensive** - explains purpose, triggers, jobs, secrets, setup instructions
- ✅ **All platforms** - GitHub Actions, Jenkins, AWS CodeBuild

## 📊 Pipeline Visualization (Automatic)

WorkflowForge automatically generates visual diagrams of your pipelines using **Graphviz**:

```bash
# Install Graphviz (one-time setup)
brew install graphviz          # macOS
sudo apt-get install graphviz  # Ubuntu
choco install graphviz         # Windows
```

```python
# Generate workflow with automatic diagram
workflow.save(".github/workflows/ci.yml", generate_diagram=True)
# Creates: ci.yml + CI_Pipeline_workflow.png

# Generate diagram separately
diagram_path = workflow.generate_diagram("png")
print(f"📊 Diagram saved: {diagram_path}")

# Multiple formats supported
workflow.generate_diagram("svg")  # Vector graphics
workflow.generate_diagram("pdf")  # PDF document
```

**Features:**

- ✅ **Automatic generation** - every pipeline gets a visual diagram
- ✅ **Multiple formats** - PNG, SVG, PDF, DOT
- ✅ **Smart fallback** - DOT files if Graphviz not installed
- ✅ **Platform-specific styling** - GitHub (blue), Jenkins (orange), CodeBuild (purple)
- ✅ **Comprehensive view** - shows triggers, jobs, dependencies, step counts

## 📖 Basic Usage

```python
from workflowforge import (
    Workflow, Job,
    action, run,
    on_push, on_pull_request
)

# Create workflow
workflow = Workflow(
    name="My Workflow",
    on=on_push(branches=["main"])
)

# Create job
job = Job(runs_on="ubuntu-latest")
job.add_step(action("actions/checkout@v4", name="Checkout"))
job.add_step(run("echo 'Hello World!'", name="Say Hello"))

# Add job to workflow
workflow.add_job("hello", job)

# Generate YAML
print(workflow.to_yaml())

# Save with documentation and diagram
workflow.save(".github/workflows/hello.yml", generate_readme=True, generate_diagram=True)
# Creates: hello.yml + hello_README.md + My_Workflow.png
```

### Jenkins Pipeline Usage

```python
from workflowforge import (
    JenkinsPipeline, stage,
    agent_docker, pipeline
)

# Create Jenkins pipeline
jp = pipeline()
jp.set_agent(agent_docker("maven:3.9.3-eclipse-temurin-17"))

# Add stages
build_stage = stage("Build")
build_stage.add_step("mvn clean compile")
jp.add_stage(build_stage)

# Generate Jenkinsfile
print(jp.to_jenkinsfile())
jp.save("Jenkinsfile")
```

### AWS CodeBuild BuildSpec Usage

```python
from workflowforge import (
    buildspec, phase, environment, artifacts
)

# Create BuildSpec
spec = buildspec()

# Add environment
env = environment()
env.add_variable("JAVA_HOME", "/usr/lib/jvm/java-17-openjdk")
spec.set_env(env)

# Add build phase
build_phase = phase()
build_phase.add_command("mvn clean package")
spec.set_build_phase(build_phase)

# Generate buildspec.yml with AI documentation and diagram
spec.save("buildspec.yml", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: buildspec.yml + buildspec_README.md + codebuild_spec.png
```

### AI Documentation Examples

```python
# GitHub Actions with AI README
workflow = Workflow(name="CI Pipeline", on=on_push())
job = Job(runs_on="ubuntu-latest")
job.add_step(action("actions/checkout@v4"))
workflow.add_job("test", job)

# Save with AI documentation and diagram
workflow.save("ci.yml", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: ci.yml + ci_README.md + Test_Workflow.png

# Jenkins with AI README and diagram
pipeline = pipeline()
stage_build = stage("Build")
stage_build.add_step("mvn clean package")
pipeline.add_stage(stage_build)

# Save with AI documentation and diagram
pipeline.save("Jenkinsfile", generate_readme=True, use_ai=True, generate_diagram=True)
# Creates: Jenkinsfile + Jenkinsfile_README.md + jenkins_pipeline.png

# Check AI availability
from workflowforge import OllamaClient
client = OllamaClient()
if client.is_available():
    print("AI documentation available!")
else:
    print("Using template documentation (Ollama not running)")
```

## 🔧 Advanced Examples

### Build Matrix Workflow

```python
from workflowforge import matrix, strategy

job = Job(
    runs_on="ubuntu-latest",
    strategy=strategy(
        matrix=matrix(
            python_version=["3.8", "3.9", "3.10", "3.11"],
            os=["ubuntu-latest", "windows-latest"]
        )
    )
)
```

### Multiple Triggers

```python
workflow = Workflow(
    name="CI/CD",
    on=[
        on_push(branches=["main"]),
        on_pull_request(branches=["main"]),
        on_schedule("0 2 * * *")  # Daily at 2 AM
    ]
)
```

### Jobs with Dependencies

```python
test_job = Job(runs_on="ubuntu-latest")
deploy_job = Job(runs_on="ubuntu-latest").set_needs("test")

workflow.add_job("test", test_job)
workflow.add_job("deploy", deploy_job)
```

## 📚 Complete Documentation

### Platform Support

**GitHub Actions:**

- `on_push()`, `on_pull_request()`, `on_schedule()`, `on_workflow_dispatch()`
- `action()`, `run()` steps
- `secret()`, `variable()`, `github_context()` for credentials
- Build matrices, strategies, environments

**Jenkins:**

- `pipeline()`, `stage()`, `agent_docker()`, `agent_any()`
- `jenkins_credential()`, `jenkins_env()`, `jenkins_param()`
- Shared libraries, parameters, post actions

**AWS CodeBuild:**

- `buildspec()`, `phase()`, `environment()`, `artifacts()`
- `codebuild_secret()`, `codebuild_parameter()`, `codebuild_env()`
- Runtime versions, caching, reports

### AI Documentation

- **Ollama Integration**: Local AI models (llama3.2, codellama, qwen2.5-coder)
- **Automatic README**: Explains workflow purpose, triggers, jobs, setup
- **Fallback Support**: Template-based documentation if AI unavailable
- **All Platforms**: Works with GitHub Actions, Jenkins, CodeBuild

### Pipeline Visualization

- **Graphviz Integration**: Native diagram generation using DOT language
- **Multiple Formats**: PNG, SVG, PDF, DOT files
- **Platform Styling**: Color-coded diagrams (GitHub: blue, Jenkins: orange, CodeBuild: purple)
- **Smart Fallback**: DOT files if Graphviz not installed, images if available
- **Comprehensive View**: Shows triggers, jobs, dependencies, step counts, execution flow

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests
4. Submit a pull request

## 👨‍💻 Author & Maintainer

**Brainy Nimbus, LLC** - We love opensource! 💖

Website: [brainynimbus.io](https://brainynimbus.io)
Email: <info@brainynimbus.io>
GitHub: [@brainynimbus](https://github.com/brainynimbus)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

**GitHub Actions:**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

**Jenkins:**
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Jenkins Plugins](https://plugins.jenkins.io/)

**AWS CodeBuild:**
- [CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [BuildSpec Reference](https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html)
- [CodeBuild Samples](https://docs.aws.amazon.com/codebuild/latest/userguide/samples.html)
