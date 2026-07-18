# fullapi Documentation

Welcome to the fullapi documentation. fullapi is a spec-driven FastAPI tool: it generates a project from `api.yaml`, then enforces that spec in CI.

## What is fullapi?

Most scaffolders help once, then leave — the generated code and the thing that produced it drift apart over time. fullapi keeps `api.yaml` as the source of truth for the life of the project:

- `fullapi init` writes a starter `api.yaml` to edit.
- `fullapi gen` builds the FastAPI project from the spec.
- `fullapi check` reads the live app's `app.openapi()`, derives what the spec expects, and fails CI when they've drifted.

## Key Features

- Zero runtime dependencies beyond PyYAML
- Declarative resources — fields, types, and per-resource auth in YAML
- SQLite or PostgreSQL, or no database at all
- Optional JWT authentication (global or per-resource)
- Generated CRUD routers, Pydantic schemas, and (with a database) SQLAlchemy models
- `check` classifies drift as breaking (removed routes/fields, type changes, newly required fields) or safe (additions)

## Quick Links

- [Installation Guide](installation.md)
- [Usage Guide](usage.md)
- [Configuration Options](configuration.md)
- [Project Structure](structure.md)
- [Contributing](contributing.md)

## Get Started

```bash
pip install fullapi
fullapi init
fullapi gen
```

`init` writes a starter `api.yaml` to edit; `gen` generates `./app` from it.
