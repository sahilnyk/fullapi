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
| Minimal Dependencies | Runtime dependency is PyYAML only — don't add more without discussion |
| Single Source of Truth | Field-type mapping lives in `fullapi/types.py`; both `gen` and `check` must go through it |
| Test Changes | Run `pytest unit_tests/` before submitting |
| Follow Style | Use type hints, keep functions focused |
| Clear Commits | Follow commit message format below |

### Testing Your Changes

```bash
pytest unit_tests/
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
| New Field Types | Open issue first to discuss (`fullapi/types.py`) |
| Documentation | Improvements appreciated |
| Database Backends | Open issue first to discuss |

## Questions?

Open an [issue](https://github.com/sahilnyk/fullapi/issues) or start a [discussion](https://github.com/sahilnyk/fullapi/discussions).
