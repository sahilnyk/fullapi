"""Add components to existing fullapi projects."""

import os
import sys
from pathlib import Path
from string import Template

from fullapi.colors import (
    ICON_CHECK, ICON_CROSS, ICON_WARNING,
    success, error, warning, info, muted, bold, color, Style
)
from fullapi.prompt import show_loading_animation
from fullapi.templates import router, schema, model, crud


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
    print(f"  {ICON_CHECK}  {success(f'{component_type.capitalize()} added successfully!')}")
    print()


def _add_router(name: str) -> None:
    """Add a new router with CRUD operations."""
    template_vars = {
        "model_name": name,
        "model_name_lower": name.lower(),
        "model_name_plural": name.lower() + "s"
    }
    
    # Create router file
    router_path = Path(f"routers/{name.lower()}.py")
    if router_path.exists():
        print(f"  {ICON_WARNING}  {warning(f'Router {name.lower()}.py already exists')}")
        return
    
    router_path.parent.mkdir(exist_ok=True)
    router_content = Template(_get_router_template()).substitute(template_vars)
    router_path.write_text(router_content)
    
    _show_progress(f"routers/{name.lower()}.py")
    
    # Update main.py to include the new router
    _update_main_py(name)


def _add_model(name: str) -> None:
    """Add a new model with schema."""
    template_vars = {
        "model_name": name,
        "model_name_lower": name.lower(),
        "model_name_plural": name.lower() + "s"
    }
    
    # Check if project has database support
    if not Path("db").exists():
        print(f"  {ICON_WARNING}  {warning('Project does not have database support')}")
        print(f"  {info('Tip:')} Create a new project with --db flag or use 'fullapi add router' first")
        return
    
    # Create model file
    model_path = Path(f"models/{name.lower()}.py")
    if model_path.exists():
        print(f"  {ICON_WARNING}  {warning(f'Model {name.lower()}.py already exists')}")
        return
    
    model_path.parent.mkdir(exist_ok=True)
    model_content = Template(_get_model_template()).substitute(template_vars)
    model_path.write_text(model_content)
    
    _show_progress(f"models/{name.lower()}.py")
    
    # Create schema file
    schema_path = Path(f"schemas/{name.lower()}.py")
    if schema_path.exists():
        print(f"  {ICON_WARNING}  {warning(f'Schema {name.lower()}.py already exists')}")
        return
    
    schema_path.parent.mkdir(exist_ok=True)
    schema_content = Template(_get_schema_template()).substitute(template_vars)
    schema_path.write_text(schema_content)
    
    _show_progress(f"schemas/{name.lower()}.py")
    
    # Create CRUD file
    crud_path = Path(f"crud/{name.lower()}.py")
    if crud_path.exists():
        print(f"  {ICON_WARNING}  {warning(f'CRUD {name.lower()}.py already exists')}")
        return
    
    crud_path.parent.mkdir(exist_ok=True)
    crud_content = Template(_get_crud_template()).substitute(template_vars)
    crud_path.write_text(crud_content)
    
    _show_progress(f"crud/{name.lower()}.py")


def _update_main_py(name: str) -> None:
    """Update main.py to include the new router."""
    main_path = Path("main.py")
    if not main_path.exists():
        return
    
    content = main_path.read_text()
    
    # Check if router is already imported
    if f"from routers import {name.lower()}" in content:
        return
    
    # Add import
    import_line = f"from routers import {name.lower()}"
    if "from routers import" in content:
        # Add to existing import
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("from routers import"):
                lines[i] = line.rstrip() + f", {name.lower()}"
                break
        content = '\n'.join(lines)
    else:
        # Add new import after other imports
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith("from fastapi import"):
                # Insert after FastAPI imports
                lines.insert(i + 1, import_line)
                break
        content = '\n'.join(lines)
    
    # Add router to app
    router_line = f"app.include_router({name.lower()}.router, prefix=\"/{name.lower()}\", tags=[\"{name.lower()}\"])"
    if "app.include_router" in content:
        # Add before the last router
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "app.include_router" in line and i > 0:
                lines.insert(i, router_line)
                break
        content = '\n'.join(lines)
    else:
        # Add after app creation
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "app = FastAPI" in line:
                lines.insert(i + 1, "")
                lines.insert(i + 2, router_line)
                break
        content = '\n'.join(lines)
    
    main_path.write_text(content)
    _show_progress("main.py (updated)")


def _show_progress(filename: str):
    """Show progress for component addition."""
    print(f"  {color('✓', Style.GREEN)} {muted(filename)}")


def _get_router_template() -> str:
    """Get template for router file."""
    return '''"""${model_name} router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from schemas.${model_name_lower} import ${model_name}, ${model_name}Create, ${model_name}Update
from crud.${model_name_lower} import ${model_name_lower}_crud

router = APIRouter()


@router.get("/", response_model=List[${model_name}])
def read_${model_name_plural}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve ${model_name_plural}."""
    ${model_name_plural} = ${model_name_lower}_crud.get_multi(db, skip=skip, limit=limit)
    return ${model_name_plural}


@router.post("/", response_model=${model_name})
def create_${model_name_lower}(
    ${model_name_lower}: ${model_name}Create,
    db: Session = Depends(get_db)
):
    """Create a new ${model_name_lower}."""
    return ${model_name_lower}_crud.create(db=db, obj_in=${model_name_lower})


@router.get("/{${model_name_lower}_id}", response_model=${model_name})
def read_${model_name_lower}(
    ${model_name_lower}_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific ${model_name_lower} by ID."""
    db_${model_name_lower} = ${model_name_lower}_crud.get(db, id=${model_name_lower}_id)
    if db_${model_name_lower} is None:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    return db_${model_name_lower}


@router.put("/{${model_name_lower}_id}", response_model=${model_name})
def update_${model_name_lower}(
    ${model_name_lower}_id: int,
    ${model_name_lower}: ${model_name}Update,
    db: Session = Depends(get_db)
):
    """Update a ${model_name_lower}."""
    db_${model_name_lower} = ${model_name_lower}_crud.get(db, id=${model_name_lower}_id)
    if db_${model_name_lower} is None:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    return ${model_name_lower}_crud.update(db=db, db_obj=db_${model_name_lower}, obj_in=${model_name_lower})


@router.delete("/{${model_name_lower}_id}")
def delete_${model_name_lower}(
    ${model_name_lower}_id: int,
    db: Session = Depends(get_db)
):
    """Delete a ${model_name_lower}."""
    db_${model_name_lower} = ${model_name_lower}_crud.get(db, id=${model_name_lower}_id)
    if db_${model_name_lower} is None:
        raise HTTPException(status_code=404, detail="${model_name} not found")
    ${model_name_lower}_crud.remove(db=db, id=${model_name_lower}_id)
    return {"message": "${model_name} deleted successfully"}
'''


def _get_model_template() -> str:
    """Get template for model file."""
    return '''"""${model_name} model."""

from sqlalchemy import Column, Integer, String
from db.base import Base


class ${model_name}(Base):
    """${model_name} model."""
    __tablename__ = "${model_name_plural}"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # Add more fields as needed
'''


def _get_schema_template() -> str:
    """Get template for schema file."""
    return '''"""${model_name} schemas."""

from typing import Optional
from pydantic import BaseModel


class ${model_name}Base(BaseModel):
    """Base ${model_name} schema."""
    name: str
    # Add more fields as needed


class ${model_name}Create(${model_name}Base):
    """${model_name} creation schema."""
    pass


class ${model_name}Update(${model_name}Base):
    """${model_name} update schema."""
    name: Optional[str] = None
    # Add more fields as needed


class ${model_name}(${model_name}Base):
    """${model_name} response schema."""
    id: int

    class Config:
        from_attributes = True
'''


def _get_crud_template() -> str:
    """Get template for CRUD file."""
    return '''"""${model_name} CRUD operations."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.${model_name_lower} import ${model_name}
from schemas.${model_name_lower} import ${model_name}Create, ${model_name}Update


class CRUD${model_name}(Generic[TypeVar("ModelType", bound=${model_name})]):
    """CRUD operations for ${model_name}."""

    def get(self, db: Session, id: Any) -> Optional[${model_name}]:
        """Get ${model_name_lower} by ID."""
        return db.query(${model_name}).filter(${model_name}.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[${model_name}]:
        """Get multiple ${model_name_plural}."""
        return db.query(${model_name}).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: ${model_name}Create) -> ${model_name}:
        """Create new ${model_name_lower}."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = ${model_name}(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ${model_name},
        obj_in: Union[${model_name}Update, Dict[str, Any]]
    ) -> ${model_name}:
        """Update ${model_name_lower}."""
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ${model_name}:
        """Remove ${model_name_lower}."""
        obj = db.query(${model_name}).get(id)
        db.delete(obj)
        db.commit()
        return obj


# Create a singleton instance
${model_name_lower}_crud = CRUD${model_name}()
'''
