"""Codebase analysis for deployment."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
from fullapi.analyzers.docker_parser import parse_dockerfile, parse_docker_compose

DEFAULT_PORT = 8000


@dataclass
class CodebaseAnalysis:
    """Analysis results from scanning a codebase."""
    database: Optional[Dict]  # {"type": "postgresql", "version": "15"}
    redis: bool
    port: int
    health_check_path: str
    env_vars: Dict[str, str]  # All env vars
    secrets: List[str]  # Vars classified as secrets
    dependencies: List[str]  # From requirements.txt
    has_custom_dockerfile: bool
    dockerfile_path: Optional[str]
    has_docker_compose: bool
    compose_path: Optional[str]


class CodebaseAnalyzer:
    """Analyzes a codebase to extract deployment requirements."""

    def __init__(self, project_path: Path):
        """Initialize analyzer with project path."""
        self.project_path = project_path

    def analyze(self) -> CodebaseAnalysis:
        """Analyze the codebase and return requirements."""
        # Parse Docker files
        dockerfile_path = self.project_path / "Dockerfile"
        compose_path = self.project_path / "docker-compose.yml"

        dockerfile_data = parse_dockerfile(dockerfile_path)
        compose_data = parse_docker_compose(compose_path)

        # Detect database
        database = self._detect_database(compose_data)

        # Detect Redis
        redis = self._detect_redis(compose_data)

        # Detect port
        port = self._detect_port(compose_data, dockerfile_data)

        # Detect health check
        health_check_path = self._detect_health_check()

        # Parse environment variables
        env_vars = self._parse_env_vars(dockerfile_data)

        # Classify secrets
        secrets = self._classify_secrets(env_vars)

        # Read dependencies
        dependencies = self._read_dependencies()

        return CodebaseAnalysis(
            database=database,
            redis=redis,
            port=port,
            health_check_path=health_check_path,
            env_vars=env_vars,
            secrets=secrets,
            dependencies=dependencies,
            has_custom_dockerfile=dockerfile_data is not None,
            dockerfile_path=str(dockerfile_path) if dockerfile_data else None,
            has_docker_compose=compose_data is not None,
            compose_path=str(compose_path) if compose_data else None
        )

    def _detect_database(self, compose_data: Optional[Dict]) -> Optional[Dict]:
        """Detect database from docker-compose or requirements.txt."""
        # Check docker-compose first
        if compose_data and compose_data.get("postgres"):
            postgres_info = compose_data["postgres"]
            return {
                "type": "postgresql",
                "version": postgres_info.get("version", "latest")
            }

        # Check requirements.txt for database dependencies
        requirements = self._read_dependencies()
        has_sqlalchemy = any("sqlalchemy" in dep.lower() for dep in requirements)

        if has_sqlalchemy:
            # Check for postgres driver
            if any("psycopg2" in dep.lower() for dep in requirements):
                # Check if models directory exists
                models_path = self.project_path / "models"
                if models_path.exists():
                    return {"type": "postgresql", "version": "latest"}

        return None

    def _detect_redis(self, compose_data: Optional[Dict]) -> bool:
        """Detect Redis from docker-compose or requirements.txt."""
        # Check docker-compose first
        if compose_data and compose_data.get("redis"):
            return True

        # Check requirements.txt
        requirements = self._read_dependencies()
        return any("redis" in dep.lower() for dep in requirements)

    def _detect_port(self, compose_data: Optional[Dict], dockerfile_data: Optional[Dict]) -> int:
        """Detect port with priority: docker-compose > Dockerfile > main.py > default 8000."""
        # Priority 1: docker-compose
        if compose_data and compose_data.get("ports"):
            return compose_data["ports"][0]

        # Priority 2: Dockerfile
        if dockerfile_data and dockerfile_data.get("port"):
            return dockerfile_data["port"]

        # Priority 3: main.py
        main_py_path = self.project_path / "main.py"
        if main_py_path.exists():
            content = main_py_path.read_text()
            # Look for uvicorn.run(..., port=...)
            port_match = re.search(r'port\s*=\s*(\d+)', content)
            if port_match:
                return int(port_match.group(1))

        # Default: DEFAULT_PORT
        return DEFAULT_PORT

    def _detect_health_check(self) -> str:
        """Detect health check endpoint from code."""
        # Common health check patterns
        for filename in ["main.py", "routers/health.py"]:
            filepath = self.project_path / filename
            if filepath.exists():
                content = filepath.read_text()
                # Look for common health check patterns
                if "/health" in content:
                    return "/health"
                if "/healthz" in content:
                    return "/healthz"

        # Default
        return "/health"

    def _parse_env_vars(self, dockerfile_data: Optional[Dict]) -> Dict[str, str]:
        """Parse environment variables from .env.example, .env, and Dockerfile."""
        env_vars = {}

        # Parse .env.example
        env_example_path = self.project_path / ".env.example"
        if env_example_path.exists():
            env_vars.update(self._parse_env_file(env_example_path))

        # Parse .env
        env_path = self.project_path / ".env"
        if env_path.exists():
            env_vars.update(self._parse_env_file(env_path))

        # Parse Dockerfile ENV directives
        if dockerfile_data and dockerfile_data.get("env_vars"):
            env_vars.update(dockerfile_data["env_vars"])

        return env_vars

    def _parse_env_file(self, filepath: Path) -> Dict[str, str]:
        """Parse environment variables from a .env file."""
        env_vars = {}
        content = filepath.read_text()

        for line in content.split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

        return env_vars

    def _classify_secrets(self, env_vars: Dict[str, str]) -> List[str]:
        """Classify environment variables as secrets based on keywords."""
        secret_keywords = ["key", "secret", "password", "token", "credential"]
        secrets = []

        for key in env_vars.keys():
            key_lower = key.lower()
            if any(keyword in key_lower for keyword in secret_keywords):
                secrets.append(key)

        return secrets

    def _read_dependencies(self) -> List[str]:
        """Read dependencies from requirements.txt."""
        requirements_path = self.project_path / "requirements.txt"
        if not requirements_path.exists():
            return []

        content = requirements_path.read_text()
        dependencies = []

        for line in content.split('\n'):
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                dependencies.append(line)

        return dependencies
