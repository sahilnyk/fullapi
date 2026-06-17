"""Docker build and push operations."""

import subprocess
import json
from pathlib import Path

from fullapi.colors import color, Style


def _run_command(command: list) -> tuple:
    """Run command and return (exit_code, stdout)."""
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True
        )
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        print(f"{color('[ERROR]', Style.RED)} Command not found: {command[0]}")
        return 1, ""
    except Exception as e:
        print(f"{color('[ERROR]', Style.RED)} {str(e)}")
        return 1, ""


def _get_git_commit() -> str:
    """Get current git commit SHA (short)."""
    exit_code, stdout = _run_command(["git", "rev-parse", "--short", "HEAD"])
    if exit_code == 0 and stdout:
        return stdout
    return "latest"


def _get_project_metadata() -> dict:
    """Read project metadata from .fullapi.json."""
    metadata_path = Path.cwd() / ".fullapi.json"
    if not metadata_path.exists():
        return {}

    try:
        return json.loads(metadata_path.read_text())
    except Exception:
        return {}


def _get_registry_url(project_name: str) -> str:
    """Get registry URL (generic)."""
    return project_name


def docker_build():
    """Build Docker image."""
    dockerfile = Path.cwd() / "Dockerfile"

    if not dockerfile.exists():
        print(f"{color('[ERROR]', Style.RED)} No Dockerfile found")
        print("Enable Docker when creating project: fullapi new myapi --docker")
        return 1

    metadata = _get_project_metadata()
    project_name = metadata.get('name', Path.cwd().name)
    commit = _get_git_commit()

    image_tag = f"{project_name}:{commit}"

    print(f"{color('[INFO]', Style.CYAN)} Building Docker image...")
    print(f"  Image: {image_tag}")
    print()

    exit_code, _ = _run_command([
        "docker", "build",
        "-t", image_tag,
        "-t", f"{project_name}:latest",
        "."
    ])

    if exit_code == 0:
        print()
        print(f"{color('[OK]', Style.GREEN)} Image built: {image_tag}")
        print()
        print("Next steps:")
        print("  fullapi docker push")
    else:
        print(f"{color('[ERROR]', Style.RED)} Build failed")

    return exit_code


def docker_push():
    """Push Docker image to registry."""
    metadata = _get_project_metadata()

    if not metadata:
        print(f"{color('[ERROR]', Style.RED)} No .fullapi.json found")
        return 1

    project_name = metadata.get('name', Path.cwd().name)

    commit = _get_git_commit()
    local_tag = f"{project_name}:{commit}"
    registry_url = _get_registry_url(project_name)
    remote_tag = f"{registry_url}:{commit}"

    print(f"{color('[INFO]', Style.CYAN)} Pushing to registry...")
    print(f"  Local:  {local_tag}")
    print(f"  Remote: {remote_tag}")
    print()

    # Check if local image exists
    exit_code, _ = _run_command(["docker", "image", "inspect", local_tag])
    if exit_code != 0:
        print(f"{color('[ERROR]', Style.RED)} Image not found: {local_tag}")
        print("Build it first: fullapi docker build")
        return 1

    # Tag for remote
    print(f"{color('[INFO]', Style.CYAN)} Tagging image...")
    exit_code, _ = _run_command(["docker", "tag", local_tag, remote_tag])
    if exit_code != 0:
        print(f"{color('[ERROR]', Style.RED)} Tagging failed")
        return exit_code

    # Push
    print(f"{color('[INFO]', Style.CYAN)} Pushing image...")
    exit_code, _ = _run_command(["docker", "push", remote_tag])

    if exit_code == 0:
        print()
        print(f"{color('[OK]', Style.GREEN)} Image pushed: {remote_tag}")
    else:
        print(f"{color('[ERROR]', Style.RED)} Push failed")

    return exit_code
