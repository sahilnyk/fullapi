"""Introspect a live FastAPI app and normalize it into the comparable shape."""

import importlib
import os
import re
import sys

from fullapi.check.model import CheckError

_PATH_PARAM = re.compile(r"\{[^}]+\}")


def _load_app(app_import_path: str):
    """Import ``module:attr`` and return the app object."""
    if ":" not in app_import_path:
        raise CheckError(
            f"invalid app path {app_import_path!r}; expected 'module.path:attr'"
        )
    module_path, attr = app_import_path.split(":", 1)

    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        raise CheckError(f"could not import {module_path!r}: {exc}") from exc

    try:
        return getattr(module, attr)
    except AttributeError as exc:
        raise CheckError(
            f"module {module_path!r} has no attribute {attr!r}"
        ) from exc


def normalize_openapi(openapi: dict) -> dict:
    """Reduce a real OpenAPI document to the shared normalized shape."""
    routes = set()
    for path, methods in (openapi.get("paths") or {}).items():
        norm_path = _normalize_path(path)
        for method in methods:
            routes.add(f"{method.upper()} {norm_path}")

    schemas = {}
    components = (openapi.get("components") or {}).get("schemas") or {}
    for name, schema in components.items():
        required = set(schema.get("required") or [])
        props = schema.get("properties") or {}
        fields = {}
        for field_name, prop in props.items():
            typ, optional = _field_type(prop)
            fields[field_name] = {
                "type": typ,
                # An anyOf-with-null field is optional regardless of the
                # `required` list (Pydantic v2 / FastAPI representation).
                "required": field_name in required and not optional,
            }
        schemas[name] = fields
    return {"routes": routes, "schemas": schemas}


def _normalize_path(path: str) -> str:
    """Collapse path params to {id} and strip a trailing slash (except root)."""
    path = _PATH_PARAM.sub("{id}", path)
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return path


def _field_type(prop: dict) -> tuple:
    """Return (normalized-type, is_optional).

    Unwraps ``anyOf: [X, {type: null}]`` into X's type and flags the field
    optional. Falls back to the plain ``type`` key otherwise.
    """
    any_of = prop.get("anyOf")
    if any_of:
        non_null = [s for s in any_of if s.get("type") != "null"]
        has_null = any(s.get("type") == "null" for s in any_of)
        if len(non_null) == 1 and "type" in non_null[0]:
            return {"type": non_null[0]["type"]}, has_null
    if "type" in prop:
        return {"type": prop["type"]}, False
    return {}, False


def actual_schema(app_import_path: str) -> dict:
    """Import the app object and return its normalized OpenAPI schema."""
    app = _load_app(app_import_path)
    try:
        openapi = app.openapi()
    except Exception as exc:
        raise CheckError(f"failed to call {app_import_path}.openapi(): {exc}") from exc
    return normalize_openapi(openapi)
