<div align="center">

# 🕊️ fullapi

**FastAPI project scaffolder — one command, full stack**

[![PyPI](https://img.shields.io/pypi/v/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Python](https://img.shields.io/pypi/pyversions/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![License](https://img.shields.io/github/license/sahilnyk/fullapi?color=009688)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/fullapi?color=009688)](https://pypi.org/project/fullapi/)

</div>

## Quick Start

```bash
pip install fullapi
fullapi new my_api --preset production
cd my_api && pip install -r requirements.txt
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for auto-generated API documentation.

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
```

## Presets

| Preset | Description |
|--------|-------------|
| `production` | Full setup: PostgreSQL + auth + Docker + Redis + middleware + logging |
| `microservice` | Lightweight: SQLite + Docker + middleware + logging |
| `docker-ready` | Full mode with PostgreSQL + Docker + logging |
| `minimal` | Bare essentials, nothing else |

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
  --template PATH      Custom template directory
  --preset NAME        Use a preset configuration
```

## Features

✨ **Zero Dependencies** — Pure Python stdlib  
⚡ **Instant Setup** — Complete project in seconds  
🎯 **Production Ready** — Auth, Docker, DB migrations, caching  
🔧 **Extensible** — Add routers/models to existing projects  
🩺 **Health Checks** — `fullapi doctor` validates structure  
📦 **Presets** — Save common configurations  
🎨 **Custom Templates** — Bring your own boilerplate  

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

### Full Mode (--db postgresql --auth --docker)
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

# Custom template
fullapi new api --template ./my_template
```

## Contributing

1. Keep it stdlib only — no new dependencies
2. Test your changes: `pip install -e . && fullapi new test_project --full`
3. One feature per PR

## License

MIT License — see [LICENSE](LICENSE)

**Created by** [Sahil Nayak](https://github.com/sahilnyk)
