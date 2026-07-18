# Usage Guide

## Writing a Spec

Everything starts from `api.yaml`. Run `fullapi init` to get a starter file with a worked example, or write one from scratch:

```yaml
name: shop_api
database: sqlite        # none | sqlite | postgres
auth: jwt                # optional, protects every resource by default
resources:
  - name: product
    fields:
      title: str
      price: float
      note: str?          # trailing ? = optional field
    auth: true             # protect just this resource's routes
```

Supported field types: `str`, `int`, `float`, `bool` — each may be suffixed with `?` to make it optional.

```bash
fullapi init                # writes ./api.yaml (fails if it already exists)
fullapi init other.yaml     # write to a different path
```

## Generating a Project

```bash
fullapi gen                # reads ./api.yaml, writes to ./app
fullapi gen other.yaml     # use a different spec file
fullapi gen -o build       # write to a different output directory
```

Run the generated project:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Your API is now running at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

## Checking for Drift

`fullapi check` fails CI when the live app no longer matches `api.yaml`:

```bash
fullapi check                       # reads ./api.yaml, imports app.main:app
fullapi check other.yaml            # check against a different spec
fullapi check --app mypkg.main:app  # import a different app object
fullapi check -v                    # also list safe (non-breaking) changes
```

It exits non-zero when it finds breaking changes: removed routes, removed fields, changed field types, or fields that became required. Added routes and added optional fields are reported as safe and don't fail the build.

## Command Reference

| Command | Description |
|---------|-------------|
| `fullapi init [spec]` | Write a starter api.yaml |
| `fullapi gen [spec] [-o dir]` | Generate the project from the spec |
| `fullapi check [spec] [--app app.main:app] [-v]` | Fail on breaking drift from the spec |
| `fullapi --version` | Show version |
| `fullapi --help` | Show help |
