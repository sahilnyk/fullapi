# Configuration Options

Everything is configured through `api.yaml`. There are no CLI flags for project shape — the spec is the single source of truth for both `gen` and `check`.

## Top-Level Keys

```yaml
name: shop_api        # required — used as the FastAPI app title
database: sqlite       # none | sqlite | postgres (default: none)
auth: jwt               # optional — enables JWT scaffolding, protects every resource
resources: [...]        # list of resources (see below)
```

## Database Options

### None (default)
No database configuration is generated. Resources fall back to a simple in-memory dict-backed store, useful for prototyping.

### SQLite
- Generates `app/database.py` and `app/config.py` with a file-based `sqlite:///./app.db` connection
- Generates a SQLAlchemy model, CRUD module, and DB-backed router per resource
- No server required

### PostgreSQL
- Same generated shape as SQLite, but `DATABASE_URL` is left blank for you to set (e.g. via `.env`)
- Adds `psycopg2-binary` to `requirements.txt`

## Resources

Each resource becomes a full CRUD slice: a Pydantic schema, a router with `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}`, and — if a database is configured — a SQLAlchemy model and CRUD module.

```yaml
resources:
  - name: product        # singular, lowercase — routes are pluralized ("products")
    fields:
      title: str
      price: float
      note: str?          # trailing ? = optional field
    auth: true             # protect just this resource's routes
```

Supported field types: `str`, `int`, `float`, `bool`.

## Authentication

### None (default)
No auth scaffolding. All endpoints are public.

### JWT
Set `auth: jwt` at the top level to generate `app/auth.py`:

- `OAuth2PasswordBearer` scheme
- `create_access_token()` / `get_current_user()` helpers using `python-jose`
- Adds `python-jose[cryptography]` and `passlib[bcrypt]` to `requirements.txt`

Top-level `auth: jwt` protects every resource's routes by default. Set `auth: true` on an individual resource to protect just that one without enabling it globally.

```python
from fastapi import Depends, APIRouter
from app.auth import get_current_user

router = APIRouter()

@router.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {"message": f"Hello {user}"}
```
