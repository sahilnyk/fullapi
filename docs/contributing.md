# Contributing

Thank you for your interest in contributing to fullapi.

## Development Setup

1. Fork and clone the repository:

```bash
git clone https://github.com/sahilnyk/fullapi.git
cd fullapi
```

2. Install in development mode:

```bash
pip install -e .
```

3. Verify the installation:

```bash
fullapi --version
```

## Guidelines

### Keep It Simple

- Only runtime dependency is PyYAML — don't add more without discussion
- `gen` (spec -> code) and `check` (spec -> expected OpenAPI) both go through `fullapi.types.resolve` as the single source of truth for field-type mapping; don't duplicate that mapping
- One feature per pull request

### Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and small

### Testing

Run the test suite before submitting:

```bash
pytest unit_tests/
```

To sanity-check generation and drift detection manually:

```bash
mkdir /tmp/fullapi_test && cd /tmp/fullapi_test
fullapi init
fullapi gen
pip install -r requirements.txt
fullapi check
```

### Commit Messages

Write clear, descriptive commit messages:

```
Add feature X

- Description of what changed
- Why it was needed
- Any breaking changes
```

### Pull Request Process

1. Create a branch for your feature
2. Make your changes
3. Test thoroughly
4. Update documentation if needed
5. Submit pull request with clear description

## Reporting Issues

When reporting bugs, include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages if any

## Feature Requests

We welcome suggestions. Please:

- Describe the use case
- Explain why it helps users
- Keep it aligned with the project's philosophy (spec stays the source of truth)

## Code of Conduct

Be respectful and constructive. We're building this together.
