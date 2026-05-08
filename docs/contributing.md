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

- Use Python standard library only
- No external dependencies
- Clean, readable code
- One feature per pull request

### Code Style

- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions
- Keep functions focused and small

### Testing

Test your changes before submitting:

```bash
# Test basic mode
fullapi new test_basic --basic

# Test full mode
fullapi new test_full --full --db sqlite --auth

# Verify generated code works
cd test_full
pip install -r requirements.txt
python -c "from main import app; print('OK')"
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
- Keep it aligned with the project's philosophy (stdlib only)

## Code of Conduct

Be respectful and constructive. We're building this together.
