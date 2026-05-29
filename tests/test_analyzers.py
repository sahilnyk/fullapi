"""Tests for codebase analyzers."""

from fullapi.analyzers.codebase import CodebaseAnalysis


def test_codebase_analysis_creation():
    """Test CodebaseAnalysis dataclass creation."""
    analysis = CodebaseAnalysis(
        database={"type": "postgresql", "version": "15"},
        redis=True,
        port=8000,
        health_check_path="/health",
        env_vars={"PORT": "8000", "SECRET_KEY": "secret"},
        secrets=["SECRET_KEY"],
        dependencies=["fastapi==0.104.1", "uvicorn==0.24.0"],
        has_custom_dockerfile=True,
        dockerfile_path="Dockerfile",
        has_docker_compose=False,
        compose_path=None
    )

    assert analysis.database["type"] == "postgresql"
    assert analysis.redis is True
    assert analysis.port == 8000
    assert "SECRET_KEY" in analysis.secrets
    assert analysis.has_custom_dockerfile is True
