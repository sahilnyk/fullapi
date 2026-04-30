# ⚡ fullapi

> FastAPI project scaffolder — zero dependencies, one command.

---

## What is fullapi?

`fullapi` is a CLI tool that scaffolds a complete FastAPI project for you in seconds. No more manually creating folders, writing boilerplate, or setting up project structure from scratch. One command and you're ready to code.

Inspired by tools like `cookiecutter` — simple, no magic, just works.

---

## Install

```bash
pip install fullapi
```

That's it. No extra dependencies. Pure Python stdlib.

---

## Usage

```bash
fullapi new my_project
```

Starts an interactive prompt:

```
┌─────────────────────────────────┐
│                                 │
│   ⚡ fullapi v1.0.0             │
│   FastAPI project scaffolder    │
│                                 │
└─────────────────────────────────┘

  [1] Mode
      1. basic
      2. full
  → 2

  [2] Database
      1. none
      2. sqlite
      3. postgresql
      4. mysql
  → 3

  [3] Auth
      1. none
      2. jwt
  → 2

  [4] Docker
      1. yes
      2. no
  → 1

  Creating project...

  ████████████████████░░░░░░░░░░░░  60%  creating routers...

  ✓  my_project/
  ✓  my_project/main.py
  ✓  my_project/routers/health.py
  ✓  my_project/routers/users.py
  ✓  my_project/models/user.py
  ✓  my_project/schemas/user.py
  ✓  my_project/crud/user.py
  ✓  my_project/core/config.py
  ✓  my_project/core/security.py
  ✓  my_project/db/session.py
  ✓  my_project/deps.py
  ✓  my_project/tests/test_main.py
  ✓  my_project/.env.example
  ✓  my_project/requirements.txt
  ✓  my_project/Dockerfile
  ✓  my_project/docker-compose.yml

┌──────────────────────────────────────────┐
│                                          │
│   ✅  my_project is ready!               │
│                                          │
│   cd my_project                          │
│   pip install -r requirements.txt        │
│   uvicorn main:app --reload              │
│                                          │
│   Docs → http://localhost:8000/docs      │
│                                          │
└──────────────────────────────────────────┘
```

---

## Skip prompts with flags

```bash
fullapi new my_project --basic                        # basic mode, no prompts
fullapi new my_project --full                         # full mode, no prompts
fullapi new my_project --full --db postgresql         # full + postgres
fullapi new my_project --full --db postgresql --auth  # full + postgres + jwt
fullapi new my_project --full --db postgresql --auth --docker  # everything
```

---

## Modes

### Basic

Minimal, clean starting point. Good for small APIs or learning.

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

### Full

Production-ready structure. Covers routing, models, schemas, CRUD, auth, DB, tests, Docker.

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
│   └── user.py
├── crud/
│   ├── __init__.py
│   └── user.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   └── security.py         # only if --auth selected
├── db/
│   ├── __init__.py
│   └── session.py          # only if db selected
├── deps.py
├── tests/
│   └── test_main.py
├── .env.example
├── requirements.txt
├── Dockerfile              # only if --docker selected
└── docker-compose.yml      # only if --docker selected
```

---

## Options

| Option | Description |
|--------|-------------|
| `--basic` | Scaffold basic mode, skip prompts |
| `--full` | Scaffold full mode, skip prompts |
| `--db` | Database: `none`, `sqlite`, `postgresql`, `mysql` |
| `--auth` | Add JWT authentication |
| `--docker` | Add Dockerfile and docker-compose.yml |
| `--version` | Show version |
| `--help` | Show help |

---

## Architecture

```
fullapi/
├── pyproject.toml              # package metadata + entry point
├── README.md
└── fullapi/
    ├── __init__.py
    ├── cli.py                  # entry point, parses commands + flags
    ├── prompt.py               # interactive prompts, returns config
    ├── scaffold.py             # creates folders + writes files
    ├── config.py               # ProjectConfig dataclass
    └── templates/
        ├── __init__.py
        ├── main.py             # main.py template
        ├── router.py           # router templates
        ├── model.py            # SQLAlchemy model templates
        ├── schema.py           # Pydantic schema templates
        ├── crud.py             # CRUD templates
        ├── deps.py             # dependency injection template
        ├── config.py           # core config template
        ├── security.py         # JWT security template
        ├── database.py         # DB session template
        ├── dockerfile.py       # Dockerfile template
        ├── dockercompose.py    # docker-compose template
        ├── env.py              # .env.example template
        └── requirements.py     # requirements.txt template
```

### How it flows

```
cli.py
  │
  ├── parse args + flags
  │
  └── prompt.py
        │
        ├── ask interactive questions (if no flags)
        │
        └── ProjectConfig dataclass
              │
              └── scaffold.py
                    │
                    ├── read config
                    ├── create folders via pathlib
                    ├── render templates via string.Template
                    └── write files + show progress bar
```

### ProjectConfig — drives everything

```python
@dataclass
class ProjectConfig:
    name: str
    mode: str        # basic | full
    database: str    # none | sqlite | postgresql | mysql
    auth: bool       # jwt
    docker: bool
```

Every folder, every file, every template decision is driven purely by this config object. Clean, no spaghetti.

---

## Zero Dependencies

`fullapi` uses only Python stdlib. Nothing else.

| Need | Solution |
|------|----------|
| CLI parsing | `argparse` |
| Folder/file creation | `pathlib` |
| String templating | `string.Template` |
| Terminal colors + progress bar | ANSI escape codes + `\r` |
| Interactive prompts | `input()` |

---

## Error Handling

**Project already exists:**
```
  ⚠️  Directory 'my_project' already exists.

      1. Overwrite
      2. Cancel
  →
```

**Invalid input:**
```
  ✗  Invalid choice. Pick a valid option.
```

**Missing project name:**
```
  ✗  Usage: fullapi new <project_name>
```

---

## Roadmap

- [x] Basic scaffolding
- [x] Full scaffolding
- [x] Database support (sqlite, postgresql, mysql)
- [x] JWT auth
- [x] Docker support
- [x] Progress bar
- [ ] `fullapi add router <name>` — add a new router to existing project
- [ ] `fullapi add model <name>` — add a new model to existing project
- [ ] Alembic migrations support
- [ ] Redis support
- [ ] Custom templates support

---

## Contributing

PRs welcome. Keep it stdlib only — no new dependencies.

---

## License

MIT
