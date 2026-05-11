# fullapi

A FastAPI project scaffolder that generates complete project structures with one command. Built with pure Python stdlib - no external dependencies.

## Installation

Install from PyPI:

```bash
pip install fullapi
```

Or install from source:

```bash
git clone https://github.com/sahilnyk/fullapi.git
cd fullapi
pip install -e .
```

## Quick Start

Create a new project interactively:

```bash
fullapi new my_project
```

This starts an interactive prompt where you select:
- Mode (basic or full)
- Database (none, sqlite, postgresql, mysql)
- Authentication (none or JWT)
- Docker support

## Commands

| Command | Description |
|---------|-------------|
| `fullapi new <name>` | Create new project with prompts |
| `fullapi new <name> --basic` | Basic mode, skip prompts |
| `fullapi new <name> --full` | Full mode, skip prompts |
| `fullapi new <name> --full --db postgresql --auth --docker` | All features |
| `fullapi --version` | Show version |
| `fullapi --help` | Show help |

## CLI Flags

| Flag | Values | Description |
|------|--------|-------------|
| `--basic` | - | Minimal project structure |
| `--full` | - | Complete production structure |
| `--db` | none, sqlite, postgresql, mysql | Database choice |
| `--auth` | - | Add JWT authentication |
| `--docker` | - | Add Docker files |

## What Gets Created

### Basic Mode

A minimal starting point for small APIs:

```
my_project/
├── main.py
├── routers/
│   └── health.py
├── schemas/
│   └── base.py
├── core/
│   └── config.py
└── requirements.txt
```

### Full Mode

Production-ready structure with all components:

```
my_project/
├── main.py
├── routers/
│   ├── __init__.py
│   ├── health.py
│   └── users.py
├── models/
│   ├── __init__.py
│   └── user.py
├── schemas/
│   ├── __init__.py
│   ├── base.py
│   └── user.py
├── crud/
│   ├── __init__.py
│   └── user.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── security.py      (if --auth)
├── db/
│   ├── __init__.py
│   └── session.py       (if --db)
├── tests/
│   └── test_main.py
├── deps.py
├── .env.example
├── requirements.txt
├── Dockerfile           (if --docker)
└── docker-compose.yml   (if --docker)
```

## Features

- Interactive prompts for configuration
- CLI flags for automation
- Database support: SQLite, PostgreSQL, MySQL
- JWT authentication with OAuth2
- Docker and docker-compose setup
- Progress bar during scaffolding
- Overwrite protection for existing directories
- Zero external dependencies

## Examples

Basic API:
```bash
fullapi new my_api --basic
```

Full API with PostgreSQL:
```bash
fullapi new my_api --full --db postgresql
```

Complete setup with everything:
```bash
fullapi new my_api --full --db postgresql --auth --docker
```

## Running Your Project

After scaffolding:

```bash
cd my_project
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for the auto-generated API documentation.

## Architecture

fullapi is built entirely with Python standard library:

- argparse for CLI parsing
- pathlib for file operations
- string.Template for code generation
- ANSI escape codes for terminal output

The tool uses a simple dataclass (ProjectConfig) to drive all decisions. No complex logic or external templating engines.

## Contributing

Contributions are welcome. Guidelines:

1. Keep it stdlib only - no new dependencies
2. Write clean, readable code
3. Test your changes before submitting
4. One feature per PR

To contribute:

```bash
# Fork and clone
git clone https://github.com/sahilnyk/fullapi.git
cd fullapi

# Make changes
# ...

# Test
pip install -e .
fullapi new test_project --full

# Submit PR
```

## Roadmap

- Basic scaffolding (done)
- Full scaffolding with models/CRUD (done)
- Database support (done)
- JWT authentication (done)
- Docker support (done)
- Progress bar (done)
- Add router/model to existing projects (planned)
- Alembic migrations (planned)
- Redis support (planned)
- Custom templates (planned)
- Middleware support (planned)
- Logging support (planned)

## License

MIT License - see LICENSE file for details.

## Author

Sahil Nayak - https://github.com/sahilnyk
