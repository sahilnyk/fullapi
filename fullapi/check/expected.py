"""Derive the expected normalized schema from a spec (pure)."""

from fullapi.types import resolve


def _plural(name: str) -> str:
    return name + "s"


def _schema_name(name: str, suffix: str) -> str:
    """FastAPI names component schemas after the pydantic model class."""
    return name.capitalize() + suffix


def _routes_for(name: str) -> set:
    plural = _plural(name)
    return {
        f"GET /{plural}",
        f"POST /{plural}",
        f"GET /{plural}/{{id}}",
        f"PUT /{plural}/{{id}}",
        f"DELETE /{plural}/{{id}}",
    }


def _fields_for(resource) -> dict:
    return {
        field.name: {"type": resolve(field.type).openapi, "required": field.required}
        for field in resource.fields
    }


def expected_schema(spec) -> dict:
    """Return the normalized schema the live app is expected to expose.

    Normalized shape (shared with actual_schema so diff compares like-for-like):
        {
          "routes": set[str] of "METHOD /path" (path params normalized to {id}),
          "schemas": {schema_name: {field_name: {"type": <openapi>, "required": bool}}},
        }
    """
    has_id = spec.database != "none"
    routes: set = set()
    schemas: dict = {}
    for resource in spec.resources:
        routes |= _routes_for(resource.name)
        create_fields = _fields_for(resource)
        # A DB-backed Response model carries an auto primary key `id`; the
        # Create model does not.
        response_fields = dict(create_fields)
        if has_id:
            response_fields = {
                "id": {"type": {"type": "integer"}, "required": True},
                **response_fields,
            }
        schemas[_schema_name(resource.name, "Response")] = response_fields
        schemas[_schema_name(resource.name, "Create")] = create_fields
    return {"routes": routes, "schemas": schemas}
