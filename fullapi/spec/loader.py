"""Load and validate api.yaml into a Spec."""

from pathlib import Path

import yaml

from fullapi.spec.model import Spec, Resource, Field
from fullapi.types import SUPPORTED_TYPES

DATABASES = ("none", "sqlite", "postgres")


class SpecError(ValueError):
    """Raised when api.yaml is missing or invalid."""


def load_spec(path: Path) -> Spec:
    """Read, parse, and validate api.yaml. Raises SpecError on any problem."""
    if not path.exists():
        raise SpecError(f"spec file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise SpecError(f"invalid YAML: {exc}")

    if not isinstance(raw, dict):
        raise SpecError("spec must be a mapping at the top level")

    return _build_spec(raw)


def _build_spec(raw: dict) -> Spec:
    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        raise SpecError("'name' is required and must be a non-empty string")

    database = raw.get("database", "none")
    if database not in DATABASES:
        raise SpecError(
            f"'database' must be one of {DATABASES}, got {database!r}"
        )

    auth = bool(raw.get("auth"))

    raw_resources = raw.get("resources", [])
    if not isinstance(raw_resources, list):
        raise SpecError("'resources' must be a list")

    seen = set()
    resources = []
    for item in raw_resources:
        resource = _build_resource(item)
        if resource.name in seen:
            raise SpecError(f"duplicate resource name: {resource.name!r}")
        seen.add(resource.name)
        resources.append(resource)

    return Spec(name=name.strip(), database=database, auth=auth, resources=resources)


def _build_resource(item: dict) -> Resource:
    if not isinstance(item, dict):
        raise SpecError("each resource must be a mapping")

    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise SpecError("resource 'name' is required and must be a non-empty string")

    raw_fields = item.get("fields", {})
    if not isinstance(raw_fields, dict):
        raise SpecError(f"resource {name!r}: 'fields' must be a mapping")

    fields = [_build_field(name, fname, ftype) for fname, ftype in raw_fields.items()]

    return Resource(name=name.strip(), fields=fields, auth=bool(item.get("auth")))


def _build_field(resource_name: str, fname: str, ftype) -> Field:
    required = True
    # Support "type?" suffix or explicit mapping for optional fields.
    if isinstance(ftype, str) and ftype.endswith("?"):
        ftype, required = ftype[:-1], False

    if ftype not in SUPPORTED_TYPES:
        raise SpecError(
            f"resource {resource_name!r} field {fname!r}: "
            f"unsupported type {ftype!r}; supported: {', '.join(SUPPORTED_TYPES)}"
        )

    return Field(name=fname, type=ftype, required=required)
