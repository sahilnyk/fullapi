"""Docker image building and pushing."""

import json
import subprocess
from pathlib import Path
from typing import Optional

from fullapi.colors import ICON_CHECK, ICON_CROSS, color, error, info, Style


class DockerBuilder:
    """Builds and pushes Docker images to cloud registries."""

    def __init__(self, project_name: str, cloud_provider: str,
                 region: str, dockerfile_path: Optional[str]):
        """Initialize builder."""
        self.project_name = project_name
        self.cloud_provider = cloud_provider
        self.region = region
        self.dockerfile_path = dockerfile_path

    def build_and_push(self, project_path: Path, port: int) -> str:
        """Build Docker image and push to cloud registry.

        Returns: Image URI
        """
        # Generate Dockerfile if needed
        if not self.dockerfile_path:
            print(f"  {info('Generating Dockerfile...')}")
            dockerfile_content = self._generate_dockerfile(project_path, port)
            dockerfile_path = project_path / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)
            print(f"  {ICON_CHECK}  Dockerfile created")
        else:
            print(f"  {ICON_CHECK}  Using existing Dockerfile")

        # Build image
        print()
        print(f"  {info('Building Docker image...')}")
        if not self._build_image(project_path):
            raise RuntimeError("Docker build failed")
        print(f"  {ICON_CHECK}  Image built")

        # Push to registry
        print()
        print(f"  {info(f'Pushing to {self.cloud_provider.upper()} registry...')}")
        image_uri = self._push_to_registry(project_path)
        if not image_uri:
            raise RuntimeError("Docker push failed")
        print(f"  {ICON_CHECK}  Image pushed: {image_uri}")

        return image_uri

    def _generate_dockerfile(self, project_path: Path, port: int) -> str:
        """Generate a Dockerfile."""
        return f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
"""

    def _build_image(self, project_path: Path) -> bool:
        """Build Docker image."""
        tag = f"{self.project_name}:latest"

        result = subprocess.run(
            ["docker", "build", "-t", tag, "."],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  {ICON_CROSS}  {error('Build failed:')}")
            print(result.stderr)
            return False

        return True

    def _push_to_registry(self, project_path: Path) -> Optional[str]:
        """Push image to cloud registry."""
        if self.cloud_provider == "aws":
            return self._push_to_ecr(project_path)
        elif self.cloud_provider == "gcp":
            return self._push_to_artifact_registry(project_path)
        elif self.cloud_provider == "azure":
            return self._push_to_acr(project_path)
        else:
            print(f"  {ICON_CROSS}  {error(f'Unknown cloud provider: {self.cloud_provider}')}")
            return None

    def _push_to_ecr(self, project_path: Path) -> Optional[str]:
        """Push image to AWS ECR."""
        # Get AWS account ID
        account_id = self._get_aws_account_id()
        if not account_id:
            print(f"  {ICON_CROSS}  {error('Could not get AWS account ID')}")
            return None

        # ECR repository URL
        ecr_url = f"{account_id}.dkr.ecr.{self.region}.amazonaws.com"
        repo_name = self.project_name

        # Create ECR repository if not exists
        print(f"    Creating ECR repository...")
        subprocess.run(
            ["aws", "ecr", "create-repository",
             "--repository-name", repo_name,
             "--region", self.region],
            capture_output=True
        )
        # Ignore error if repository already exists

        # Authenticate Docker to ECR
        print(f"    Authenticating...")
        result = subprocess.run(
            ["aws", "ecr", "get-login-password", "--region", self.region],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  {ICON_CROSS}  {error('ECR authentication failed')}")
            return None

        password = result.stdout.strip()

        result = subprocess.run(
            ["docker", "login", "--username", "AWS",
             "--password-stdin", ecr_url],
            input=password,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  {ICON_CROSS}  {error('Docker login failed')}")
            return None

        # Tag image for ECR
        local_tag = f"{self.project_name}:latest"
        remote_tag = f"{ecr_url}/{repo_name}:latest"

        result = subprocess.run(
            ["docker", "tag", local_tag, remote_tag],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  {ICON_CROSS}  {error('Docker tag failed')}")
            return None

        # Push to ECR
        print(f"    Pushing image...")
        result = subprocess.run(
            ["docker", "push", remote_tag],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  {ICON_CROSS}  {error('Docker push failed')}")
            print(result.stderr)
            return None

        return remote_tag

    def _push_to_artifact_registry(self, project_path: Path) -> Optional[str]:
        """Push image to GCP Artifact Registry."""
        # Placeholder for GCP - Phase 2
        print(f"  {ICON_CROSS}  {error('GCP support not yet implemented')}")
        return None

    def _push_to_acr(self, project_path: Path) -> Optional[str]:
        """Push image to Azure Container Registry."""
        # Placeholder for Azure - Phase 2
        print(f"  {ICON_CROSS}  {error('Azure support not yet implemented')}")
        return None

    def _get_aws_account_id(self) -> Optional[str]:
        """Get AWS account ID."""
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return None

        try:
            data = json.loads(result.stdout)
            return data.get("Account")
        except (json.JSONDecodeError, KeyError):
            return None
