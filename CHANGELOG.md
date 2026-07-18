# Changelog

All notable changes to fullapi will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `fullapi init [spec]` — write a starter `api.yaml` with a worked example; refuses to overwrite an existing file

---

## [2.0.0] - 2026-07-06

### Changed
- **Breaking**: Rewritten from a project scaffolder into a spec-driven tool. `api.yaml`
  is now the single source of truth for the life of the project, not just at
  creation time.
- Field-type mapping (`str`, `int`, `float`, `bool`) now lives in one place
  (`fullapi/types.py`) shared by generation and drift checking, so they can't disagree.

### Added
- `fullapi gen [spec] [-o dir]` — generate a FastAPI project from `api.yaml`
  (schemas, routers, and — with a database configured — SQLAlchemy models and CRUD)
- `fullapi check [spec] [--app app.main:app] [-v]` — read the live app's
  `app.openapi()`, diff it against the spec, and exit non-zero on breaking
  drift (removed routes/fields, type changes, newly required fields); added
  routes and optional fields are reported as safe

### Removed
- `fullapi new`, `fullapi add router/model`, `fullapi deploy`, `fullapi scale`
  and all associated interactive prompts, presets, and cloud/Terraform
  infrastructure support — replaced by the `gen`/`check` pair above
- MySQL support — `database` is now `none | sqlite | postgres`

---

## [1.3.0] - 2026-06-13

### Added
- ASCII art CLI banner with updated tagline
- Color-coded configuration summary table before project generation
- Real-time file creation progress bar
- `-v/--verbose` and `-q/--quiet` global flags

### Changed
- Password hashing switched from `bcrypt` to `sha256_crypt` (no 72-byte limit)
- Simplified CLI — removed `deploy`, `scale`, and cloud infrastructure commands
- Docker operations now work with any container registry (no cloud-specific auth)
- `ProjectConfig` — removed `terraform`, `cloud_provider`, `region`, `instance_size` fields
- `production` preset no longer includes Terraform configuration

### Removed
- Terraform infrastructure support (AWS ECS Fargate, GCP Cloud Run, Azure Container Apps)
- `fullapi deploy` command and related infrastructure automation
- `fullapi scale` command (up/down/set/status)
- AWS/GCP/Azure deployment templates

### Security
- Fixed bcrypt 72-byte password limit by switching to `sha256_crypt`

---

## [1.2.1] - 2026-06-01

### Fixed
- Package version alignment between `__init__.py` and `pyproject.toml`

---

## [1.2.0] - 2026-05-30

### Added
- Database connection pooling (`pool_size`, `max_overflow`, auto-reconnect, hourly recycle)
- CONTRIBUTING.md with contribution guidelines

### Changed
- CORS allowed headers changed from wildcard to explicit allowlist (`Content-Type`, `Authorization`, `X-Request-ID`)
- README reorganized with feature tables for better readability
- Enhanced security warnings in generated code comments

### Fixed
- `datetime.utcnow()` deprecation — replaced with `datetime.now(timezone.utc)` throughout generated code
- Weak default `SECRET_KEY` — now auto-generated in development, enforced in production

### Security
- **Breaking**: Production deployments now require `SECRET_KEY` set in `.env`
  - Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Replaced weak `.env.example` password placeholders with explicit `CHANGE_ME_*` values

---

## [1.1.0] - 2026-05-27

### Added
- `email-validator` as an explicit dependency (previously relied on pydantic extras)

### Changed
- `pyproject.toml` license field updated to SPDX format
- Requirements now include version floor pins for reproducibility

### Fixed
- `fullapi add router` now correctly detects database presence and generates appropriate code
- Basic projects (no database) can now add routers with in-memory storage
- `requirements.txt` deduplication — no more duplicate dependency lines

---

## [1.0.0] - 2024-04-30

### Added
- Project scaffolding in `basic` and `full` modes
- Database support: SQLite, PostgreSQL, MySQL with Alembic migrations
- JWT authentication (access + refresh tokens, role-based access)
- Docker and `docker-compose` file generation
- Redis caching support with async client and cache manager
- Middleware stack: CORS, rate limiting, security headers, gzip, request ID, request logging
- Structured logging with configurable formatters
- Terraform infrastructure for AWS ECS, GCP Cloud Run, Azure Container Apps
- `fullapi doctor` — project health check command
- `fullapi add router/model` — add components to existing projects
- Presets system (`production`, `minimal`, `docker-ready`, `microservice`)
- Custom template directory support
- Zero runtime dependencies for the CLI itself

[Unreleased]: https://github.com/sahilnyk/fullapi/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/sahilnyk/fullapi/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/sahilnyk/fullapi/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/sahilnyk/fullapi/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/sahilnyk/fullapi/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/sahilnyk/fullapi/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/sahilnyk/fullapi/releases/tag/v1.0.0
