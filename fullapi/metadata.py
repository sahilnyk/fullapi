"""Project metadata (.fullapi.json) management."""

import json
from pathlib import Path
from datetime import datetime

from fullapi import __version__
from fullapi.config import ProjectConfig


METADATA_FILE = ".fullapi.json"


def generate_metadata(config: ProjectConfig) -> dict:
    """Generate metadata dict from project config."""
    metadata = {
        "version": __version__,
        "created_at": datetime.now().isoformat(),
        "name": config.name,
        "mode": config.mode,
        "database": config.database,
        "auth": config.auth,
        "docker": config.docker,
        "redis": config.redis,
        "middleware": config.middleware,
        "logging": config.logging,
        "template": config.template,
        "terraform": config.terraform,
    }

    if config.terraform:
        metadata["cloud_provider"] = config.cloud_provider
        metadata["region"] = config.region
        metadata["instance_size"] = config.instance_size

    return metadata


def write_metadata(project_path: Path, config: ProjectConfig) -> None:
    """Write .fullapi.json to the project directory."""
    metadata = generate_metadata(config)
    metadata_path = project_path / METADATA_FILE
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")


def read_metadata(project_path: Path = None) -> dict:
    """Read .fullapi.json from a project directory. Returns None if not found."""
    if project_path is None:
        project_path = Path(".")
    metadata_path = project_path / METADATA_FILE
    if not metadata_path.exists():
        return None
    return json.loads(metadata_path.read_text())
