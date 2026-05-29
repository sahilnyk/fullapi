"""Tests for Docker file parsing."""

from pathlib import Path
from fullapi.analyzers.docker_parser import parse_dockerfile


def test_parse_dockerfile_port(tmp_path):
    """Test parsing EXPOSE directive from Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("""
FROM python:3.11-slim
WORKDIR /app
EXPOSE 8080
CMD ["uvicorn", "main:app"]
""")

    result = parse_dockerfile(dockerfile)
    assert result["port"] == 8080


def test_parse_dockerfile_env_vars(tmp_path):
    """Test parsing ENV directives from Dockerfile."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("""
FROM python:3.11-slim
ENV DEBUG=false
ENV SECRET_KEY=default
CMD ["python", "app.py"]
""")

    result = parse_dockerfile(dockerfile)
    assert result["env_vars"] == {"DEBUG": "false", "SECRET_KEY": "default"}


def test_parse_dockerfile_missing():
    """Test parsing non-existent Dockerfile."""
    result = parse_dockerfile(Path("/nonexistent/Dockerfile"))
    assert result is None
