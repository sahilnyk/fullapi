"""Tests for the main deploy command orchestration."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, call

import pytest

from fullapi.analyzers.codebase import CodebaseAnalysis
from fullapi.commands.deploy import deploy_project
from fullapi.deployers.planner import DeploymentSpec


@pytest.fixture
def sample_analysis():
    """Create a sample codebase analysis."""
    return CodebaseAnalysis(
        database={"type": "postgresql", "version": "15"},
        redis=True,
        port=8000,
        health_check_path="/health",
        env_vars={"PORT": "8000", "DEBUG": "false", "SECRET_KEY": "secret"},
        secrets=["SECRET_KEY"],
        dependencies=["fastapi==0.104.1", "uvicorn==0.24.0"],
        has_custom_dockerfile=True,
        dockerfile_path="Dockerfile",
        has_docker_compose=False,
        compose_path=None
    )


@pytest.fixture
def sample_spec():
    """Create a sample deployment spec."""
    return DeploymentSpec(
        project_name="test-app",
        cloud_provider="aws",
        deployment_type="server",
        region="us-east-1",
        database={"type": "postgresql", "version": "15"},
        redis=True,
        port=8000,
        health_check_path="/health",
        dockerfile_path="Dockerfile",
        image_uri="",
        env_vars={"PORT": "8000", "DEBUG": "false"},
        secrets=["SECRET_KEY"],
        instance_size="small"
    )


def test_deploy_project_orchestration_flow(tmp_path, sample_analysis, sample_spec):
    """Test that deploy_project orchestrates all steps correctly."""
    # Mock all components
    with patch('fullapi.commands.deploy.CodebaseAnalyzer') as mock_analyzer, \
         patch('fullapi.commands.deploy.DeploymentPlanner') as mock_planner, \
         patch('fullapi.commands.deploy.DockerBuilder') as mock_builder, \
         patch('fullapi.commands.deploy.TerraformGenerator') as mock_generator, \
         patch('fullapi.commands.deploy.TerraformApplier') as mock_applier:

        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = sample_analysis
        mock_analyzer.return_value = mock_analyzer_instance

        mock_planner_instance = Mock()
        mock_planner_instance.create_spec.return_value = sample_spec
        mock_planner_instance.get_confirmation.return_value = True
        mock_planner.return_value = mock_planner_instance

        mock_builder_instance = Mock()
        mock_builder_instance.build_and_push.return_value = "123456789.dkr.ecr.us-east-1.amazonaws.com/test-app:latest"
        mock_builder.return_value = mock_builder_instance

        mock_generator_instance = Mock()
        mock_generator.return_value = mock_generator_instance

        mock_applier_instance = Mock()
        mock_applier_instance.init.return_value = "Terraform initialized"
        mock_applier_instance.plan.return_value = "Terraform plan output"
        mock_applier_instance.apply.return_value = "Terraform apply output"
        mock_applier.return_value = mock_applier_instance

        # Call deploy_project
        result = deploy_project(
            project_path=tmp_path,
            cloud_provider="aws",
            deployment_type="server",
            app_name="test-app",
            region="us-east-1"
        )

        # Verify orchestration flow
        assert result is True

        # Verify step 1: Codebase analysis
        mock_analyzer.assert_called_once_with(tmp_path)
        mock_analyzer_instance.analyze.assert_called_once()

        # Verify step 2: Create deployment plan
        mock_planner.assert_called_once_with(
            sample_analysis, "test-app", "aws", "server", "us-east-1"
        )
        mock_planner_instance.create_spec.assert_called_once()
        mock_planner_instance.show_summary.assert_called_once()

        # Verify step 3: User confirmation
        mock_planner_instance.get_confirmation.assert_called_once()

        # Verify step 4: Build and push Docker image
        mock_builder.assert_called_once_with(
            "test-app", "aws", "us-east-1", "Dockerfile"
        )
        mock_builder_instance.build_and_push.assert_called_once_with(tmp_path, 8000)

        # Verify step 5: Generate terraform files
        mock_generator.assert_called_once()
        assert mock_generator.call_args[0][0].project_name == "test-app"
        mock_generator_instance.generate.assert_called_once()

        # Verify step 6: Apply terraform
        mock_applier.assert_called_once()
        terraform_dir = tmp_path / "terraform"
        mock_applier.assert_called_with(terraform_dir)
        mock_applier_instance.init.assert_called_once()
        mock_applier_instance.plan.assert_called_once()
        mock_applier_instance.apply.assert_called_once()


def test_deploy_project_user_cancels(tmp_path, sample_analysis, sample_spec):
    """Test that deployment stops when user cancels confirmation."""
    with patch('fullapi.commands.deploy.CodebaseAnalyzer') as mock_analyzer, \
         patch('fullapi.commands.deploy.DeploymentPlanner') as mock_planner, \
         patch('fullapi.commands.deploy.DockerBuilder') as mock_builder:

        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = sample_analysis
        mock_analyzer.return_value = mock_analyzer_instance

        mock_planner_instance = Mock()
        mock_planner_instance.create_spec.return_value = sample_spec
        mock_planner_instance.get_confirmation.return_value = False  # User cancels
        mock_planner.return_value = mock_planner_instance

        mock_builder_instance = Mock()
        mock_builder.return_value = mock_builder_instance

        # Call deploy_project
        result = deploy_project(
            project_path=tmp_path,
            cloud_provider="aws",
            deployment_type="server",
            app_name="test-app",
            region="us-east-1"
        )

        # Verify deployment was cancelled
        assert result is False

        # Verify Docker build was NOT called
        mock_builder_instance.build_and_push.assert_not_called()


def test_deploy_project_docker_build_fails(tmp_path, sample_analysis, sample_spec):
    """Test error handling when Docker build fails."""
    with patch('fullapi.commands.deploy.CodebaseAnalyzer') as mock_analyzer, \
         patch('fullapi.commands.deploy.DeploymentPlanner') as mock_planner, \
         patch('fullapi.commands.deploy.DockerBuilder') as mock_builder:

        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = sample_analysis
        mock_analyzer.return_value = mock_analyzer_instance

        mock_planner_instance = Mock()
        mock_planner_instance.create_spec.return_value = sample_spec
        mock_planner_instance.get_confirmation.return_value = True
        mock_planner.return_value = mock_planner_instance

        mock_builder_instance = Mock()
        mock_builder_instance.build_and_push.side_effect = RuntimeError("Docker build failed")
        mock_builder.return_value = mock_builder_instance

        # Call deploy_project and expect it to handle error
        result = deploy_project(
            project_path=tmp_path,
            cloud_provider="aws",
            deployment_type="server",
            app_name="test-app",
            region="us-east-1"
        )

        # Verify deployment failed gracefully
        assert result is False


def test_deploy_project_terraform_fails(tmp_path, sample_analysis, sample_spec):
    """Test error handling when terraform apply fails."""
    with patch('fullapi.commands.deploy.CodebaseAnalyzer') as mock_analyzer, \
         patch('fullapi.commands.deploy.DeploymentPlanner') as mock_planner, \
         patch('fullapi.commands.deploy.DockerBuilder') as mock_builder, \
         patch('fullapi.commands.deploy.TerraformGenerator') as mock_generator, \
         patch('fullapi.commands.deploy.TerraformApplier') as mock_applier:

        # Setup mocks
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = sample_analysis
        mock_analyzer.return_value = mock_analyzer_instance

        mock_planner_instance = Mock()
        mock_planner_instance.create_spec.return_value = sample_spec
        mock_planner_instance.get_confirmation.return_value = True
        mock_planner.return_value = mock_planner_instance

        mock_builder_instance = Mock()
        mock_builder_instance.build_and_push.return_value = "123456789.dkr.ecr.us-east-1.amazonaws.com/test-app:latest"
        mock_builder.return_value = mock_builder_instance

        mock_generator_instance = Mock()
        mock_generator.return_value = mock_generator_instance

        mock_applier_instance = Mock()
        mock_applier_instance.init.return_value = "Terraform initialized"
        mock_applier_instance.plan.return_value = "Terraform plan"
        # Terraform apply fails
        mock_applier_instance.apply.side_effect = subprocess.CalledProcessError(1, "terraform apply", stderr="Error")
        mock_applier.return_value = mock_applier_instance

        # Call deploy_project
        result = deploy_project(
            project_path=tmp_path,
            cloud_provider="aws",
            deployment_type="server",
            app_name="test-app",
            region="us-east-1"
        )

        # Verify deployment failed gracefully
        assert result is False


def test_deploy_project_default_values():
    """Test deploy_project with default parameter values."""
    with patch('fullapi.commands.deploy.CodebaseAnalyzer') as mock_analyzer, \
         patch('fullapi.commands.deploy.DeploymentPlanner') as mock_planner, \
         patch('fullapi.commands.deploy.DockerBuilder') as mock_builder, \
         patch('fullapi.commands.deploy.TerraformGenerator') as mock_generator, \
         patch('fullapi.commands.deploy.TerraformApplier') as mock_applier:

        # Setup minimal mocks
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze.return_value = CodebaseAnalysis(
            database=None,
            redis=False,
            port=8000,
            health_check_path="/health",
            env_vars={},
            secrets=[],
            dependencies=["fastapi"],
            has_custom_dockerfile=False,
            dockerfile_path=None,
            has_docker_compose=False,
            compose_path=None
        )
        mock_analyzer.return_value = mock_analyzer_instance

        mock_planner_instance = Mock()
        mock_planner_instance.create_spec.return_value = DeploymentSpec(
            project_name="my-app",
            cloud_provider="aws",
            deployment_type="server",
            region="us-east-1",
            database=None,
            redis=False,
            port=8000,
            health_check_path="/health",
            dockerfile_path=None,
            image_uri="",
            env_vars={},
            secrets=[]
        )
        mock_planner_instance.get_confirmation.return_value = False  # Cancel to avoid full flow
        mock_planner.return_value = mock_planner_instance

        # Call with defaults (should use current directory and default region)
        result = deploy_project(
            project_path=Path("."),
            cloud_provider="aws",
            deployment_type="server",
            app_name="my-app"
        )

        # Verify planner was called with default region
        mock_planner.assert_called_once()
        call_args = mock_planner.call_args[0]
        assert call_args[4] == "us-east-1"  # Default region
