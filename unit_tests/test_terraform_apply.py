"""Tests for Terraform applier."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess
import pytest

from fullapi.deployers.terraform_apply import TerraformApplier


def test_applier_initializes_with_terraform_dir():
    """Test that TerraformApplier initializes with terraform directory path."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)
    assert applier.terraform_dir == terraform_dir


def test_init_runs_terraform_init():
    """Test that init() runs terraform init command."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        applier.init()

        mock_run.assert_called_once_with(
            ["terraform", "init"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )


def test_init_raises_error_on_failure():
    """Test that init() raises exception when terraform init fails."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["terraform", "init"],
            stderr="Error: terraform not found"
        )

        with pytest.raises(subprocess.CalledProcessError):
            applier.init()


def test_plan_runs_terraform_plan():
    """Test that plan() runs terraform plan command."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Plan: 10 to add, 0 to change, 0 to destroy.",
            stderr=""
        )
        result = applier.plan()

        mock_run.assert_called_once_with(
            ["terraform", "plan"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        assert "Plan: 10 to add" in result


def test_plan_raises_error_on_failure():
    """Test that plan() raises exception when terraform plan fails."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["terraform", "plan"],
            stderr="Error: Invalid configuration"
        )

        with pytest.raises(subprocess.CalledProcessError):
            applier.plan()


def test_apply_runs_terraform_apply_with_auto_approve():
    """Test that apply() runs terraform apply with -auto-approve flag."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Apply complete! Resources: 10 added, 0 changed, 0 destroyed.",
            stderr=""
        )
        result = applier.apply()

        mock_run.assert_called_once_with(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        assert "Apply complete!" in result


def test_apply_raises_error_on_failure():
    """Test that apply() raises exception when terraform apply fails."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["terraform", "apply"],
            stderr="Error: Failed to create resource"
        )

        with pytest.raises(subprocess.CalledProcessError):
            applier.apply()


def test_init_returns_output():
    """Test that init() returns stdout output."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Initializing the backend...\nTerraform has been successfully initialized!",
            stderr=""
        )
        result = applier.init()

        assert "successfully initialized" in result


def test_plan_returns_full_output():
    """Test that plan() returns full stdout output."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    expected_output = """
Terraform will perform the following actions:

  # aws_ecs_cluster.main will be created
  + resource "aws_ecs_cluster" "main" {
      + arn  = (known after apply)
      + name = "test-cluster"
    }

Plan: 10 to add, 0 to change, 0 to destroy.
"""

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=expected_output,
            stderr=""
        )
        result = applier.plan()

        assert "aws_ecs_cluster.main will be created" in result
        assert "Plan: 10 to add, 0 to change, 0 to destroy" in result


def test_apply_returns_full_output():
    """Test that apply() returns full stdout output."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    expected_output = """
aws_ecs_cluster.main: Creating...
aws_ecs_cluster.main: Creation complete after 5s

Apply complete! Resources: 10 added, 0 changed, 0 destroyed.

Outputs:

service_url = "http://test-lb-123456.us-east-1.elb.amazonaws.com"
"""

    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=expected_output,
            stderr=""
        )
        result = applier.apply()

        assert "Creation complete" in result
        assert "Apply complete!" in result
        assert "service_url" in result


def test_multiple_operations_in_sequence():
    """Test that init, plan, and apply can be called in sequence."""
    terraform_dir = Path("/tmp/project/terraform")
    applier = TerraformApplier(terraform_dir)

    with patch('subprocess.run') as mock_run:
        # Set up return values for each call
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Terraform initialized!", stderr=""),
            MagicMock(returncode=0, stdout="Plan: 10 to add", stderr=""),
            MagicMock(returncode=0, stdout="Apply complete!", stderr="")
        ]

        init_result = applier.init()
        plan_result = applier.plan()
        apply_result = applier.apply()

        assert "initialized" in init_result
        assert "Plan: 10 to add" in plan_result
        assert "Apply complete" in apply_result

        # Verify all three commands were called
        assert mock_run.call_count == 3
        assert mock_run.call_args_list[0][0][0] == ["terraform", "init"]
        assert mock_run.call_args_list[1][0][0] == ["terraform", "plan"]
        assert mock_run.call_args_list[2][0][0] == ["terraform", "apply", "-auto-approve"]
