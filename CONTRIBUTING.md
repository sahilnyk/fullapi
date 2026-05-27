# Contributing to fullapi

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/sahilnyk/fullapi.git
cd fullapi
pip install -e .
```

## Development Guidelines

**1. Zero Dependencies Rule**
- Keep the CLI tool dependency-free
- Only stdlib imports allowed
- Generated projects can have dependencies

**2. Testing Your Changes**
```bash
# Test basic project
fullapi new test_basic --basic
cd test_basic && python -c "from main import app; print('✓')"

# Test full project
fullapi new test_full --full --db postgresql --auth --docker
cd test_full && python -c "from main import app; print('✓')"
```

**3. Code Style**
- Follow existing code patterns
- Use type hints
- Keep functions focused and simple

**4. Pull Request Process**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and create a PR

**5. Commit Messages**
- `fix: brief description` for bug fixes
- `feat: brief description` for new features
- `docs: brief description` for documentation
- Keep under 50 characters

## What to Contribute

**Bug Fixes** - Always welcome  
**New Features** - Open an issue first to discuss  
**Documentation** - Improvements appreciated  
**Templates** - New project templates  
**Cloud Providers** - Extend Terraform support

## Questions?

Open an issue or start a discussion on GitHub.
