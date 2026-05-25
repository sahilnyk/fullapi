"""Test Terraform infrastructure support."""

import tempfile
import shutil
from pathlib import Path

from fullapi.config import ProjectConfig
from fullapi.scaffold import scaffold_project


def test_terraform_flag_generates_files():
    """Test that --terraform flag generates Terraform files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = Path.cwd()
        try:
            tmpdir_path = Path(tmpdir)
            # Change to temp directory for test
            import os
            os.chdir(tmpdir_path)

            config = ProjectConfig(
                name="test_terraform_api",
                mode="full",
                database="postgresql",
                docker=True,
                redis=True,
                terraform=True,
                cloud_provider="aws",
                region="us-east-1",
                instance_size="small"
            )

            scaffold_project(config)

            project_path = tmpdir_path / "test_terraform_api"
            terraform_dir = project_path / "terraform"

            # Verify terraform directory exists
            assert terraform_dir.exists(), "terraform/ directory not created"

            # Verify required files exist
            assert (terraform_dir / "main.tf").exists(), "main.tf not created"
            assert (terraform_dir / "variables.tf").exists(), "variables.tf not created"
            assert (terraform_dir / "outputs.tf").exists(), "outputs.tf not created"
            assert (terraform_dir / "terraform.tfvars").exists(), "terraform.tfvars not created"
            assert (terraform_dir / "README.md").exists(), "README.md not created"

            # Verify .gitignore includes terraform entries
            gitignore_path = project_path / ".gitignore"
            if gitignore_path.exists():
                gitignore_content = gitignore_path.read_text()
                assert "*.tfstate" in gitignore_content, ".gitignore missing terraform entries"

            # Verify metadata includes terraform config
            metadata_path = project_path / ".fullapi.json"
            assert metadata_path.exists(), ".fullapi.json not created"

            import json
            metadata = json.loads(metadata_path.read_text())
            assert metadata["terraform"] is True, "metadata missing terraform flag"
            assert metadata["cloud_provider"] == "aws", "metadata missing cloud_provider"
            assert metadata["region"] == "us-east-1", "metadata missing region"

            # Verify main.tf has correct provider
            main_tf_content = (terraform_dir / "main.tf").read_text()
            assert "provider \"aws\"" in main_tf_content, "main.tf missing AWS provider"
            assert "module \"database\"" in main_tf_content, "main.tf missing database module"
            assert "module \"cache\"" in main_tf_content, "main.tf missing cache module"

        finally:
            os.chdir(original_dir)


def test_terraform_conditional_modules():
    """Test that modules are conditionally included based on features."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = Path.cwd()
        try:
            tmpdir_path = Path(tmpdir)
            import os
            os.chdir(tmpdir_path)

            # Basic config without database or redis
            config = ProjectConfig(
                name="test_basic_terraform",
                mode="basic",
                database="none",
                docker=True,
                redis=False,
                terraform=True,
                cloud_provider="aws",
                region="us-west-2",
                instance_size="small"
            )

            scaffold_project(config)

            project_path = tmpdir_path / "test_basic_terraform"
            terraform_dir = project_path / "terraform"
            main_tf_content = (terraform_dir / "main.tf").read_text()

            # Should NOT include database or cache modules
            assert "module \"database\"" not in main_tf_content, "main.tf incorrectly includes database module"
            assert "module \"cache\"" not in main_tf_content, "main.tf incorrectly includes cache module"

            # Should still include compute and network
            assert "module \"compute\"" in main_tf_content, "main.tf missing compute module"
            assert "module \"network\"" in main_tf_content, "main.tf missing network module"

        finally:
            os.chdir(original_dir)
