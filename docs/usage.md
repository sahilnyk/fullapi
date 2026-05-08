# Usage Guide

## Creating a New Project

### Interactive Mode

The simplest way to create a project:

```bash
fullapi new my_project
```

This starts an interactive prompt where you choose:

1. **Mode**: Basic or Full
2. **Database**: None, SQLite, PostgreSQL, or MySQL
3. **Authentication**: None or JWT
4. **Docker**: Yes or No

### Non-Interactive Mode (Flags)

For automation or scripts, use flags to skip prompts:

```bash
# Basic mode
fullapi new my_project --basic

# Full mode with PostgreSQL
fullapi new my_project --full --db postgresql

# Full mode with everything
fullapi new my_project --full --db postgresql --auth --docker
```

## Available Commands

| Command | Description |
|---------|-------------|
| `fullapi new <name>` | Create project with prompts |
| `fullapi new <name> --basic` | Basic mode, no prompts |
| `fullapi new <name> --full` | Full mode, no prompts |
| `fullapi --version` | Show version |
| `fullapi --help` | Show help |

## CLI Flags Reference

| Flag | Values | Description |
|------|--------|-------------|
| `--basic` | - | Minimal structure |
| `--full` | - | Complete structure with models, CRUD |
| `--db` | none, sqlite, postgresql, mysql | Database choice |
| `--auth` | - | Add JWT authentication |
| `--docker` | - | Add Docker files |

## Running Your Project

After scaffolding:

```bash
cd my_project
pip install -r requirements.txt
uvicorn main:app --reload
```

Your API is now running at `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

## Handling Existing Directories

If the project directory already exists, fullapi will ask:

```
Directory 'my_project' already exists.
    1. Overwrite
    2. Cancel
```

Choose 1 to replace the existing directory, or 2 to cancel.
