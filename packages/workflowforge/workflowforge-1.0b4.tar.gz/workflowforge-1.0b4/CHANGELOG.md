# Changelog

All notable changes to WorkflowForge will be documented in this file.

## [1.0b3] - 2024-12-26

### Added
- **Modular Import Structure**: Platform-specific imports for better organization
  - `from workflowforge import github_actions`
  - `from workflowforge import jenkins_platform`
  - `from workflowforge import aws_codebuild`
- **Snake Case Naming**: Following Python PEP 8 conventions
  - `github_actions.workflow()` instead of `Workflow()`
  - `github_actions.job()` instead of `Job()`
  - All functions now use snake_case
- **Examples Directory**: Complete working examples for all platforms
  - GitHub Actions: basic CI and Python matrix testing
  - Jenkins: Maven build pipeline
  - AWS CodeBuild: Node.js application build
- **Backwards Compatibility**: Legacy imports still supported

### Changed
- README updated with new import structure and examples
- Documentation reflects snake_case naming convention
- Version bumped to 1.0b3

### Fixed
- Circular import issues resolved
- All examples tested and working
- Automatic diagram generation for all platforms

## [1.0b2] - 2024-12-26

### Fixed
- PyPI publishing pipeline with API tokens
- Safety command updated from deprecated 'check' to 'scan'
- TestPyPI vs PyPI URL configuration

## [1.0b1] - 2024-12-26

### Added
- Initial release with GitHub Actions, Jenkins, and AWS CodeBuild support
- AI documentation generation with Ollama
- Pipeline visualization with Graphviz
- Comprehensive test suite
- PyPI publishing workflow
