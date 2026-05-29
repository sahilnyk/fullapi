"""Docker configuration file parsing."""

import re
from pathlib import Path
from typing import Dict, Optional


def parse_dockerfile(dockerfile_path: Path) -> Optional[Dict]:
    """Parse Dockerfile and extract relevant configuration.

    Returns dict with:
        - port: int or None
        - env_vars: Dict[str, str]
        - base_image: str
    """
    if not dockerfile_path.exists():
        return None

    content = dockerfile_path.read_text()
    result = {
        "port": None,
        "env_vars": {},
        "base_image": None
    }

    for line in content.split('\n'):
        line = line.strip()

        # Parse EXPOSE directive
        if line.startswith('EXPOSE'):
            port_match = re.search(r'EXPOSE\s+(\d+)', line)
            if port_match:
                result["port"] = int(port_match.group(1))

        # Parse ENV directives
        elif line.startswith('ENV'):
            env_match = re.search(r'ENV\s+(\w+)=(.+)', line)
            if env_match:
                key, value = env_match.groups()
                result["env_vars"][key] = value.strip('"').strip("'")

        # Parse FROM directive
        elif line.startswith('FROM'):
            from_match = re.search(r'FROM\s+([\w:.\-/]+)', line)
            if from_match:
                result["base_image"] = from_match.group(1)

    return result


def parse_docker_compose(compose_path: Path) -> Optional[Dict]:
    """Parse docker-compose.yml and extract relevant configuration.

    Returns dict with:
        - services: Dict[str, Dict] - service name to config
        - postgres: Dict or None - postgres config if found
        - redis: Dict or None - redis config if found
        - ports: List[int] - exposed ports
    """
    if not compose_path.exists():
        return None

    try:
        import yaml
    except ImportError:
        # If PyYAML not available, return None
        return None

    try:
        content = yaml.safe_load(compose_path.read_text())
    except Exception:
        return None

    if not content or "services" not in content:
        return None

    services = content["services"]
    result = {
        "services": services,
        "postgres": None,
        "redis": None,
        "ports": []
    }

    # Detect postgres service
    for name, config in services.items():
        if not isinstance(config, dict):
            continue

        image = config.get("image", "")

        if "postgres" in image:
            result["postgres"] = {
                "name": name,
                "image": image,
                "version": _extract_version(image)
            }

        if "redis" in image:
            result["redis"] = {
                "name": name,
                "image": image
            }

        # Extract ports
        if "ports" in config:
            for port_mapping in config["ports"]:
                if isinstance(port_mapping, str):
                    # Format: "8000:8000" or "8000"
                    host_port = port_mapping.split(':')[0]
                    if host_port.isdigit():
                        result["ports"].append(int(host_port))

    return result


def _extract_version(image: str) -> str:
    """Extract version from Docker image string.

    Examples:
        postgres:15 -> 15
        postgres:15.2-alpine -> 15.2
        postgres -> latest
    """
    if ':' not in image:
        return "latest"

    version = image.split(':')[1]
    # Remove -alpine, -slim, etc suffixes
    version = version.split('-')[0]
    return version
