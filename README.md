<div align="center">

# 🕊️ fullapi

CLI tool for production-ready FastAPI projects with auth, Docker, databases, and Redis caching

[![PyPI](https://img.shields.io/pypi/v/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Python](https://img.shields.io/pypi/pyversions/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Downloads](https://img.shields.io/pypi/dm/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Issues](https://img.shields.io/github/issues-raw/sahilnyk/fullapi?color=009688)](https://github.com/sahilnyk/fullapi/issues)
[![Changelog](https://img.shields.io/badge/changelog-1.1.1-009688)](CHANGELOG.md)
[![Contributing](https://img.shields.io/badge/PRs-welcome-009688)](CONTRIBUTING.md)

</div>

## Quick Start

```bash
pip install fullapi
fullapi new my_api --preset production
cd my_api && pip install -r requirements.txt
uvicorn main:app --reload
```

## Features

| Feature | Description |
|---------|-------------|
| Zero Dependencies | Pure Python stdlib |
| Production Ready | Auth, Docker, DB migrations, Redis |
| Modern Architecture | SQLAlchemy 2.0, Pydantic v2, async lifespan |
| Extensible | Add routers/models anytime |
| Health Checks | `fullapi doctor` validates structure |
| Database Support | SQLite, PostgreSQL, MySQL with Alembic migrations |
| JWT Authentication | Access/refresh tokens, role-based access |
| Redis Caching | Async client with cache manager |
| Middleware Stack | CORS, rate limiting, security headers, gzip, request ID, logging |

## Commands

| Command | Description |
|---------|-------------|
| `fullapi new <name>` | Create new project |
| `fullapi add router <name>` | Add router to project |
| `fullapi doctor` | Check project health |
| `fullapi docker build` | Build Docker image |
| `fullapi docker push` | Push image to registry |
| `fullapi preset list` | List available presets |

## Presets

| Preset | Stack |
|--------|-------|
| `production` | PostgreSQL + auth + Docker + Redis + middleware + logging |
| `microservice` | SQLite + Docker + middleware + logging |
| `minimal` | Basic API only |

## CLI Options

```bash
fullapi new my_api [OPTIONS]

--basic              Minimal structure
--full               Production structure
--db TYPE            none | sqlite | postgresql | mysql
--auth               JWT authentication
--docker             Docker + docker-compose
--redis              Redis caching
--middleware         Middleware stack
--logging            Structured logging
--preset NAME        Use preset config
```

## Project Structure

```
my_api/
├── main.py              # FastAPI app with lifespan
├── core/                # Config, responses, middleware, logging
├── routers/             # API endpoints (health, users, auth, redis)
├── schemas/             # Pydantic models
├── models/              # SQLAlchemy models
├── crud/                # Database operations
├── dependencies/        # DB, auth, cache injection
├── db/                  # Session, base, mixins
├── tests/               # Pytest with fixtures
├── alembic/             # DB migrations
├── requirements.txt
└── .env.example
```

Built and maintained by [@sahilnyk](https://github.com/sahilnyk) with zero dependencies