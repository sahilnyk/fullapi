<div align="center">

# fullapi

Spec-driven FastAPI: generate a project from `api.yaml`, then enforce it in CI.

[![PyPI](https://img.shields.io/pypi/v/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Python](https://img.shields.io/pypi/pyversions/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Downloads](https://img.shields.io/pypi/dm/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![CI](https://github.com/sahilnyk/fullapi/actions/workflows/ci.yml/badge.svg)](https://github.com/sahilnyk/fullapi/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/fullapi?color=009688)](https://github.com/sahilnyk/fullapi/blob/master/LICENSE)

</div>

## Why

Scaffolders build once, then leave you on your own. `fullapi` doesn't. `gen`
builds the project from `api.yaml`, `check` keeps it honest: change a field,
drop a route, and CI fails instead of your API quietly drifting from the spec.

## Quick Start

```bash
pip install fullapi
```

Write `api.yaml` (or run `fullapi init` for a starter file):

```yaml
name: shop_api
database: sqlite        # none | sqlite | postgres
auth: jwt               # optional
resources:
  - name: product
    fields:
      title: str
      price: float
      note: str?        # trailing ? = optional
    auth: true          # protect this resource's routes
```

Generate and run:

```bash
fullapi gen                       # api.yaml -> ./app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Enforce in CI:

```bash
fullapi check                     # exits non-zero on breaking changes
```

## Commands

| Command | Description |
|---------|-------------|
| `fullapi init [spec]` | Write a starter api.yaml |
| `fullapi gen [spec] [-o dir]` | Generate the project from the spec |
| `fullapi check [spec] [--app app.main:app]` | Fail on breaking drift from the spec |

## How `check` works

It reads the live app's real `app.openapi()`, derives the expected schema from
`api.yaml`, and diffs them. Removed routes/fields, type changes, and newly
required fields are **breaking** (non-zero exit); added routes and optional
fields are **safe**.

Built and maintained by [@sahilnyk](https://github.com/sahilnyk).
