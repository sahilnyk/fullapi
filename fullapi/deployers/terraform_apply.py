"""Terraform applier for executing terraform commands."""

from pathlib import Path
import subprocess


class TerraformApplier:
    """Executes terraform commands to deploy infrastructure."""

    def __init__(self, terraform_dir: Path):
        """Initialize applier with terraform directory.

        Args:
            terraform_dir: Path to directory containing terraform files
        """
        self.terraform_dir = terraform_dir

    def init(self) -> str:
        """Run terraform init to initialize the working directory.

        Returns:
            stdout output from terraform init command

        Raises:
            subprocess.CalledProcessError: If terraform init fails
        """
        result = subprocess.run(
            ["terraform", "init"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def plan(self) -> str:
        """Run terraform plan to show execution plan.

        Returns:
            stdout output from terraform plan command

        Raises:
            subprocess.CalledProcessError: If terraform plan fails
        """
        result = subprocess.run(
            ["terraform", "plan"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def apply(self) -> str:
        """Run terraform apply to create/update infrastructure.

        Returns:
            stdout output from terraform apply command

        Raises:
            subprocess.CalledProcessError: If terraform apply fails
        """
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
