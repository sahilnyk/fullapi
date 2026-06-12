"""Tests for Docker builder."""

from unittest.mock import Mock, patch
from fullapi.deployers.docker_builder import DockerBuilder


def test_docker_builder_initialization():
    """Test DockerBuilder initialization."""
    builder = DockerBuilder(
        project_name="myapi",
        cloud_provider="aws",
        region="us-east-1",
        dockerfile_path="Dockerfile"
    )

    assert builder.project_name == "myapi"
    assert builder.cloud_provider == "aws"


@patch('subprocess.run')
def test_generate_dockerfile(mock_run, tmp_path):
    """Test Dockerfile generation when none exists."""
    builder = DockerBuilder(
        project_name="myapi",
        cloud_provider="aws",
        region="us-east-1",
        dockerfile_path=None
    )

    dockerfile = builder._generate_dockerfile(tmp_path, 8000)

    assert "FROM python:3.11-slim" in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "uvicorn" in dockerfile


@patch('subprocess.run')
def test_get_aws_account_id(mock_run):
    """Test AWS account ID retrieval."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout='{"Account": "123456789012"}'
    )

    builder = DockerBuilder(
        project_name="myapi",
        cloud_provider="aws",
        region="us-east-1",
        dockerfile_path="Dockerfile"
    )

    account_id = builder._get_aws_account_id()
    assert account_id == "123456789012"
