"""Tests for the check package: expected_schema derivation and diff logic."""

import pytest

from fullapi.spec import Spec, Resource, Field
from fullapi.check import expected_schema, diff, CheckError


def make_spec():
    return Spec(
        name="demo",
        database="sqlite",
        auth=False,
        resources=[
            Resource(
                name="user",
                fields=[
                    Field("id", "int"),
                    Field("email", "str"),
                    Field("age", "int", required=False),
                ],
            )
        ],
    )


def kinds(changes):
    return {c.kind for c in changes}


def test_expected_schema_shape():
    exp = expected_schema(make_spec())
    assert exp["routes"] == {
        "GET /users",
        "POST /users",
        "GET /users/{id}",
        "PUT /users/{id}",
        "DELETE /users/{id}",
    }
    assert set(exp["schemas"]) == {"UserResponse", "UserCreate"}
    resp = exp["schemas"]["UserResponse"]
    assert resp["email"] == {"type": {"type": "string"}, "required": True}
    assert resp["age"]["required"] is False


def test_identical_has_no_changes():
    exp = expected_schema(make_spec())
    assert diff(exp, exp) == []


def test_field_removed_is_breaking():
    exp = expected_schema(make_spec())
    actual = expected_schema(make_spec())
    del actual["schemas"]["UserResponse"]["email"]
    changes = diff(exp, actual)
    assert "field_removed" in kinds(changes)
    removed = [c for c in changes if c.kind == "field_removed"]
    assert all(c.severity == "breaking" for c in removed)


def test_field_type_changed_is_breaking():
    exp = expected_schema(make_spec())
    actual = expected_schema(make_spec())
    actual["schemas"]["UserResponse"]["age"]["type"] = {"type": "string"}
    changes = diff(exp, actual)
    changed = [c for c in changes if c.kind == "field_type_changed"]
    assert changed and changed[0].severity == "breaking"


def test_added_optional_field_is_safe():
    exp = expected_schema(make_spec())
    actual = expected_schema(make_spec())
    actual["schemas"]["UserResponse"]["nickname"] = {
        "type": {"type": "string"}, "required": False
    }
    changes = diff(exp, actual)
    added = [c for c in changes if c.kind == "field_added"]
    assert added and added[0].severity == "safe"


def test_route_removed_is_breaking():
    exp = expected_schema(make_spec())
    actual = expected_schema(make_spec())
    actual["routes"].discard("DELETE /users/{id}")
    changes = diff(exp, actual)
    removed = [c for c in changes if c.kind == "route_removed"]
    assert removed and removed[0].severity == "breaking"


def test_route_added_is_safe():
    exp = expected_schema(make_spec())
    actual = expected_schema(make_spec())
    actual["routes"].add("GET /health")
    changes = diff(exp, actual)
    added = [c for c in changes if c.kind == "route_added"]
    assert added and added[0].severity == "safe"


def test_required_tightened_is_breaking():
    exp = expected_schema(make_spec())
    actual = expected_schema(make_spec())
    actual["schemas"]["UserResponse"]["age"]["required"] = True
    changes = diff(exp, actual)
    tightened = [c for c in changes if c.kind == "field_required_tightened"]
    assert tightened and tightened[0].severity == "breaking"


def test_actual_schema_with_live_app(tmp_path, monkeypatch):
    pytest.importorskip("fastapi")
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()

    class UserResponse(BaseModel):
        id: int
        email: str

    @app.get("/users", response_model=list[UserResponse])
    def list_users():
        return []

    module = "_check_live_app"
    import sys
    import types as _t
    mod = _t.ModuleType(module)
    mod.app = app
    sys.modules[module] = mod
    try:
        from fullapi.check import actual_schema
        result = actual_schema(f"{module}:app")
        assert "GET /users" in result["routes"]
        assert "UserResponse" in result["schemas"]
    finally:
        del sys.modules[module]


def test_realistic_openapi_matches_spec():
    """A generated app that matches its spec must yield 0 breaking changes.

    Covers trailing-slash collection routes, {item_id} path params, anyOf-null
    optional fields, and the auto `id` primary key on the Response model.
    """
    from fullapi.check.actual import normalize_openapi

    spec = Spec(
        name="shop",
        database="sqlite",
        auth=False,
        resources=[
            Resource(
                name="product",
                fields=[
                    Field("title", "str"),
                    Field("price", "float"),
                    Field("note", "str", required=False),
                ],
            )
        ],
    )

    str_or_null = {"anyOf": [{"type": "string"}, {"type": "null"}], "title": "Note"}
    openapi = {
        "paths": {
            "/products/": {"get": {}, "post": {}},
            "/products/{item_id}": {"get": {}, "put": {}, "delete": {}},
            "/health": {"get": {}},
        },
        "components": {
            "schemas": {
                "ProductResponse": {
                    "properties": {
                        "id": {"type": "integer", "title": "Id"},
                        "title": {"type": "string", "title": "Title"},
                        "price": {"type": "number", "title": "Price"},
                        "note": str_or_null,
                    },
                    "required": ["id", "title", "price"],
                },
                "ProductCreate": {
                    "properties": {
                        "title": {"type": "string", "title": "Title"},
                        "price": {"type": "number", "title": "Price"},
                        "note": str_or_null,
                    },
                    "required": ["title", "price"],
                },
            }
        },
    }

    exp = expected_schema(spec)
    actual = normalize_openapi(openapi)
    changes = diff(exp, actual)
    breaking = [c for c in changes if c.severity == "breaking"]
    assert breaking == [], breaking
    # /health is an extra route -> safe addition, not breaking.
    assert kinds(changes) == {"route_added"}


def test_expected_schema_no_id_when_no_database():
    spec = Spec(
        name="demo", database="none", auth=False,
        resources=[Resource(name="thing", fields=[Field("label", "str")])],
    )
    exp = expected_schema(spec)
    assert "id" not in exp["schemas"]["ThingResponse"]


def test_actual_schema_bad_path_raises():
    from fullapi.check import actual_schema
    with pytest.raises(CheckError):
        actual_schema("no_such_module_xyz:app")
    with pytest.raises(CheckError):
        actual_schema("missing_colon")
