import os
import subprocess
import sys
from pathlib import Path

import pytest

SPEC = """\
name: shop_api
database: sqlite
resources:
  - name: product
    fields:
      title: str
      price: float
      note: str?
"""

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(args, cwd, extra_env=None):
    env = {"PYTHONPATH": str(REPO_ROOT), "NO_COLOR": "1", "PATH": ""}
    env["PATH"] = os.environ.get("PATH", "")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-m", "fullapi", *args],
        cwd=cwd, env=env, capture_output=True, text=True, check=False,
    )


def test_cli_init_writes_starter_spec(tmp_path):
    result = _run(["init"], cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "api.yaml").exists()
    assert "name:" in (tmp_path / "api.yaml").read_text()

    again = _run(["init"], cwd=tmp_path)
    assert again.returncode != 0
    assert "already exists" in (again.stdout + again.stderr)


def test_cli_gen_writes_files(tmp_path):
    (tmp_path / "api.yaml").write_text(SPEC)
    result = _run(["gen"], cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "app/main.py").exists()
    assert (tmp_path / "app/routers/product.py").exists()
    assert "done" in result.stdout
    assert "files written" in result.stdout


def test_cli_version_flag():
    result = _run(["--version"], cwd=REPO_ROOT)
    assert result.returncode == 0
    assert "fullapi" in result.stdout


def test_cli_help_lists_both_commands():
    result = _run(["--help"], cwd=REPO_ROOT)
    assert result.returncode == 0
    assert "gen" in result.stdout and "check" in result.stdout


def test_cli_without_command_shows_help():
    result = _run([], cwd=REPO_ROOT)
    assert result.returncode == 0
    assert "fullapi init" in result.stdout
    assert "command-specific help" in result.stdout


def test_cli_gen_keeps_file_list_behind_verbose_flag(tmp_path):
    (tmp_path / "api.yaml").write_text(SPEC)

    normal = _run(["gen"], cwd=tmp_path)
    assert normal.returncode == 0
    assert "app/main.py" not in normal.stdout
    assert "uvicorn app.main:app --reload" in normal.stdout

    verbose = _run(["gen", "--verbose"], cwd=tmp_path)
    assert verbose.returncode == 0
    assert "main.py" in verbose.stdout


def test_cli_missing_spec_errors(tmp_path):
    result = _run(["gen"], cwd=tmp_path)
    assert result.returncode != 0
    assert "spec error" in (result.stdout + result.stderr)


def test_cli_check_detects_breaking_drift(tmp_path):
    pytest.importorskip("fastapi")
    pytest.importorskip("sqlalchemy")
    pytest.importorskip("pydantic_settings")

    (tmp_path / "api.yaml").write_text(SPEC)
    gen = _run(["gen"], cwd=tmp_path)
    assert gen.returncode == 0

    ok = _run(["check"], cwd=tmp_path)
    assert ok.returncode == 0, ok.stdout + ok.stderr

    (tmp_path / "api.yaml").write_text(SPEC.replace("price: float", "price: str"))
    drift = _run(["check"], cwd=tmp_path)
    assert drift.returncode != 0
    assert "breaking" in (drift.stdout + drift.stderr).lower()


def test_cli_check_supports_app_directory(tmp_path):
    spec_path = tmp_path / "api.yaml"
    project = tmp_path / "generated"
    spec_path.write_text(SPEC)
    gen = _run(["gen", str(spec_path), "--out", str(project)], cwd=tmp_path)
    assert gen.returncode == 0, gen.stdout + gen.stderr

    checked = _run(
        ["check", str(spec_path), "--app-dir", str(project)],
        cwd=tmp_path,
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
