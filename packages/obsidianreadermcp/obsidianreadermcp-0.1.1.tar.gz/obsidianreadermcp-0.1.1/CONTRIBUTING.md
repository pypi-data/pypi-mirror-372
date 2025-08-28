# Contributing to ObsidianReaderMCP

We welcome contributions to ObsidianReaderMCP! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Git
- Obsidian with obsidian-local-rest-api plugin (for testing)

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ObsidianReaderMCP.git
   cd ObsidianReaderMCP
   ```

3. Install dependencies:
   ```bash
   uv sync --dev
   ```

4. Set up pre-commit hooks (optional but recommended):
   ```bash
   uv run pre-commit install
   ```

5. Copy the environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your Obsidian API settings
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Run all checks:
```bash
# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Check formatting
uv run black --check src/ tests/
uv run isort --check-only src/ tests/

# Lint
uv run flake8 src/ tests/

# Type check
uv run mypy src/obsidianreadermcp/
```

### Testing

We maintain comprehensive test coverage:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=obsidianreadermcp --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py

# Run with verbose output
uv run pytest -v
```

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards

3. Add or update tests for your changes

4. Run the test suite to ensure everything passes

5. Update documentation if necessary

6. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

## Types of Contributions

### Bug Reports

When filing a bug report, please include:

- A clear description of the issue
- Steps to reproduce the problem
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)
- Relevant error messages or logs

### Feature Requests

For feature requests, please provide:

- A clear description of the proposed feature
- Use cases and motivation
- Any relevant examples or mockups
- Consideration of potential implementation approaches

### Code Contributions

We welcome:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

### Documentation

Help improve our documentation by:

- Fixing typos or unclear explanations
- Adding examples
- Improving API documentation
- Translating documentation

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Add or update tests for your changes
3. Update documentation as needed
4. Ensure all tests pass
5. Update CHANGELOG.md with your changes
6. Submit a pull request with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots or examples if applicable

### Pull Request Guidelines

- Keep changes focused and atomic
- Write clear commit messages
- Include tests for new functionality
- Update documentation for API changes
- Follow the existing code style

## Code Review Process

1. All submissions require review before merging
2. Reviewers will check for:
   - Code quality and style
   - Test coverage
   - Documentation updates
   - Backward compatibility
3. Address feedback promptly
4. Once approved, maintainers will merge your PR

## Release Process

Releases are managed by maintainers:

1. Version numbers follow [Semantic Versioning](https://semver.org/)
2. Changes are documented in CHANGELOG.md
3. Releases are tagged and published to PyPI
4. GitHub releases include release notes

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Communication

- Use GitHub issues for bug reports and feature requests
- Use GitHub discussions for questions and general discussion
- Be patient and helpful when responding to questions

## Getting Help

If you need help:

1. Check the documentation and examples
2. Search existing issues and discussions
3. Create a new issue with your question
4. Join community discussions

## Recognition

Contributors are recognized in:

- GitHub contributors list
- Release notes for significant contributions
- Special mentions for major features or fixes

Thank you for contributing to ObsidianReaderMCP!
