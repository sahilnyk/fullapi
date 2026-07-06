"""Shared field-type map — the single source of truth for type mapping.

Both `generate` (spec -> code) and `check` (spec -> expected OpenAPI) consume
this table so generation and enforcement can never disagree.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TypeInfo:
    """How one spec field type maps across the stack."""
    python: str        # Python / Pydantic annotation, e.g. "str"
    sqlalchemy: str    # SQLAlchemy column type, e.g. "String"
    openapi: dict      # OpenAPI schema fragment, e.g. {"type": "string"}


# Spec field type -> mapping. Extend here to add a new supported type (Open/Closed).
TYPE_MAP = {
    "str": TypeInfo("str", "String", {"type": "string"}),
    "int": TypeInfo("int", "Integer", {"type": "integer"}),
    "float": TypeInfo("float", "Float", {"type": "number"}),
    "bool": TypeInfo("bool", "Boolean", {"type": "boolean"}),
}

SUPPORTED_TYPES = tuple(TYPE_MAP)


def resolve(field_type: str) -> TypeInfo:
    """Return the TypeInfo for a spec field type, or raise ValueError."""
    try:
        return TYPE_MAP[field_type]
    except KeyError:
        raise ValueError(
            f"unsupported field type {field_type!r}; "
            f"supported: {', '.join(SUPPORTED_TYPES)}"
        )
