"""Tests for codebase analyzers."""

from fullapi.analyzers.codebase import CodebaseAnalysis, CodebaseAnalyzer


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


def test_analyzer_detects_database_from_requirements(tmp_path):
    """Test database detection from requirements.txt."""
    (tmp_path / "requirements.txt").write_text("""
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.9
""")
    (tmp_path / "models").mkdir()

    analyzer = CodebaseAnalyzer(tmp_path)
    analysis = analyzer.analyze()

    assert analysis.database is not None
    assert analysis.database["type"] == "postgresql"


def test_analyzer_detects_redis(tmp_path):
    """Test Redis detection from requirements.txt."""
    (tmp_path / "requirements.txt").write_text("""
fastapi==0.104.1
redis==5.0.0
""")

    analyzer = CodebaseAnalyzer(tmp_path)
    analysis = analyzer.analyze()

    assert analysis.redis is True


def test_analyzer_detects_port_from_dockerfile(tmp_path):
    """Test port detection from Dockerfile."""
    (tmp_path / "Dockerfile").write_text("""
FROM python:3.11-slim
EXPOSE 9000
CMD ["uvicorn", "main:app"]
""")
    (tmp_path / "requirements.txt").write_text("fastapi==0.104.1")

    analyzer = CodebaseAnalyzer(tmp_path)
    analysis = analyzer.analyze()

    assert analysis.port == 9000
    assert analysis.has_custom_dockerfile is True


def test_analyzer_env_vars_classification(tmp_path):
    """Test environment variable classification into secrets."""
    (tmp_path / ".env.example").write_text("""
PORT=8000
DEBUG=true
SECRET_KEY=change-me
DATABASE_PASSWORD=secret
API_KEY=your-key-here
""")
    (tmp_path / "requirements.txt").write_text("fastapi==0.104.1")

    analyzer = CodebaseAnalyzer(tmp_path)
    analysis = analyzer.analyze()

    assert "PORT" in analysis.env_vars
    assert "SECRET_KEY" in analysis.secrets
    assert "DATABASE_PASSWORD" in analysis.secrets
    assert "API_KEY" in analysis.secrets
    assert "PORT" not in analysis.secrets
