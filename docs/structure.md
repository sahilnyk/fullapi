# Project Structure

`fullapi gen` writes everything under `app/`, next to `requirements.txt`. The exact files depend on `database` and `auth` in `api.yaml`.

## No Database (`database: none`)

```
app/
├── __init__.py
├── main.py              # FastAPI instance, routers, /health
├── auth.py               # JWT helpers (only if auth: jwt)
├── schemas/
│   ├── __init__.py
│   └── <resource>.py    # <Resource>Create / <Resource>Response
└── routers/
    ├── __init__.py
    └── <resource>.py    # CRUD routes, in-memory dict store
requirements.txt
```

## With a Database (`database: sqlite` or `postgres`)

```
app/
├── __init__.py
├── main.py               # FastAPI instance, lifespan creates tables, routers, /health
├── config.py              # pydantic-settings: APP_NAME, DATABASE_URL, SECRET_KEY
├── database.py            # SQLAlchemy engine, SessionLocal, Base, get_db()
├── auth.py                 # JWT helpers (only if auth: jwt)
├── models/
│   ├── __init__.py
│   └── <resource>.py     # SQLAlchemy model
├── schemas/
│   ├── __init__.py
│   └── <resource>.py     # <Resource>Create / <Resource>Response
├── crud/
│   ├── __init__.py
│   └── <resource>.py     # list / get / create / update / delete
└── routers/
    ├── __init__.py
    └── <resource>.py     # CRUD routes, backed by crud/<resource>.py
requirements.txt
```

## File Descriptions

### app/main.py
Creates the FastAPI instance, includes each resource's router, registers a `/health` endpoint. When a database is configured, wires a `lifespan` handler that calls `Base.metadata.create_all()` on startup.

### app/config.py (database only)
`pydantic-settings` `Settings` class: `APP_NAME`, `DATABASE_URL`, `SECRET_KEY`. Reads from `.env` if present.

### app/database.py (database only)
SQLAlchemy `engine`, `SessionLocal`, declarative `Base`, and a `get_db()` dependency.

### app/auth.py (auth only)
`OAuth2PasswordBearer` scheme plus `create_access_token()` / `get_current_user()` built on `python-jose`.

### app/models/
One SQLAlchemy model per resource — an `id` primary key plus one column per spec field.

### app/schemas/
One Pydantic module per resource — a `<Resource>Create` request model and a `<Resource>Response` model (`from_attributes=True`).

### app/crud/ (database only)
`list_/get_/create_/update_/delete_<resource>()` functions operating on a `Session`.

### app/routers/
One `APIRouter` per resource exposing `GET /`, `GET /{id}`, `POST /`, `PUT /{id}`, `DELETE /{id}` at `/<resource>s`, backed by CRUD functions (or an in-memory dict when there's no database).
