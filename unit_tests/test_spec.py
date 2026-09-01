import pytest

from fullapi.spec import SpecError, load_spec


def _load(tmp_path, text: str):
    path = tmp_path / "api.yaml"
    path.write_text(text, encoding="utf-8")
    return load_spec(path)


@pytest.mark.parametrize("name", ["bad-name", "Uppercase", "two words", "con"])
def test_resource_names_must_be_portable_identifiers(tmp_path, name):
    text = f"name: demo\nresources:\n  - name: {name}\n"
    with pytest.raises(SpecError, match="resource name"):
        _load(tmp_path, text)


@pytest.mark.parametrize("name", ["id", "metadata", "registry", "bad-name"])
def test_reserved_or_invalid_field_names_are_rejected(tmp_path, name):
    text = f"name: demo\nresources:\n  - name: item\n    fields:\n      {name}: str\n"
    with pytest.raises(SpecError, match="field name"):
        _load(tmp_path, text)


def test_auth_values_are_validated(tmp_path):
    with pytest.raises(SpecError, match="'auth'"):
        _load(tmp_path, "name: demo\nauth: sometimes\n")

    spec = _load(tmp_path, "name: demo\nauth: jwt\n")
    assert spec.auth is True


def test_resource_auth_must_be_boolean(tmp_path):
    text = "name: demo\nresources:\n  - name: item\n    auth: jwt\n"
    with pytest.raises(SpecError, match="must be true or false"):
        _load(tmp_path, text)
