"""Tests for deployment planning."""

from fullapi.analyzers.codebase import CodebaseAnalysis
from fullapi.deployers.planner import DeploymentPlanner, DeploymentSpec


def test_deployment_spec_creation():
    """Test DeploymentSpec dataclass."""
    spec = DeploymentSpec(
        project_name="myapi",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database={"type": "postgresql", "version": "15"},
        redis=True,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={"PORT": "8000"},
        secrets=["SECRET_KEY"],
        instance_size="small",
        existing_deployment=False,
        changes_detected=[]
    )

    assert spec.project_name == "myapi"
    assert spec.cloud_provider == "aws"
    assert spec.redis is True


def test_planner_creates_spec_from_analysis():
    """Test creating deployment spec from analysis."""
    analysis = CodebaseAnalysis(
        database={"type": "postgresql", "version": "15"},
        redis=True,
        port=8000,
        health_check_path="/health",
        env_vars={"SECRET_KEY": "secret", "PORT": "8000"},
        secrets=["SECRET_KEY"],
        dependencies=["fastapi==0.104.1"],
        has_custom_dockerfile=True,
        dockerfile_path="Dockerfile",
        has_docker_compose=False,
        compose_path=None
    )

    planner = DeploymentPlanner(
        analysis=analysis,
        project_name="myapi",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1"
    )

    spec = planner.create_spec()

    assert spec.project_name == "myapi"
    assert spec.cloud_provider == "aws"
    assert spec.database["type"] == "postgresql"
    assert "SECRET_KEY" in spec.secrets
