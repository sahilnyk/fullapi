# Spec-Driven `fullapi` — Design

Date: 2026-07-06

## Problem

The current `fullapi` is a one-shot scaffolder: it generates a FastAPI project
from CLI flags/presets and then never touches the project again. Value is
delivered once (t=0) and the tool leaves. This is a crowded, solved space
(cookiecutter, tiangolo's template) and the tool has no recurring reason to
exist. It "doesn't solve a problem."

## Solution

Make an `api.yaml` **spec the single source of truth** for the API, enforced
over the whole lifetime of the project. Two verbs:

- `fullapi gen`   — spec → generate/update the FastAPI project (t=0 value)
- `fullapi check` — diff the live app against the spec, fail on breaking
  changes (t=1..∞ value; runs in CI)

`gen` alone is just a generator. `check` alone has nothing to check. Together
they form a **living contract**: the spec keeps enforcing itself on every
commit. That recurring enforcement is what makes the tool necessary.

## The spec: `api.yaml`

```yaml
name: my_api
database: postgres        # none | sqlite | postgres
auth: jwt                 # optional; enables JWT auth scaffolding
resources:
  - name: user
    fields:
      email: str
      age: int
      is_active: bool
    auth: true            # protect this resource's routes
```

- One file, declarative. Replaces all presets and the CLI flag matrix.
- Each resource generates: SQLAlchemy model, Pydantic schema, CRUD, REST router
  (standard list/get/create/update/delete routes).
- Field types map to Python/SQLAlchemy/Pydantic types via one shared table
  (DRY — the same map drives generation and the expected-schema derivation).

## Commands

### `fullapi gen`
Pure `spec → file contents` transform, then a single writer flushes to disk.
Deterministic, idempotent, no hidden flags. Absorbs everything presets/flags
did before.

### `fullapi check`
1. Import the generated/live FastAPI app object and call `app.openapi()` to get
   the **actual** served schema. (Runs in the user's project where deps are
   installed; accuracy over guessing — static parsing would give false
   confidence.)
2. Derive the **expected** OpenAPI-shaped schema from `api.yaml` using the same
   type map as `gen`.
3. Diff expected vs actual, classifying each change:
   - **safe** — added optional field, new route
   - **breaking** — removed field/route, type change, required tightened
4. Print a minimal report. Exit non-zero if any breaking change → CI gate.

## Architecture (DRY / SOLID)

```
fullapi/
  spec/        # load + validate api.yaml → typed Spec dataclasses (SSOT)
  generate/    # Spec → file contents (pure functions); one writer flushes disk
  check/       # extract actual OpenAPI, derive expected, diff, classify
  cli.py       # thin dispatch: gen | check. No banner. Minimal output.
  types.py     # shared field-type map used by both generate/ and check/
```

- **Single Responsibility:** each package does one thing; `cli.py` only routes.
- **DRY:** the field-type map is defined once and consumed by both `generate/`
  and `check/` so generation and enforcement can never disagree.
- **Open/Closed:** new field types or resource features are added by extending
  the type map / spec model, not by editing command logic.
- **Testable in isolation:** `spec` (parse/validate), `generate` (pure spec→str),
  and `check` (diff logic on fixture schemas) each unit-test without the others.

## Terminal output

- Remove the ascii `BANNER` in `cli.py` entirely.
- Minimal, quiet output. `gen`: a short list of written files. `check`: a short
  pass/fail summary with breaking changes listed. No decorative art, no
  overwhelming feature dumps.

## Removed (clean slate)

- ascii `BANNER`
- presets and the CLI flag matrix (`--basic/--full/--db/--auth/...`)
- dead cloud `deployers/` and cloud templates
- `demoapps/` (already staged for deletion) and `INTERVIEW_PREP.md`
- The `analyzers/` OpenAPI-reading logic is salvaged into `check/`.

## Success criteria

1. `fullapi gen` on the example `api.yaml` produces an importable FastAPI
   project whose `app.openapi()` matches the spec-derived expected schema.
2. `fullapi check` exits 0 when code matches spec.
3. `fullapi check` exits non-zero and names the change when a field type is
   changed or a resource/route is removed.
4. No ascii banner; `--help` and command output are minimal.
5. `spec/`, `generate/`, `check/` each have isolated unit tests that pass.

## Out of scope (for now)

- Cloud deployment.
- Migrations diffing (Alembic autogenerate stays as generated output, not
  enforced by `check`).
- Non-REST route shapes, nested/related resources.
