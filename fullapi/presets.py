"""Preset configurations for common project setups."""

import json
from pathlib import Path

from fullapi.config import ProjectConfig


BUILTIN_PRESETS = {
    "production": {
        "description": "Full production setup with all features",
        "mode": "full",
        "database": "postgresql",
        "auth": True,
        "docker": True,
        "redis": True,
        "middleware": True,
        "logging": True,
    },
    "minimal": {
        "description": "Bare minimum API",
        "mode": "basic",
        "database": "none",
        "auth": False,
        "docker": False,
        "redis": False,
        "middleware": False,
        "logging": False,
    },
    "docker-ready": {
        "description": "Full mode with Docker and PostgreSQL",
        "mode": "full",
        "database": "postgresql",
        "auth": False,
        "docker": True,
        "redis": False,
        "middleware": False,
        "logging": True,
    },
    "microservice": {
        "description": "Lightweight service with logging and middleware",
        "mode": "full",
        "database": "sqlite",
        "auth": False,
        "docker": True,
        "redis": False,
        "middleware": True,
        "logging": True,
    },
}

USER_PRESETS_PATH = Path.home() / ".fullapi" / "presets.json"


def load_user_presets() -> dict:
    """Load user-defined presets from ~/.fullapi/presets.json."""
    if not USER_PRESETS_PATH.exists():
        return {}
    try:
        return json.loads(USER_PRESETS_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def get_all_presets() -> dict:
    """Get all presets (built-in + user-defined). User presets override built-in."""
    presets = dict(BUILTIN_PRESETS)
    presets.update(load_user_presets())
    return presets


def get_preset(name: str) -> dict:
    """Get a preset by name. Returns None if not found."""
    presets = get_all_presets()
    return presets.get(name)


def apply_preset(project_name: str, preset: dict) -> ProjectConfig:
    """Create a ProjectConfig from a preset dict."""
    return ProjectConfig(
        name=project_name,
        mode=preset.get("mode", "full"),
        database=preset.get("database", "none"),
        auth=preset.get("auth", False),
        docker=preset.get("docker", False),
        redis=preset.get("redis", False),
        middleware=preset.get("middleware", False),
        logging=preset.get("logging", False),
        template=preset.get("template", None),
    )


def save_user_preset(name: str, config: ProjectConfig) -> None:
    """Save current config as a user preset."""
    USER_PRESETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    presets = load_user_presets()
    presets[name] = {
        "description": f"Custom preset '{name}'",
        "mode": config.mode,
        "database": config.database,
        "auth": config.auth,
        "docker": config.docker,
        "redis": config.redis,
        "middleware": config.middleware,
        "logging": config.logging,
    }
    USER_PRESETS_PATH.write_text(json.dumps(presets, indent=2) + "\n")


def list_presets() -> dict:
    """Return all available presets with descriptions."""
    return get_all_presets()
