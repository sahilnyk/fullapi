# Changelog

All notable changes to fullapi will be documented here.

## [1.1.1] - 2026-05-28

### Security Fixes (CRITICAL)
- **SECRET_KEY auto-generation**: Now generates random key in development, enforces in production
- **Weak default passwords**: Replaced with explicit CHANGE_ME placeholders in .env.example
- **Python 3.12+ compatibility**: Fixed datetime.utcnow() deprecation
- **Database connection pooling**: Added pool_size=20, max_overflow=10, auto-reconnect, hourly recycle
- **CORS security**: Changed wildcard headers to specific allowlist (Content-Type, Authorization, X-Request-ID)
- **SQL injection warnings**: Added security documentation in CRUD templates

### Breaking Changes
- Production apps now MUST set SECRET_KEY in .env file (intentional security measure)
- Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Documentation
- Improved README with tables and better organization
- Added CONTRIBUTING.md with contribution guidelines
- Enhanced security warnings in generated code

## [1.1.0] - 2026-05-27

### Fixed
- Component addition (`fullapi add router`) now detects database presence and generates appropriate code
- Basic projects without database can now add routers with in-memory storage
- Requirements.txt deduplication - no more duplicate dependencies
- Added email-validator as explicit dependency instead of relying on pydantic extras

### Changed
- Updated license format in pyproject.toml to modern SPDX standard
- Requirements now include version pins for better reproducibility

## [1.0.0] - 2024-04-30

### Added
- Initial release
- Project scaffolding (basic and full modes)
- Database support (SQLite, PostgreSQL, MySQL)
- JWT authentication
- Docker and docker-compose generation
- Redis caching support
- Middleware stack (CORS, rate limiting, security headers, gzip)
- Structured logging
- Terraform infrastructure for AWS, GCP, Azure
- Infrastructure scaling commands
- Presets system (production, minimal, docker-ready, microservice)
- Component addition (routers, models)
- Health check command (`fullapi doctor`)
- Custom template support
- Zero runtime dependencies
