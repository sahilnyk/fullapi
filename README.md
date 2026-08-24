<div align="center">

# fullapi

Spec-driven FastAPI: generate a project from `api.yaml`, then enforce it in CI.

[![PyPI](https://img.shields.io/pypi/v/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Python](https://img.shields.io/pypi/pyversions/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Downloads](https://img.shields.io/pypi/dm/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![Status](https://img.shields.io/pypi/status/fullapi?color=009688)](https://pypi.org/project/fullapi/)
[![License](https://img.shields.io/pypi/l/fullapi?color=009688)](https://pypi.org/project/fullapi/)

</div>

## Why

Every FastAPI project ends up with the same folder layout, the same CRUD
routes, the same Pydantic models copied and renamed. `fullapi` generates that
from one `api.yaml` file instead. The part that actually matters is `check`:
it fails CI the moment the running app stops matching the spec, so the spec
stays true instead of turning into documentation nobody trusts.

## Install

```bash
pip install fullapi
```

Needs Python 3.9 or newer.

## Setup

Start with a spec file. Either write `api.yaml` by hand or run:

```bash
fullapi init
```

which drops a starter file you can edit. A minimal spec looks like this:

```yaml
name: shop_api
database: sqlite        # none | sqlite | postgres
auth: jwt                # optional
resources:
  - name: product
    fields:
      title: str
      price: float
      note: str?         # trailing ? marks the field optional
    auth: true            # protect this resource's routes
```

Each entry under `resources` becomes a full CRUD resource: a database model,
request and response schemas, and the routes to create, read, update, and
delete it.

## Generate and run

```bash
fullapi gen                       # api.yaml -> ./app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`gen` writes a working FastAPI project into `./app` (or wherever you point
`-o`). At this point you have a normal FastAPI codebase: read it, extend it,
add your own routes alongside the generated ones.

## Keep it honest

As the project grows, the code and the spec can drift apart. Someone renames
a field, drops a route, or makes something required without touching
`api.yaml`. `check` catches that:

```bash
fullapi check                     # exits non-zero on breaking changes
```

Wire it into CI and a spec/app mismatch fails the build instead of shipping
quietly.

## Commands

| Command | Description |
|---------|-------------|
| `fullapi init [spec]` | Write a starter api.yaml |
| `fullapi gen [spec] [-o dir]` | Generate the project from the spec |
| `fullapi check [spec] [--app app.main:app]` | Fail on breaking drift from the spec |

## How `check` works

It imports your live app and calls its real `app.openapi()` method, the same
schema FastAPI would serve at `/openapi.json`, then compares that against
what `api.yaml` says should exist. A route or field that disappeared, a type
that changed, or a field that became required without a matching spec
change: all of that counts as breaking and exits non-zero. New routes and
new optional fields are safe and don't fail the build.

Built and maintained by [@sahilnyk](https://github.com/sahilnyk).
