# Changelog

All notable changes to fullapi will be documented here.

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
