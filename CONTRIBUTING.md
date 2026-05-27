# Contributing to fullapi

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-009688.svg)](https://github.com/sahilnyk/fullapi/pulls)
[![Issues](https://img.shields.io/github/issues/sahilnyk/fullapi?color=009688)](https://github.com/sahilnyk/fullapi/issues)

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/sahilnyk/fullapi.git
cd fullapi
pip install -e .
```

## Development Guidelines

### Rules

| Rule | Description |
|------|-------------|
| Zero Dependencies | Keep CLI tool dependency-free, only stdlib imports |
| Test Changes | Test both basic and full project generation |
| Follow Style | Use type hints, keep functions focused |
| Clear Commits | Follow commit message format below |

### Testing Your Changes

```bash
# Test basic project
fullapi new test_basic --basic
cd test_basic && python -c "from main import app; print('✓')"

# Test full project
fullapi new test_full --full --db postgresql --auth --docker
cd test_full && python -c "from main import app; print('✓')"
```

### Pull Request Process

| Step | Action |
|------|--------|
| 1 | Fork the repository |
| 2 | Create feature branch: `git checkout -b feature-name` |
| 3 | Make your changes |
| 4 | Test thoroughly |
| 5 | Commit with clear messages |
| 6 | Push and create PR |

### Commit Message Format

| Type | Usage |
|------|-------|
| `fix:` | Bug fixes |
| `feat:` | New features |
| `docs:` | Documentation |
| `refactor:` | Code refactoring |
| `test:` | Adding tests |

Keep messages under 50 characters.

## What to Contribute

| Area | Status |
|------|--------|
| Bug Fixes | Always welcome |
| New Features | Open issue first to discuss |
| Documentation | Improvements appreciated |
| Templates | New project templates |
| Cloud Providers | Extend Terraform support |

## Questions?

Open an [issue](https://github.com/sahilnyk/fullapi/issues) or start a [discussion](https://github.com/sahilnyk/fullapi/discussions).
