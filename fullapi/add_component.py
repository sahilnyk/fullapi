"""Add components to existing fullapi projects."""

import json
from pathlib import Path
from string import Template

from fullapi.colors import (
    ICON_CHECK, ICON_WARNING,
    success, warning, info, muted, bold, color, Style
)
from fullapi.prompt import show_loading_animation


def add_component_to_project(component_type: str, component_name: str) -> None:
    """Add a component (router/model) to an existing project."""
    component_name = component_name.capitalize()

    print()
    print(f"  {bold('Adding component:')} {info(component_name)} {muted(f'({component_type})')}")
    print()

    if component_type == "router":
        _add_router(component_name)
    elif component_type == "model":
        _add_model(component_name)

    show_loading_animation("Finalizing component addition", 0.5)


def _add_router(name: str) -> None:
    """Add a new router with CRUD operations."""
    config_path = Path(".fullapi.json")
    has_db = False
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            has_db = config.get("database", "none") != "none"
        except (json.JSONDecodeError, OSError):
            pass

    if not has_db:
        has_db = Path("db").exists()

    template_vars = {
        "model_name": name,
        "model_name_lower": name.lower(),
        "model_name_plural": name.lower() + "s",
    }

    router_path = Path(f"routers/{name.lower()}.py")
    if router_path.exists():
        print(f"  {ICON_WARNING}  {warning(f'Router {name.lower()}.py already exists')}")
        return

    router_path.parent.mkdir(exist_ok=True)

    if has_db:
        router_content = Template(_get_router_template_with_db()).substitute(template_vars)
    else:
        router_content = Template(_get_router_template_simple()).substitute(template_vars)

    router_path.write_text(router_content)
    _show_progress(f"routers/{name.lower()}.py")

    schema_path = Path(f"schemas/{name.lower()}.py")
    if not schema_path.exists():
        schema_path.parent.mkdir(exist_ok=True)
        schema_content = Template(_get_schema_template()).substitute(template_vars)
        schema_path.write_text(schema_content)
        _show_progress(f"schemas/{name.lower()}.py")

    _update_main_py(name)


def _add_model(name: str) -> None:
    """Add a new model with schema."""
    template_vars = {
        "model_name": name,
        "model_name_lower": name.lower(),
        "model_name_plural": name.lower() + "s",
    }

    if not Path("db").exists():
        print(f"  {ICON_WARNING}  {warning('Project does not have database support')}")
        print(f"  {info('Tip:')} Create a new project with --db flag or use 'fullapi add router' first")
        return

    model_path = Path(f"models/{name.lower()}.py")
    if model_path.exists():
        print(f"  {ICON_WARNING}  {warning(f'Model {name.lower()}.py already exists')}")
        return

    model_path.parent.mkdir(exist_ok=True)
    model_path.write_text(Template(_get_model_template()).substitute(template_vars))
    _show_progress(f"models/{name.lower()}.py")

    schema_path = Path(f"schemas/{name.lower()}.py")
    if not schema_path.exists():
        schema_path.parent.mkdir(exist_ok=True)
        schema_path.write_text(Template(_get_schema_template()).substitute(template_vars))
        _show_progress(f"schemas/{name.lower()}.py")

    crud_path = Path(f"crud/{name.lower()}.py")
    if not crud_path.exists():
        crud_path.parent.mkdir(exist_ok=True)
        crud_path.write_text(Template(_get_crud_template()).substitute(template_vars))
        _show_progress(f"crud/{name.lower()}.py")


def _update_main_py(name: str) -> None:
    """Update main.py to include the new router."""
    main_path = Path("main.py")
    if not main_path.exists():
        return

    content = main_path.read_text()

    if f"from routers import {name.lower()}" in content:
        return

    import_line = f"from routers import {name.lower()}"
    lines = content.split("\n")

    # Add import
    if "from routers import" in content:
        for i, line in enumerate(lines):
            if line.strip().startswith("from routers import"):
                lines[i] = line.rstrip() + f", {name.lower()}"
                break
    else:
        for i, line in enumerate(lines):
            if line.strip().startswith("from fastapi import"):
                lines.insert(i + 1, import_line)
                break

    content = "\n".join(lines)

    router_line = f'app.include_router({name.lower()}.router, prefix="/{name.lower()}", tags=["{name.lower()}"])'
    lines = content.split("\n")

    if "app.include_router" in content:
        for i, line in enumerate(lines):
            if "app.include_router" in line:
                lines.insert(i, router_line)
                break
    else:
        for i, line in enumerate(lines):
            if "app = FastAPI" in line:
                lines.insert(i + 1, "")
                lines.insert(i + 2, router_line)
                break

    main_path.write_text("\n".join(lines))
    _show_progress("main.py (updated)")


def _show_progress(filename: str) -> None:
    """Show progress for component addition."""
    print(f"  {color('✓', Style.GREEN)} {muted(filename)}")


def _get_router_template_simple() -> str:
    """Get template for router without database."""
    return '''"""${model_name} router."""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from schemas.${model_name_lower} import ${model_name}Response, ${model_name}Create, ${model_name}Update

router = APIRouter()

_storage: Dict[int, dict] = {}
_id_counter: List[int] = [1]


@router.get("/", response_model=List[${model_name}Response])
def list_${model_name_plural}(skip: int = 0, limit: int = 100):
    """Retrieve ${model_name_plural}."""
    items = list(_storage.values())
    return items[skip : skip + limit]


@router.post("/", response_model=${model_name}Response, status_code=201)
def create_${model_name_lower}(payload: ${model_name}Create):
    """Create a new ${model_name_lower}."""
    item_id = _id_counter[0]
    _id_counter[0] += 1
    item = {"id": item_id, **payload.model_dump()}
    _storage[item_id] = item
    return item


@router.get("/{item_id}", response_model=${model_name}Response)
def get_${model_name_lower}(item_id: int):
    """Get a ${model_name_lower} by ID."""
    if item_id not in _storage:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    return _storage[item_id]


@router.patch("/{item_id}", response_model=${model_name}Response)
def update_${model_name_lower}(item_id: int, payload: ${model_name}Update):
    """Update a ${model_name_lower}."""
    if item_id not in _storage:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    item = _storage[item_id]
    item.update({k: v for k, v in payload.model_dump(exclude_unset=True).items()})
    _storage[item_id] = item
    return item


@router.delete("/{item_id}")
def delete_${model_name_lower}(item_id: int):
    """Delete a ${model_name_lower}."""
    if item_id not in _storage:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    del _storage[item_id]
    return {"message": "${model_name} deleted successfully"}
'''


def _get_router_template_with_db() -> str:
    """Get template for router with database."""
    return '''"""${model_name} router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from schemas.${model_name_lower} import ${model_name}Response, ${model_name}Create, ${model_name}Update
from crud.${model_name_lower} import ${model_name_lower}_crud

router = APIRouter()


@router.get("/", response_model=List[${model_name}Response])
def list_${model_name_plural}(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve ${model_name_plural}."""
    return ${model_name_lower}_crud.get_all(db, skip=skip, limit=limit)


@router.post("/", response_model=${model_name}Response, status_code=201)
def create_${model_name_lower}(payload: ${model_name}Create, db: Session = Depends(get_db)):
    """Create a new ${model_name_lower}."""
    return ${model_name_lower}_crud.create(db, obj_in=payload.model_dump())


@router.get("/{item_id}", response_model=${model_name}Response)
def get_${model_name_lower}(item_id: int, db: Session = Depends(get_db)):
    """Get a ${model_name_lower} by ID."""
    item = ${model_name_lower}_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    return item


@router.patch("/{item_id}", response_model=${model_name}Response)
def update_${model_name_lower}(item_id: int, payload: ${model_name}Update, db: Session = Depends(get_db)):
    """Update a ${model_name_lower}."""
    item = ${model_name_lower}_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    return ${model_name_lower}_crud.update(db, db_obj=item, obj_in=payload.model_dump(exclude_unset=True))


@router.delete("/{item_id}")
def delete_${model_name_lower}(item_id: int, db: Session = Depends(get_db)):
    """Delete a ${model_name_lower}."""
    item = ${model_name_lower}_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    ${model_name_lower}_crud.delete(db, item_id)
    return {"message": "${model_name} deleted successfully"}
'''


def _get_model_template() -> str:
    """Get template for model file."""
    return '''"""${model_name} model."""

from sqlalchemy import Column, Integer, String
from db.base import Base


class ${model_name}(Base):
    """${model_name} database model."""
    __tablename__ = "${model_name_plural}"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
'''


def _get_schema_template() -> str:
    """Get template for schema file."""
    return '''"""${model_name} schemas."""

from typing import Optional
from pydantic import BaseModel


class ${model_name}Base(BaseModel):
    name: str


class ${model_name}Create(${model_name}Base):
    pass


class ${model_name}Update(BaseModel):
    name: Optional[str] = None


class ${model_name}Response(${model_name}Base):
    id: int

    model_config = {"from_attributes": True}
'''


def _get_crud_template() -> str:
    """Get template for CRUD file."""
    return '''"""${model_name} CRUD operations."""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from models.${model_name_lower} import ${model_name}


class ${model_name}CRUD:
    """CRUD operations for ${model_name}."""

    def get(self, db: Session, id: int) -> Optional[${model_name}]:
        return db.query(${model_name}).filter(${model_name}.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[${model_name}]:
        return db.query(${model_name}).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: Dict[str, Any]) -> ${model_name}:
        obj = ${model_name}(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, db_obj: ${model_name}, obj_in: Dict[str, Any]) -> ${model_name}:
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        obj = self.get(db, id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True


${model_name_lower}_crud = ${model_name}CRUD()
'''
