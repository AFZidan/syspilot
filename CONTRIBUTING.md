# Contributing to SysPilot

We welcome contributions to SysPilot! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat all contributors and users with respect.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use a clear and descriptive title** for the issue
3. **Provide detailed information** about the bug:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - System information (OS, Python version, etc.)
   - Error messages or logs

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Use a clear and descriptive title**
3. **Provide detailed information** about the feature:
   - Use case and motivation
   - Detailed description
   - Alternative solutions considered

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Ensure all tests pass**
6. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Ubuntu 18.04+ or Debian 10+
- Git

### Setting up the Development Environment

```bash
# Clone the repository
git clone https://github.com/AFZidan/syspilot.git
cd syspilot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=syspilot --cov-report=html

# Run specific test file
python -m pytest tests/test_cleanup_service.py

# Run tests with verbose output
python -m pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
black syspilot/
isort syspilot/

# Lint code
flake8 syspilot/
pylint syspilot/

# Type checking
mypy syspilot/
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Use type hints where appropriate
- Keep functions focused and reasonably short

### Code Organization

- Keep related functionality together
- Use appropriate design patterns
- Separate concerns (UI, business logic, data access)
- Follow the existing project structure

### Documentation

- Write clear, concise docstrings
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update CHANGELOG.md for all changes

### Testing

- Write tests for all new functionality
- Maintain test coverage above 90%
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with appropriate tests
3. **Ensure all tests pass** and code quality checks succeed
4. **Update documentation** as needed
5. **Submit a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

### Pull Request Guidelines

- Keep changes focused and atomic
- Write clear commit messages
- Squash commits if necessary
- Be responsive to feedback
- Update your branch with latest `main` before merging

## Code Review Process

All code changes require review before merging:

1. **Automated checks** must pass (tests, linting, etc.)
2. **At least one reviewer** must approve the changes
3. **Address all feedback** before merging
4. **Maintainers** will merge approved changes

## Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Use mocks for external dependencies
- Test edge cases and error conditions
- Keep tests fast and isolated

### Integration Tests

- Test component interactions
- Test with real file system operations
- Test system integration points
- Use temporary directories for file tests

### GUI Tests

- Test user interactions
- Test UI state changes
- Mock system services
- Test error handling in UI

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

1. **Update version** in `setup.py` and `__init__.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Tag the release** with version number
4. **Create release notes** on GitHub
5. **Publish to PyPI** (maintainers only)

## Security

If you discover a security vulnerability, please:

1. **Do not** open a public issue
2. **Email** the maintainers directly
3. **Wait for confirmation** before disclosing
4. **Follow responsible disclosure** practices

## Getting Help

- **Documentation**: Check the README and Wiki
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our Discord server (link in README)

## Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** section
- **Special thanks** in documentation

## License

By contributing to SysPilot, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to SysPilot!
