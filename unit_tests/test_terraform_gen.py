"""Tests for Terraform file generation."""

from pathlib import Path
from fullapi.deployers.terraform_gen import TerraformGenerator
from fullapi.deployers.planner import DeploymentSpec


def test_generate_creates_terraform_directory(tmp_path):
    """Test that generate creates terraform/ directory."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    terraform_dir = tmp_path / "terraform"
    assert terraform_dir.exists()
    assert terraform_dir.is_dir()


def test_generate_creates_all_required_files(tmp_path):
    """Test that generate creates all required terraform files."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    terraform_dir = tmp_path / "terraform"
    assert (terraform_dir / "main.tf").exists()
    assert (terraform_dir / "variables.tf").exists()
    assert (terraform_dir / "outputs.tf").exists()
    assert (terraform_dir / "terraform.tfvars").exists()


def test_main_tf_contains_terraform_block(tmp_path):
    """Test that main.tf contains terraform version block."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    main_tf = (tmp_path / "terraform" / "main.tf").read_text()
    assert 'terraform {' in main_tf
    assert 'required_version = ">= 1.0.0"' in main_tf
    assert 'hashicorp/aws' in main_tf


def test_main_tf_includes_ecs_resources(tmp_path):
    """Test that main.tf includes ECS cluster and service resources."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    main_tf = (tmp_path / "terraform" / "main.tf").read_text()
    assert 'resource "aws_ecs_cluster"' in main_tf
    assert 'resource "aws_ecs_service"' in main_tf
    assert 'resource "aws_ecs_task_definition"' in main_tf


def test_main_tf_includes_database_when_specified(tmp_path):
    """Test that main.tf includes RDS resources when database is specified."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database={"type": "postgresql", "version": "15"},
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    main_tf = (tmp_path / "terraform" / "main.tf").read_text()
    assert 'resource "aws_db_instance"' in main_tf
    assert '"postgres"' in main_tf


def test_main_tf_includes_redis_when_specified(tmp_path):
    """Test that main.tf includes ElastiCache resources when redis is specified."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=True,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    main_tf = (tmp_path / "terraform" / "main.tf").read_text()
    assert 'resource "aws_elasticache_cluster"' in main_tf
    assert '"redis"' in main_tf


def test_variables_tf_contains_required_variables(tmp_path):
    """Test that variables.tf contains required variable definitions."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    variables_tf = (tmp_path / "terraform" / "variables.tf").read_text()
    assert 'variable "project_name"' in variables_tf
    assert 'variable "region"' in variables_tf
    assert 'variable "image_uri"' in variables_tf
    assert 'variable "container_port"' in variables_tf
    assert 'variable "health_check_path"' in variables_tf


def test_variables_tf_includes_db_vars_when_database_specified(tmp_path):
    """Test that variables.tf includes database variables when database is specified."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database={"type": "postgresql", "version": "15"},
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    variables_tf = (tmp_path / "terraform" / "variables.tf").read_text()
    assert 'variable "db_username"' in variables_tf
    assert 'variable "db_password"' in variables_tf
    assert 'sensitive   = true' in variables_tf


def test_outputs_tf_contains_service_url(tmp_path):
    """Test that outputs.tf contains service_url output."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    outputs_tf = (tmp_path / "terraform" / "outputs.tf").read_text()
    assert 'output "service_url"' in outputs_tf
    assert 'aws_lb.main.dns_name' in outputs_tf


def test_outputs_tf_includes_database_endpoint_when_specified(tmp_path):
    """Test that outputs.tf includes database_endpoint when database is specified."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database={"type": "postgresql", "version": "15"},
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    outputs_tf = (tmp_path / "terraform" / "outputs.tf").read_text()
    assert 'output "database_endpoint"' in outputs_tf
    assert 'aws_db_instance.main.endpoint' in outputs_tf


def test_outputs_tf_includes_redis_endpoint_when_specified(tmp_path):
    """Test that outputs.tf includes redis_endpoint when redis is specified."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database=None,
        redis=True,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    outputs_tf = (tmp_path / "terraform" / "outputs.tf").read_text()
    assert 'output "redis_endpoint"' in outputs_tf
    assert 'aws_elasticache_cluster.main.cache_nodes.0.address' in outputs_tf


def test_tfvars_contains_correct_values(tmp_path):
    """Test that terraform.tfvars contains correct values from spec."""
    spec = DeploymentSpec(
        project_name="my-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-west-2",
        database=None,
        redis=False,
        port=9000,
        health_check_path="/api/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    image_uri = "123456789.dkr.ecr.us-west-2.amazonaws.com/my-api:v1.0"
    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, image_uri)

    tfvars = (tmp_path / "terraform" / "terraform.tfvars").read_text()
    assert 'project_name       = "my-api"' in tfvars
    assert 'region             = "us-west-2"' in tfvars
    assert f'image_uri          = "{image_uri}"' in tfvars
    assert 'container_port     = 9000' in tfvars
    assert 'health_check_path  = "/api/health"' in tfvars


def test_tfvars_includes_database_credentials_when_specified(tmp_path):
    """Test that terraform.tfvars includes database credentials when database is specified."""
    spec = DeploymentSpec(
        project_name="test-api",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database={"type": "postgresql", "version": "15"},
        redis=False,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={},
        secrets=[]
    )

    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, "123456789.dkr.ecr.us-east-1.amazonaws.com/test-api:latest")

    tfvars = (tmp_path / "terraform" / "terraform.tfvars").read_text()
    assert 'db_username' in tfvars
    assert 'db_password' in tfvars
    assert 'CHANGE_ME_IN_PRODUCTION' in tfvars


def test_generate_with_full_spec(tmp_path):
    """Test generate with database and redis both enabled."""
    spec = DeploymentSpec(
        project_name="full-api",
        cloud_provider="aws",
        deployment_type="server",
        region="eu-west-1",
        database={"type": "postgresql", "version": "15"},
        redis=True,
        port=8080,
        health_check_path="/api/v1/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={"ENV": "production"},
        secrets=["API_KEY", "SECRET_KEY"]
    )

    image_uri = "123456789.dkr.ecr.eu-west-1.amazonaws.com/full-api:latest"
    generator = TerraformGenerator(spec)
    generator.generate(tmp_path, image_uri)

    # Check all files exist
    terraform_dir = tmp_path / "terraform"
    assert (terraform_dir / "main.tf").exists()
    assert (terraform_dir / "variables.tf").exists()
    assert (terraform_dir / "outputs.tf").exists()
    assert (terraform_dir / "terraform.tfvars").exists()

    # Check main.tf has both database and redis
    main_tf = (terraform_dir / "main.tf").read_text()
    assert 'resource "aws_db_instance"' in main_tf
    assert 'resource "aws_elasticache_cluster"' in main_tf

    # Check outputs has both database and redis endpoints
    outputs_tf = (terraform_dir / "outputs.tf").read_text()
    assert 'output "database_endpoint"' in outputs_tf
    assert 'output "redis_endpoint"' in outputs_tf
