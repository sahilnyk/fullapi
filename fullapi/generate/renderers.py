"""Pure renderers: turn a `Spec` into a {relative-path: file-text} mapping.

No side effects here. Type mapping goes through `fullapi.types.resolve` so
generation can never disagree with the rest of the stack.
"""

from fullapi.spec import Spec, Resource
from fullapi.types import resolve


def _class_name(resource: Resource) -> str:
    """Capitalized singular, e.g. "user" -> "User"."""
    return resource.name.capitalize()


def _plural(resource: Resource) -> str:
    """Plural route/table stem, e.g. "user" -> "users"."""
    return resource.name + "s"


def render(spec: Spec) -> dict[str, str]:
    """Return {relative path -> file content} for the whole project (pure)."""
    has_db = spec.database != "none"
    files: dict[str, str] = {}

    files["app/__init__.py"] = ""
    files["requirements.txt"] = _requirements(spec)
    files["app/main.py"] = _main(spec)

    if has_db:
        files["app/config.py"] = _config(spec)
        files["app/database.py"] = _database(spec)
        files["app/models/__init__.py"] = ""
        files["app/crud/__init__.py"] = ""

    files["app/schemas/__init__.py"] = ""
    files["app/routers/__init__.py"] = ""

    if spec.auth:
        files["app/auth.py"] = _auth()

    for res in spec.resources:
        files[f"app/schemas/{res.name}.py"] = _schema(res)
        files[f"app/routers/{res.name}.py"] = _router(spec, res, has_db)
        if has_db:
            files[f"app/models/{res.name}.py"] = _model(res)
            files[f"app/crud/{res.name}.py"] = _crud(res)

    return files


def _requirements(spec: Spec) -> str:
    reqs = ["fastapi", "uvicorn", "pydantic", "pydantic-settings"]
    if spec.database != "none":
        reqs.append("sqlalchemy")
        if spec.database == "postgres":
            reqs.append("psycopg2-binary")
    if spec.auth:
        reqs += ["python-jose[cryptography]", "passlib[bcrypt]"]
    return "\n".join(reqs) + "\n"


def _config(spec: Spec) -> str:
    default_url = "sqlite:///./app.db" if spec.database == "sqlite" else ""
    return (
        "from pydantic_settings import BaseSettings\n\n\n"
        "class Settings(BaseSettings):\n"
        f'    APP_NAME: str = "{spec.name}"\n'
        f'    DATABASE_URL: str = "{default_url}"\n'
        '    SECRET_KEY: str = "change-me"\n\n'
        '    model_config = {"env_file": ".env"}\n\n\n'
        "settings = Settings()\n"
    )


def _database(spec: Spec) -> str:
    connect_args = ', connect_args={"check_same_thread": False}' if spec.database == "sqlite" else ""
    return (
        "from sqlalchemy import create_engine\n"
        "from sqlalchemy.orm import sessionmaker, declarative_base\n"
        "from app.config import settings\n\n"
        f"engine = create_engine(settings.DATABASE_URL{connect_args})\n"
        "SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)\n"
        "Base = declarative_base()\n\n\n"
        "def get_db():\n"
        "    db = SessionLocal()\n"
        "    try:\n"
        "        yield db\n"
        "    finally:\n"
        "        db.close()\n"
    )


def _model(res: Resource) -> str:
    cols = ["    id = Column(Integer, primary_key=True, index=True)"]
    used = {"Integer"}
    for f in res.fields:
        satype = resolve(f.type).sqlalchemy
        used.add(satype)
        nullable = "False" if f.required else "True"
        cols.append(f"    {f.name} = Column({satype}, nullable={nullable})")
    imports = ", ".join(sorted(used))
    return (
        f"from sqlalchemy import Column, {imports}\n"
        "from app.database import Base\n\n\n"
        f"class {_class_name(res)}(Base):\n"
        f'    __tablename__ = "{_plural(res)}"\n\n'
        + "\n".join(cols)
        + "\n"
    )


def _schema(res: Resource) -> str:
    cls = _class_name(res)
    create_lines = []
    resp_lines = ["    id: int"]
    for f in res.fields:
        py = resolve(f.type).python
        if f.required:
            create_lines.append(f"    {f.name}: {py}")
            resp_lines.append(f"    {f.name}: {py}")
        else:
            create_lines.append(f"    {f.name}: Optional[{py}] = None")
            resp_lines.append(f"    {f.name}: Optional[{py}] = None")
    if not create_lines:
        create_lines.append("    pass")
    return (
        "from typing import Optional\n"
        "from pydantic import BaseModel\n\n\n"
        f"class {cls}Create(BaseModel):\n"
        + "\n".join(create_lines)
        + "\n\n\n"
        f"class {cls}Response(BaseModel):\n"
        + "\n".join(resp_lines)
        + "\n\n"
        '    model_config = {"from_attributes": True}\n'
    )


def _crud(res: Resource) -> str:
    cls = _class_name(res)
    assigns = ", ".join(f"{f.name}=payload.{f.name}" for f in res.fields)
    set_fields = "\n".join(
        f"        setattr(obj, {f.name!r}, getattr(payload, {f.name!r}))"
        for f in res.fields
    ) or "        pass"
    return (
        "from sqlalchemy.orm import Session\n"
        f"from app.models.{res.name} import {cls}\n"
        f"from app.schemas.{res.name} import {cls}Create\n\n\n"
        f"def list_{res.name}(db: Session, skip: int = 0, limit: int = 100):\n"
        f"    return db.query({cls}).offset(skip).limit(limit).all()\n\n\n"
        f"def get_{res.name}(db: Session, item_id: int):\n"
        f"    return db.query({cls}).filter({cls}.id == item_id).first()\n\n\n"
        f"def create_{res.name}(db: Session, payload: {cls}Create):\n"
        f"    obj = {cls}({assigns})\n"
        "    db.add(obj)\n"
        "    db.commit()\n"
        "    db.refresh(obj)\n"
        "    return obj\n\n\n"
        f"def update_{res.name}(db: Session, item_id: int, payload: {cls}Create):\n"
        f"    obj = get_{res.name}(db, item_id)\n"
        "    if obj is None:\n"
        "        return None\n"
        f"{set_fields}\n"
        "    db.commit()\n"
        "    db.refresh(obj)\n"
        "    return obj\n\n\n"
        f"def delete_{res.name}(db: Session, item_id: int):\n"
        f"    obj = get_{res.name}(db, item_id)\n"
        "    if obj is None:\n"
        "        return False\n"
        "    db.delete(obj)\n"
        "    db.commit()\n"
        "    return True\n"
    )


def _router(spec: Spec, res: Resource, has_db: bool) -> str:
    cls = _class_name(res)
    plural = _plural(res)
    protected = spec.auth or res.auth
    auth_dep = ", current_user=Depends(get_current_user)" if protected else ""

    if not has_db:
        # In-memory router when there is no database.
        if protected:
            header = "from fastapi import APIRouter, Depends, HTTPException\n"
            header += "from app.auth import get_current_user\n"
        else:
            header = "from fastapi import APIRouter, HTTPException\n"
        header += (
            f"from app.schemas.{res.name} import {cls}Create, {cls}Response\n\n"
            f'router = APIRouter(prefix="/{plural}", tags=["{plural}"])\n\n'
            "_db: dict[int, dict] = {}\n"
            "_next_id = {\"v\": 1}\n\n\n"
        )
        return header + (
            f"@router.get(\"/\", response_model=list[{cls}Response])\n"
            f"def list_{plural}({auth_dep.lstrip(', ')}):\n"
            "    return list(_db.values())\n\n\n"
            f"@router.get(\"/{{item_id}}\", response_model={cls}Response)\n"
            f"def get_{res.name}(item_id: int{auth_dep}):\n"
            "    if item_id not in _db:\n"
            '        raise HTTPException(404, "Not found")\n'
            "    return _db[item_id]\n\n\n"
            f"@router.post(\"/\", response_model={cls}Response, status_code=201)\n"
            f"def create_{res.name}(payload: {cls}Create{auth_dep}):\n"
            '    item_id = _next_id["v"]\n'
            '    _next_id["v"] += 1\n'
            '    _db[item_id] = {"id": item_id, **payload.model_dump()}\n'
            "    return _db[item_id]\n\n\n"
            f"@router.put(\"/{{item_id}}\", response_model={cls}Response)\n"
            f"def update_{res.name}(item_id: int, payload: {cls}Create{auth_dep}):\n"
            "    if item_id not in _db:\n"
            '        raise HTTPException(404, "Not found")\n'
            '    _db[item_id] = {"id": item_id, **payload.model_dump()}\n'
            "    return _db[item_id]\n\n\n"
            f"@router.delete(\"/{{item_id}}\", status_code=204)\n"
            f"def delete_{res.name}(item_id: int{auth_dep}):\n"
            "    if item_id not in _db:\n"
            '        raise HTTPException(404, "Not found")\n'
            "    del _db[item_id]\n"
        )

    header = (
        "from fastapi import APIRouter, Depends, HTTPException\n"
        "from sqlalchemy.orm import Session\n"
        "from app.database import get_db\n"
        f"from app.crud import {res.name} as crud\n"
        f"from app.schemas.{res.name} import {cls}Create, {cls}Response\n"
    )
    if protected:
        header += "from app.auth import get_current_user\n"
    header += (
        f'\nrouter = APIRouter(prefix="/{plural}", tags=["{plural}"])\n\n\n'
    )
    return header + (
        f"@router.get(\"/\", response_model=list[{cls}Response])\n"
        f"def list_{plural}(skip: int = 0, limit: int = 100, db: Session = Depends(get_db){auth_dep}):\n"
        f"    return crud.list_{res.name}(db, skip, limit)\n\n\n"
        f"@router.get(\"/{{item_id}}\", response_model={cls}Response)\n"
        f"def get_{res.name}(item_id: int, db: Session = Depends(get_db){auth_dep}):\n"
        f"    obj = crud.get_{res.name}(db, item_id)\n"
        "    if obj is None:\n"
        '        raise HTTPException(404, "Not found")\n'
        "    return obj\n\n\n"
        f"@router.post(\"/\", response_model={cls}Response, status_code=201)\n"
        f"def create_{res.name}(payload: {cls}Create, db: Session = Depends(get_db){auth_dep}):\n"
        f"    return crud.create_{res.name}(db, payload)\n\n\n"
        f"@router.put(\"/{{item_id}}\", response_model={cls}Response)\n"
        f"def update_{res.name}(item_id: int, payload: {cls}Create, db: Session = Depends(get_db){auth_dep}):\n"
        f"    obj = crud.update_{res.name}(db, item_id, payload)\n"
        "    if obj is None:\n"
        '        raise HTTPException(404, "Not found")\n'
        "    return obj\n\n\n"
        f"@router.delete(\"/{{item_id}}\", status_code=204)\n"
        f"def delete_{res.name}(item_id: int, db: Session = Depends(get_db){auth_dep}):\n"
        f"    if not crud.delete_{res.name}(db, item_id):\n"
        '        raise HTTPException(404, "Not found")\n'
    )


def _auth() -> str:
    return (
        "from fastapi import Depends, HTTPException\n"
        "from fastapi.security import OAuth2PasswordBearer\n"
        "from jose import JWTError, jwt\n"
        "from app.config import settings\n\n"
        'oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")\n\n\n'
        "def create_access_token(data: dict) -> str:\n"
        '    return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")\n\n\n'
        "def get_current_user(token: str = Depends(oauth2_scheme)):\n"
        "    try:\n"
        '        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])\n'
        "    except JWTError:\n"
        '        raise HTTPException(status_code=401, detail="Invalid token")\n'
    )


def _main(spec: Spec) -> str:
    has_db = spec.database != "none"
    imports = ["from fastapi import FastAPI"]
    if has_db:
        imports.append("from contextlib import asynccontextmanager")
        imports.append("from app.database import engine, Base")
        # import models so tables register on Base.metadata
        for res in spec.resources:
            imports.append(f"from app.models.{res.name} import {_class_name(res)}  # noqa: F401")
    for res in spec.resources:
        imports.append(f"from app.routers.{res.name} import router as {res.name}_router")

    body = "\n".join(imports) + "\n\n"

    if has_db:
        body += (
            "\n@asynccontextmanager\n"
            "async def lifespan(app: FastAPI):\n"
            "    Base.metadata.create_all(bind=engine)\n"
            "    yield\n\n\n"
            f'app = FastAPI(title="{spec.name}", lifespan=lifespan)\n\n'
        )
    else:
        body += f'\napp = FastAPI(title="{spec.name}")\n\n'

    for res in spec.resources:
        body += f"app.include_router({res.name}_router)\n"

    body += (
        "\n\n@app.get(\"/health\")\n"
        "def health():\n"
        '    return {"status": "ok"}\n'
    )
    return body
