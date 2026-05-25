"""Docker build and push operations."""

import subprocess
import sys
import json
from pathlib import Path

from fullapi.colors import color, Style


def _run_command(command: list) -> tuple:
    """Run command and return (exit_code, stdout)."""
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True
        )
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        print(f"{color('[ERROR]', Style.RED)} Command not found: {command[0]}")
        return 1, ""
    except Exception as e:
        print(f"{color('[ERROR]', Style.RED)} {str(e)}")
        return 1, ""


def _get_git_commit() -> str:
    """Get current git commit SHA (short)."""
    exit_code, stdout = _run_command(["git", "rev-parse", "--short", "HEAD"])
    if exit_code == 0 and stdout:
        return stdout
    return "latest"


def _get_project_metadata() -> dict:
    """Read project metadata from .fullapi.json."""
    metadata_path = Path.cwd() / ".fullapi.json"
    if not metadata_path.exists():
        return {}

    try:
        return json.loads(metadata_path.read_text())
    except:
        return {}


def _get_registry_url(cloud_provider: str, region: str, project_name: str) -> str:
    """Get registry URL based on cloud provider."""
    if cloud_provider == "aws":
        # Format: <account-id>.dkr.ecr.<region>.amazonaws.com/<repo-name>
        return f"<AWS_ACCOUNT_ID>.dkr.ecr.{region}.amazonaws.com/{project_name}"
    elif cloud_provider == "gcp":
        # Format: <region>-docker.pkg.dev/<project-id>/<repo-name>/<image-name>
        return f"{region}-docker.pkg.dev/<GCP_PROJECT_ID>/{project_name}/{project_name}"
    elif cloud_provider == "azure":
        # Format: <registry-name>.azurecr.io/<image-name>
        return f"<REGISTRY_NAME>.azurecr.io/{project_name}"
    return project_name


def docker_build():
    """Build Docker image."""
    dockerfile = Path.cwd() / "Dockerfile"

    if not dockerfile.exists():
        print(f"{color('[ERROR]', Style.RED)} No Dockerfile found")
        print(f"Enable Docker when creating project: fullapi new myapi --docker")
        return 1

    metadata = _get_project_metadata()
    project_name = metadata.get('name', Path.cwd().name)
    commit = _get_git_commit()

    image_tag = f"{project_name}:{commit}"

    print(f"{color('[INFO]', Style.CYAN)} Building Docker image...")
    print(f"  Image: {image_tag}")
    print()

    exit_code, _ = _run_command([
        "docker", "build",
        "-t", image_tag,
        "-t", f"{project_name}:latest",
        "."
    ])

    if exit_code == 0:
        print()
        print(f"{color('[OK]', Style.GREEN)} Image built: {image_tag}")
        print()
        print(f"Next steps:")
        print(f"  fullapi docker push")
    else:
        print(f"{color('[ERROR]', Style.RED)} Build failed")

    return exit_code


def docker_push():
    """Push Docker image to cloud registry."""
    metadata = _get_project_metadata()

    if not metadata:
        print(f"{color('[ERROR]', Style.RED)} No .fullapi.json found")
        return 1

    cloud_provider = metadata.get('cloud_provider')
    region = metadata.get('region')
    project_name = metadata.get('name', Path.cwd().name)

    if not cloud_provider or not region:
        print(f"{color('[ERROR]', Style.RED)} Terraform not configured")
        print(f"Create project with --terraform flag")
        return 1

    commit = _get_git_commit()
    local_tag = f"{project_name}:{commit}"
    registry_url = _get_registry_url(cloud_provider, region, project_name)
    remote_tag = f"{registry_url}:{commit}"

    print(f"{color('[INFO]', Style.CYAN)} Pushing to {cloud_provider.upper()} registry...")
    print(f"  Local:  {local_tag}")
    print(f"  Remote: {remote_tag}")
    print()

    # Check if local image exists
    exit_code, _ = _run_command(["docker", "image", "inspect", local_tag])
    if exit_code != 0:
        print(f"{color('[ERROR]', Style.RED)} Image not found: {local_tag}")
        print(f"Build it first: fullapi docker build")
        return 1

    # Authenticate based on cloud provider
    print(f"{color('[INFO]', Style.CYAN)} Authenticating...")
    auth_exit_code = _authenticate_registry(cloud_provider, region)
    if auth_exit_code != 0:
        return auth_exit_code

    # Tag for remote
    print(f"{color('[INFO]', Style.CYAN)} Tagging image...")
    exit_code, _ = _run_command(["docker", "tag", local_tag, remote_tag])
    if exit_code != 0:
        print(f"{color('[ERROR]', Style.RED)} Tagging failed")
        return exit_code

    # Push
    print(f"{color('[INFO]', Style.CYAN)} Pushing image...")
    exit_code, _ = _run_command(["docker", "push", remote_tag])

    if exit_code == 0:
        print()
        print(f"{color('[OK]', Style.GREEN)} Image pushed: {remote_tag}")
        print()
        print(f"Update terraform.tfvars:")
        print(f'  container_image_uri = "{remote_tag}"')
        print()
        print(f"Then deploy:")
        print(f"  fullapi terraform apply")

        # Update terraform.tfvars if it exists
        _update_tfvars(remote_tag)
    else:
        print(f"{color('[ERROR]', Style.RED)} Push failed")

    return exit_code


def _authenticate_registry(cloud_provider: str, region: str) -> int:
    """Authenticate with cloud registry."""
    if cloud_provider == "aws":
        print(f"  Authenticating with ECR...")
        exit_code, password = _run_command([
            "aws", "ecr", "get-login-password",
            "--region", region
        ])
        if exit_code != 0:
            print(f"{color('[ERROR]', Style.RED)} AWS CLI authentication failed")
            print(f"Run: aws configure")
            return exit_code

        exit_code, _ = _run_command([
            "docker", "login",
            "--username", "AWS",
            "--password-stdin",
            f"<AWS_ACCOUNT_ID>.dkr.ecr.{region}.amazonaws.com"
        ])
        return exit_code

    elif cloud_provider == "gcp":
        print(f"  Authenticating with GCR...")
        exit_code, _ = _run_command([
            "gcloud", "auth", "configure-docker",
            f"{region}-docker.pkg.dev"
        ])
        if exit_code != 0:
            print(f"{color('[ERROR]', Style.RED)} GCloud authentication failed")
            print(f"Run: gcloud auth login")
        return exit_code

    elif cloud_provider == "azure":
        print(f"  Authenticating with ACR...")
        exit_code, _ = _run_command([
            "az", "acr", "login",
            "--name", "<REGISTRY_NAME>"
        ])
        if exit_code != 0:
            print(f"{color('[ERROR]', Style.RED)} Azure CLI authentication failed")
            print(f"Run: az login")
        return exit_code

    return 0


def _update_tfvars(image_uri: str):
    """Update container_image_uri in terraform.tfvars."""
    tfvars_path = Path.cwd() / "terraform" / "terraform.tfvars"

    if not tfvars_path.exists():
        return

    try:
        content = tfvars_path.read_text()
        lines = content.split('\n')
        updated_lines = []

        for line in lines:
            if line.startswith('container_image_uri'):
                updated_lines.append(f'container_image_uri = "{image_uri}"')
            else:
                updated_lines.append(line)

        tfvars_path.write_text('\n'.join(updated_lines))
        print(f"{color('[OK]', Style.GREEN)} Updated terraform.tfvars")
    except Exception as e:
        print(f"{color('[WARNING]', Style.YELLOW)} Could not update terraform.tfvars: {e}")
