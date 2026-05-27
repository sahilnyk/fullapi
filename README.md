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

Visit `http://localhost:8000/docs` for auto-generated API documentation.

### With Infrastructure

```bash
fullapi new my_api --full --db postgresql --docker --terraform
cd my_api
pip install -r requirements.txt
fullapi docker build
fullapi docker push
fullapi terraform apply
```

## Commands

```bash
# Interactive mode
fullapi new my_api

# Use a preset
fullapi new my_api --preset production

# Add components
fullapi add router Product
fullapi add model Order

# Check project health
fullapi doctor

# List presets
fullapi preset list

# Terraform operations
fullapi terraform init
fullapi terraform plan
fullapi terraform apply
fullapi terraform destroy

# Docker operations
fullapi docker build
fullapi docker push

# Scaling
fullapi scale up
fullapi scale down
fullapi scale set medium
fullapi scale status
```

## Presets

| Preset | Description |
|--------|-------------|
| `production` | PostgreSQL + auth + Docker + Redis + middleware + logging |
| `microservice` | SQLite + Docker + middleware + logging |
| `docker-ready` | PostgreSQL + Docker + logging |
| `minimal` | Basic API structure only |

Create custom presets in `~/.fullapi/presets.json`

## CLI Flags

```bash
fullapi new my_api [OPTIONS]

OPTIONS:
  --basic              Minimal structure
  --full               Production-ready structure
  --db TYPE            none | sqlite | postgresql | mysql
  --auth               JWT authentication
  --docker             Docker + docker-compose
  --redis              Redis caching
  --middleware         CORS, rate limiting, security headers
  --logging            Structured logging
  --terraform          Terraform infrastructure (AWS, GCP, Azure)
  --template PATH      Custom template directory
  --preset NAME        Use a preset configuration
```

## Features

| Feature | Description |
|---------|-------------|
| Zero Dependencies | Pure Python stdlib |
| Instant Setup | Complete project in seconds |
| Production Ready | Auth, Docker, DB migrations, caching |
| Cloud Infrastructure | Terraform for AWS, GCP, Azure |
| Container Ops | Build and push Docker images |
| Auto Scaling | Scale infrastructure with simple commands |
| Extensible | Add routers/models to existing projects |
| Health Checks | `fullapi doctor` validates structure |
| Presets | Save common configurations |
| Custom Templates | Bring your own boilerplate |  

## What Gets Created

### Basic Mode
```
my_project/
├── main.py
├── routers/health.py
├── schemas/base.py
├── core/config.py
├── requirements.txt
└── .fullapi.json
```

### Full Mode (--db postgresql --auth --docker --terraform)
```
my_project/
├── main.py
├── routers/
│   ├── health.py
│   └── users.py
├── models/user.py
├── schemas/user.py
├── crud/user.py
├── core/
│   ├── config.py
│   └── security.py
├── db/session.py
├── alembic/
│   ├── env.py
│   └── versions/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── README.md
├── tests/test_main.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .fullapi.json
```

## Examples

```bash
# Start with a preset
fullapi new api --preset production

# Customized setup
fullapi new api --full --db mysql --auth --redis --middleware

# Basic API
fullapi new api --basic

# With cloud infrastructure
fullapi new api --full --db postgresql --docker --terraform

# Custom template
fullapi new api --template ./my_template
```

## Infrastructure Management

Deploy your FastAPI app to AWS, GCP, or Azure with built-in Terraform support:

```bash
# Create project with infrastructure
fullapi new myapi --full --db postgresql --docker --redis --terraform

# Build and push Docker image
cd myapi
fullapi docker build
fullapi docker push

# Deploy to cloud
fullapi terraform init
fullapi terraform plan
fullapi terraform apply

# Scale resources
fullapi scale up              # Increase instance size
fullapi scale down            # Decrease instance size
fullapi scale set large       # Set specific size
fullapi scale status          # View current configuration

# Destroy infrastructure
fullapi terraform destroy
```

### Supported Cloud Providers

| Provider | Container | Database | Cache | Registry |
|----------|-----------|----------|-------|----------|
| AWS | ECS Fargate | RDS | ElastiCache | ECR |
| Google Cloud | Cloud Run | Cloud SQL | Memorystore | Artifact Registry |
| Azure | Container Apps | Azure Database | Azure Cache | ACR |

### Cost-Optimized Defaults

| Size | Resources | Estimated Cost |
|------|-----------|----------------|
| Small | 1 vCPU, 2GB RAM | $10-15/month |
| Medium | 2 vCPU, 4GB RAM | $25-35/month |
| Large | 4 vCPU, 8GB RAM | $60-80/month |

[@sahilnyk](https://github.com/sahilnyk)
