"""Tests for the generate/ package."""

import importlib.util


from fullapi.generate import render, write
from fullapi.spec import Spec, Resource, Field


def make_spec(database="sqlite", auth=False):
    return Spec(
        name="Demo",
        database=database,
        auth=auth,
        resources=[
            Resource(
                name="item",
                fields=[
                    Field("name", "str", required=True),
                    Field("note", "str", required=False),
                    Field("count", "int", required=True),
                ],
            ),
            Resource(name="tag", fields=[Field("label", "str")]),
        ],
    )


def test_render_is_pure_and_deterministic():
    spec = make_spec()
    a = render(spec)
    b = render(spec)
    assert a == b
    # calling render did not mutate the spec's resources
    assert spec.resources[0].fields[0].name == "name"


def test_models_schemas_routers_per_resource():
    files = render(make_spec())
    for res in ("item", "tag"):
        assert f"app/models/{res}.py" in files
        assert f"app/schemas/{res}.py" in files
        assert f"app/routers/{res}.py" in files
        assert f"app/crud/{res}.py" in files
    assert "class Item(Base)" in files["app/models/item.py"]
    assert '__tablename__ = "items"' in files["app/models/item.py"]
    assert '/items' in files["app/routers/item.py"]


def test_optional_field_renders_optional():
    files = render(make_spec())
    schema = files["app/schemas/item.py"]
    assert "note: Optional[str] = None" in schema
    assert "name: str" in schema
    # optional field is nullable in the model
    assert "note = Column(String, nullable=True)" in files["app/models/item.py"]
    assert "name = Column(String, nullable=False)" in files["app/models/item.py"]


def test_database_none_omits_db_files():
    files = render(make_spec(database="none"))
    assert "app/database.py" not in files
    assert "app/config.py" not in files
    assert not any(p.startswith("app/models/") for p in files)
    assert not any(p.startswith("app/crud/") for p in files)
    # schemas and routers still generated
    assert "app/schemas/item.py" in files
    assert "app/routers/item.py" in files


def test_auth_adds_dependency():
    files = render(make_spec(auth=True))
    assert "app/auth.py" in files
    assert "get_current_user" in files["app/routers/item.py"]
    reqs = files["requirements.txt"]
    assert "python-jose" in reqs and "passlib" in reqs


def test_requirements_reflect_database():
    assert "psycopg2-binary" in render(make_spec("postgres"))["requirements.txt"]
    assert "sqlalchemy" in render(make_spec("sqlite"))["requirements.txt"]
    assert "sqlalchemy" not in render(make_spec("none"))["requirements.txt"]


def test_write_produces_files_on_disk(tmp_path):
    paths = write(make_spec(), tmp_path)
    assert paths == sorted(paths)
    assert all(p.exists() for p in paths)
    assert (tmp_path / "app" / "main.py").exists()
    assert (tmp_path / "app" / "models" / "item.py").exists()


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generated_schema_is_importable(tmp_path):
    write(make_spec(), tmp_path)
    schema_path = tmp_path / "app" / "schemas" / "item.py"
    mod = _load_module(schema_path, "gen_item_schema")
    obj = mod.ItemCreate(name="x", count=3)
    assert obj.name == "x"
    assert obj.note is None
    resp = mod.ItemResponse(id=1, name="x", count=3)
    assert resp.id == 1


def test_syntax_valid_for_all_generated_files():
    for database in ("none", "sqlite", "postgres"):
        for auth in (False, True):
            for path, content in render(make_spec(database, auth)).items():
                if path.endswith(".py"):
                    compile(content, path, "exec")
