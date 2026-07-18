import subprocess
import sys
from pathlib import Path

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
    import os
    env["PATH"] = os.environ.get("PATH", "")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-m", "fullapi", *args],
        cwd=cwd, env=env, capture_output=True, text=True,
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


def test_cli_missing_spec_errors(tmp_path):
    result = _run(["gen"], cwd=tmp_path)
    assert result.returncode != 0
    assert "spec error" in (result.stdout + result.stderr)


def test_cli_check_detects_breaking_drift(tmp_path):
    import pytest
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
