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
    text = env_path.read_text(encoding="utf-8")
    marker = "target_metadata = None"
    if marker not in text:
        raise MigrateError(f"could not configure {env_path}: target_metadata marker not found")
    text = text.replace(
        marker,
        "import app.main  # register generated models on Base.metadata\n"
        "from app.database import Base\n"
        "from app.config import settings\n"
        "target_metadata = Base.metadata\n"
        "config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)",
    )
    env_path.write_text(text, encoding="utf-8")


def run_migrate(app_dir: Path, message: str) -> str:
    """Autogenerate an Alembic revision for the project in app_dir."""
    if not app_dir.is_dir():
        raise MigrateError(f"app directory not found: {app_dir}")
    for required in ("app/main.py", "app/database.py", "app/config.py"):
        if not (app_dir / required).is_file():
            raise MigrateError(f"not a generated database app: missing {required}")
    if not message.strip():
        raise MigrateError("migration message cannot be empty")

    migrations_dir = app_dir / "migrations"
    if not migrations_dir.exists():
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "init", "migrations"],
            cwd=app_dir, capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            raise MigrateError(_command_error(result))
        _patch_env(migrations_dir)

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
        cwd=app_dir, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise MigrateError(_command_error(result))
    return result.stdout or result.stderr


def _command_error(result: subprocess.CompletedProcess[str]) -> str:
    detail = (result.stderr or result.stdout or "Alembic command failed").strip()
    if "No module named alembic" in detail:
        return "Alembic is not installed; run: pip install -r requirements.txt"
    return detail
