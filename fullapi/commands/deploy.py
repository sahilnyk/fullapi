"""Main deploy command orchestration."""

import subprocess
from pathlib import Path

from fullapi.analyzers.codebase import CodebaseAnalyzer
from fullapi.deployers.planner import DeploymentPlanner
from fullapi.deployers.docker_builder import DockerBuilder
from fullapi.deployers.terraform_gen import TerraformGenerator
from fullapi.deployers.terraform_apply import TerraformApplier
from fullapi.colors import ICON_CHECK, ICON_CROSS, bold, error, info


def deploy_project(
    project_path: Path,
    cloud_provider: str,
    deployment_type: str,
    app_name: str,
    region: str = "us-east-1"
) -> bool:
    """Deploy a FastAPI project to cloud infrastructure.

    Args:
        project_path: Path to the project directory
        cloud_provider: Cloud provider (aws, gcp, azure)
        deployment_type: Deployment type (server, serverless)
        app_name: Name for the application
        region: Cloud region (default: us-east-1 for AWS)

    Returns:
        bool: True if deployment succeeded, False otherwise
    """
    try:
        # Step 1: Analyze codebase
        print()
        print(f"  {info('Step 1/6: Analyzing codebase...')}")
        analyzer = CodebaseAnalyzer(project_path)
        analysis = analyzer.analyze()
        print(f"  {ICON_CHECK}  Codebase analyzed")

        # Step 2: Create deployment plan
        print()
        print(f"  {info('Step 2/6: Creating deployment plan...')}")
        planner = DeploymentPlanner(
            analysis, app_name, cloud_provider, deployment_type, region
        )
        spec = planner.create_spec()
        planner.show_summary()
        print(f"  {ICON_CHECK}  Deployment plan created")

        # Step 3: Get user confirmation
        print()
        print(f"  {info('Step 3/6: Waiting for confirmation...')}")
        if not planner.get_confirmation():
            print(f"  {ICON_CROSS}  Deployment cancelled by user")
            print()
            return False
        print(f"  {ICON_CHECK}  Confirmed")

        # Step 4: Build and push Docker image
        print()
        print(f"  {info('Step 4/6: Building and pushing Docker image...')}")
        builder = DockerBuilder(
            app_name,
            cloud_provider,
            region,
            spec.dockerfile_path
        )
        image_uri = builder.build_and_push(project_path, spec.port)
        spec.image_uri = image_uri
        print(f"  {ICON_CHECK}  Docker image ready")

        # Step 5: Generate terraform files
        print()
        print(f"  {info('Step 5/6: Generating Terraform configuration...')}")
        generator = TerraformGenerator(spec)
        generator.generate(project_path, image_uri)
        print(f"  {ICON_CHECK}  Terraform files generated")

        # Step 6: Apply terraform
        print()
        print(f"  {info('Step 6/6: Deploying infrastructure...')}")
        terraform_dir = project_path / "terraform"
        applier = TerraformApplier(terraform_dir)

        print(f"    Initializing Terraform...")
        applier.init()
        print(f"  {ICON_CHECK}  Terraform initialized")

        print(f"    Planning changes...")
        applier.plan()
        print(f"  {ICON_CHECK}  Plan complete")

        print(f"    Applying changes...")
        applier.apply()
        print(f"  {ICON_CHECK}  Infrastructure deployed")

        # Success
        print()
        print(f"  {bold('Deployment complete!')}")
        print()
        return True

    except RuntimeError as e:
        # Handle expected errors (Docker build/push failures)
        print()
        print(f"  {ICON_CROSS}  {error(f'Deployment failed: {str(e)}')}")
        print()
        return False

    except subprocess.CalledProcessError as e:
        # Handle terraform command failures
        print()
        print(f"  {ICON_CROSS}  {error(f'Terraform command failed: {e.cmd}')}")
        if e.stderr:
            print(f"    {error(e.stderr)}")
        print()
        return False

    except Exception as e:
        # Handle unexpected errors
        print()
        print(f"  {ICON_CROSS}  {error(f'Unexpected error: {str(e)}')}")
        print()
        return False
