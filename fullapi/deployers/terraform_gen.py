"""Terraform file generator."""

from pathlib import Path
from typing import Optional

from fullapi.cloud_templates.aws_server import AWSServerTemplate
from fullapi.deployers.planner import DeploymentSpec


class TerraformGenerator:
    """Generates terraform configuration files from deployment spec."""

    def __init__(self, spec: DeploymentSpec):
        """Initialize generator with deployment spec."""
        self.spec = spec

    def generate(self, output_dir: Path, image_uri: str) -> None:
        """Generate terraform files in output_dir/terraform/.

        Args:
            output_dir: Base directory where terraform/ will be created
            image_uri: Docker image URI to use in terraform config
        """
        # Create terraform directory
        terraform_dir = output_dir / "terraform"
        terraform_dir.mkdir(parents=True, exist_ok=True)

        # Get the appropriate template based on cloud provider and deployment type
        template = self._get_template()

        # Generate and write all terraform files
        self._write_file(terraform_dir / "main.tf", template.generate_main_tf())
        self._write_file(terraform_dir / "variables.tf", template.generate_variables_tf())
        self._write_file(terraform_dir / "outputs.tf", template.generate_outputs_tf())
        self._write_file(
            terraform_dir / "terraform.tfvars",
            template.generate_tfvars(
                image_uri=image_uri,
                port=self.spec.port,
                health_check=self.spec.health_check_path,
                env_vars=self.spec.env_vars
            )
        )

    def _get_template(self):
        """Get the appropriate cloud template based on spec."""
        if self.spec.cloud_provider == "aws" and self.spec.deployment_type == "server":
            return AWSServerTemplate(
                project_name=self.spec.project_name,
                region=self.spec.region,
                has_database=self.spec.database is not None,
                has_redis=self.spec.redis
            )
        else:
            # Future: Add GCP, Azure, Serverless templates
            raise NotImplementedError(
                f"Template for {self.spec.cloud_provider}/{self.spec.deployment_type} "
                "not yet implemented"
            )

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file."""
        path.write_text(content)
