"""Terraform operations."""

import subprocess
import sys
from pathlib import Path

from fullapi.colors import color, Style


def _run_terraform_command(command: list, cwd: Path) -> int:
    """Run terraform command and return exit code."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            text=True
        )
        return result.returncode
    except FileNotFoundError:
        print(f"{color('[ERROR]', Style.RED)} Terraform not found. Install from https://www.terraform.io/downloads")
        return 1
    except Exception as e:
        print(f"{color('[ERROR]', Style.RED)} {str(e)}")
        return 1


def terraform_init():
    """Initialize Terraform."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        print(f"Run this command from your project root")
        return 1

    print(f"{color('[INFO]', Style.CYAN)} Initializing Terraform...")
    return _run_terraform_command(["terraform", "init"], terraform_dir)


def terraform_validate():
    """Validate Terraform configuration."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        return 1

    print(f"{color('[INFO]', Style.CYAN)} Validating configuration...")
    exit_code = _run_terraform_command(["terraform", "validate"], terraform_dir)

    if exit_code == 0:
        print(f"{color('[OK]', Style.GREEN)} Syntax valid")

    return exit_code


def terraform_plan():
    """Run terraform plan."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        return 1

    # Check if image URI is set
    tfvars_path = terraform_dir / "terraform.tfvars"
    if tfvars_path.exists():
        content = tfvars_path.read_text()
        if "REPLACE_WITH_IMAGE_URI" in content:
            print(f"{color('[WARNING]', Style.YELLOW)} container_image_uri not set in terraform.tfvars")
            print(f"Build and push your Docker image first:")
            print(f"  fullapi docker build")
            print(f"  fullapi docker push")
            print()

    print(f"{color('[INFO]', Style.CYAN)} Generating plan...")
    return _run_terraform_command(["terraform", "plan"], terraform_dir)


def terraform_apply():
    """Apply terraform configuration."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        return 1

    # Run validation first
    print(f"{color('[INFO]', Style.CYAN)} Validating configuration...")
    exit_code = _run_terraform_command(["terraform", "validate"], terraform_dir)

    if exit_code != 0:
        print(f"{color('[ERROR]', Style.RED)} Validation failed")
        return exit_code

    print(f"{color('[OK]', Style.GREEN)} Syntax valid")
    print()

    # Show warning
    print(f"{color('[WARNING] This will create real cloud resources. Review the plan above carefully.', Style.YELLOW)}")
    print()

    # Show plan first
    response = input("Show plan? (y/n): ").strip().lower()
    if response == 'y':
        _run_terraform_command(["terraform", "plan"], terraform_dir)
        print()

    # Confirm apply
    response = input("Apply changes? (yes/no): ").strip().lower()
    if response != 'yes':
        print(f"{color('[INFO]', Style.CYAN)} Cancelled")
        return 0

    print(f"{color('[INFO]', Style.CYAN)} Applying changes...")
    return _run_terraform_command(["terraform", "apply", "-auto-approve"], terraform_dir)


def terraform_destroy():
    """Destroy terraform-managed infrastructure."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        return 1

    print(f"{color('[WARNING] This will DESTROY all cloud resources.', Style.YELLOW)}")
    print()

    response = input("Type 'destroy' to confirm: ").strip()
    if response != 'destroy':
        print(f"{color('[INFO]', Style.CYAN)} Cancelled")
        return 0

    print(f"{color('[INFO]', Style.CYAN)} Destroying infrastructure...")
    return _run_terraform_command(["terraform", "destroy", "-auto-approve"], terraform_dir)


def terraform_output():
    """Show terraform outputs."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        return 1

    return _run_terraform_command(["terraform", "output"], terraform_dir)
