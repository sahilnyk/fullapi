<div align="center">

# 🕊️ fullapi

CLI tool for production-ready FastAPI projects with auth, Docker, databases, and cloud deployment

[![PyPI](https://img.shields.io/pypi/v/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Python](https://img.shields.io/pypi/pyversions/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Downloads](https://img.shields.io/pypi/dm/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Issues](https://img.shields.io/github/issues/sahilnyk/fullapi?color=009688)](https://github.com/sahilnyk/fullapi/issues)
[![Changelog](https://img.shields.io/badge/changelog-1.1.0-009688)](CHANGELOG.md)
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
| Cloud Deploy | Terraform for AWS, GCP, Azure |
| Extensible | Add routers/models anytime |
| Health Checks | `fullapi doctor` validates structure |

## Commands

| Command | Description |
|---------|-------------|
| `fullapi new <name>` | Create new project |
| `fullapi add router <name>` | Add router to project |
| `fullapi doctor` | Check project health |
| `fullapi docker build` | Build Docker image |
| `fullapi terraform apply` | Deploy to cloud |
| `fullapi scale up` | Scale infrastructure |

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
--db TYPE           none | sqlite | postgresql | mysql
--auth              JWT authentication
--docker            Docker + docker-compose
--redis             Redis caching
--terraform         Cloud infrastructure (AWS, GCP, Azure)
--preset NAME       Use preset config
```

## Cloud Deployment

| Provider | Services |
|----------|----------|
| AWS | ECS Fargate, RDS, ElastiCache, ECR |
| GCP | Cloud Run, Cloud SQL, Memorystore |
| Azure | Container Apps, Azure Database, Azure Cache |

| Size | Resources | Cost/month |
|------|-----------|------------|
| Small | 1 vCPU, 2GB | $10-15 |
| Medium | 2 vCPU, 4GB | $25-35 |
| Large | 4 vCPU, 8GB | $60-80 |

[@sahilnyk](https://github.com/sahilnyk)
