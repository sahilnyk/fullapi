import pytest

from fullapi.migrate import MigrateError, _patch_env, run_migrate


def test_patch_env_wires_target_metadata(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    env_path = migrations_dir / "env.py"
    env_path.write_text("target_metadata = None\n")

    _patch_env(migrations_dir)

    text = env_path.read_text()
    assert "import app.main" in text
    assert "from app.database import Base" in text
    assert "target_metadata = Base.metadata" in text
    assert "settings.DATABASE_URL" in text


def test_patch_env_rejects_unknown_template(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "env.py").write_text("unexpected template\n")

    with pytest.raises(MigrateError, match="marker not found"):
        _patch_env(migrations_dir)


def test_migrate_rejects_missing_or_non_database_app(tmp_path):
    with pytest.raises(MigrateError, match="app directory not found"):
        run_migrate(tmp_path / "missing", "create tables")

    with pytest.raises(MigrateError, match=r"missing app/main\.py"):
        run_migrate(tmp_path, "create tables")
