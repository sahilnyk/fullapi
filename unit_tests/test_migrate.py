from fullapi.migrate import _patch_env


def test_patch_env_wires_target_metadata(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    env_path = migrations_dir / "env.py"
    env_path.write_text("target_metadata = None\n")

    _patch_env(migrations_dir)

    text = env_path.read_text()
    assert "from app.database import Base" in text
    assert "target_metadata = Base.metadata" in text
    assert "settings.DATABASE_URL" in text
