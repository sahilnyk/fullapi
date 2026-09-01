"""Autogenerate an Alembic migration for a generated app.

Alembic's own --autogenerate already diffs SQLAlchemy models against the
live database. This module just wires a generated project up to it.
"""

import subprocess
import sys
from pathlib import Path


class MigrateError(Exception):
    pass


def _patch_env(migrations_dir: Path) -> None:
    # alembic init leaves target_metadata unset and the DB url as a
    # placeholder. Point both at the generated app's own Base and settings
    # so migrations stay in sync with app.yaml without manual editing.
    env_path = migrations_dir / "env.py"
    text = env_path.read_text()
    text = text.replace(
        "target_metadata = None",
        "from app.database import Base\n"
        "from app.config import settings\n"
        "target_metadata = Base.metadata\n"
        "config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)",
    )
    env_path.write_text(text)


def run_migrate(app_dir: Path, message: str) -> str:
    """Autogenerate an Alembic revision for the project in app_dir."""
    migrations_dir = app_dir / "migrations"
    if not migrations_dir.exists():
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "init", "migrations"],
            cwd=app_dir, capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise MigrateError(result.stderr)
        _patch_env(migrations_dir)

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
        cwd=app_dir, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise MigrateError(result.stderr)
    return result.stdout
