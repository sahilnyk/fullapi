"""Scaling operations for infrastructure."""

import subprocess
from pathlib import Path

from fullapi.colors import color, Style


# Instance size tiers and their cost estimates
SIZE_TIERS = {
    "small": {"cpu": "1 vCPU", "ram": "2GB", "cost": "$10-15/month"},
    "medium": {"cpu": "2 vCPU", "ram": "4GB", "cost": "$25-35/month"},
    "large": {"cpu": "4 vCPU", "ram": "8GB", "cost": "$60-80/month"},
}

SIZE_ORDER = ["small", "medium", "large"]


def _get_current_size() -> str:
    """Get current instance size from terraform.tfvars."""
    tfvars_path = Path.cwd() / "terraform" / "terraform.tfvars"

    if not tfvars_path.exists():
        return None

    try:
        content = tfvars_path.read_text()
        for line in content.split('\n'):
            if line.strip().startswith('instance_size'):
                # Extract value between quotes
                parts = line.split('=')
                if len(parts) == 2:
                    value = parts[1].strip().strip('"').strip("'")
                    return value
    except Exception:
        pass

    return None


def _update_size(new_size: str) -> bool:
    """Update instance_size in terraform.tfvars."""
    tfvars_path = Path.cwd() / "terraform" / "terraform.tfvars"

    if not tfvars_path.exists():
        return False

    try:
        content = tfvars_path.read_text()
        lines = content.split('\n')
        updated_lines = []

        for line in lines:
            if line.strip().startswith('instance_size'):
                updated_lines.append(f'instance_size      = "{new_size}"')
            else:
                updated_lines.append(line)

        tfvars_path.write_text('\n'.join(updated_lines))
        return True
    except Exception:
        return False


def _run_terraform_apply() -> int:
    """Run terraform apply."""
    terraform_dir = Path.cwd() / "terraform"

    try:
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve"],
            cwd=terraform_dir,
            check=False
        )
        return result.returncode
    except Exception:
        return 1


def scale_up():
    """Scale up instance size."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        print("Create project with --terraform flag")
        return 1

    current = _get_current_size()
    if not current:
        print(f"{color('[ERROR]', Style.RED)} Could not read current size")
        return 1

    if current not in SIZE_ORDER:
        print(f"{color('[ERROR]', Style.RED)} Unknown current size: {current}")
        return 1

    current_index = SIZE_ORDER.index(current)
    if current_index >= len(SIZE_ORDER) - 1:
        print(f"{color('[INFO]', Style.CYAN)} Already at maximum size: {current}")
        return 0

    new_size = SIZE_ORDER[current_index + 1]
    return _scale_to(current, new_size)


def scale_down():
    """Scale down instance size."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        print("Create project with --terraform flag")
        return 1

    current = _get_current_size()
    if not current:
        print(f"{color('[ERROR]', Style.RED)} Could not read current size")
        return 1

    if current not in SIZE_ORDER:
        print(f"{color('[ERROR]', Style.RED)} Unknown current size: {current}")
        return 1

    current_index = SIZE_ORDER.index(current)
    if current_index <= 0:
        print(f"{color('[INFO]', Style.CYAN)} Already at minimum size: {current}")
        return 0

    new_size = SIZE_ORDER[current_index - 1]
    return _scale_to(current, new_size)


def scale_set(size: str):
    """Set specific instance size."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        print("Create project with --terraform flag")
        return 1

    if size not in SIZE_TIERS:
        print(f"{color('[ERROR]', Style.RED)} Invalid size: {size}")
        print(f"Valid sizes: {', '.join(SIZE_ORDER)}")
        return 1

    current = _get_current_size()
    if not current:
        print(f"{color('[ERROR]', Style.RED)} Could not read current size")
        return 1

    if current == size:
        print(f"{color('[INFO]', Style.CYAN)} Already at size: {size}")
        return 0

    return _scale_to(current, size)


def scale_status():
    """Show current scaling status."""
    terraform_dir = Path.cwd() / "terraform"

    if not terraform_dir.exists():
        print(f"{color('[ERROR]', Style.RED)} No terraform/ directory found")
        return 1

    current = _get_current_size()
    if not current:
        print(f"{color('[ERROR]', Style.RED)} Could not read current size")
        return 1

    if current not in SIZE_TIERS:
        print(f"{color('[ERROR]', Style.RED)} Unknown size: {current}")
        return 1

    tier = SIZE_TIERS[current]

    print()
    print(f"Current tier: {color(current, Style.GREEN)}")
    print(f"  CPU:  {tier['cpu']}")
    print(f"  RAM:  {tier['ram']}")
    print(f"  Cost: {tier['cost']}")
    print()

    print("Available tiers:")
    for size_name in SIZE_ORDER:
        tier = SIZE_TIERS[size_name]
        marker = " (current)" if size_name == current else ""
        print(f"  {size_name:8} {tier['cpu']:8} {tier['ram']:6} {tier['cost']:16}{marker}")
    print()

    return 0


def _scale_to(current: str, new_size: str) -> int:
    """Scale from current to new size."""
    current_tier = SIZE_TIERS[current]
    new_tier = SIZE_TIERS[new_size]

    # Calculate cost change
    current_cost_mid = _parse_cost(current_tier['cost'])
    new_cost_mid = _parse_cost(new_tier['cost'])
    cost_diff = new_cost_mid - current_cost_mid
    cost_sign = "+" if cost_diff > 0 else ""

    print()
    print(f"{color('[INFO]', Style.CYAN)} Current tier: {current}")
    print(f"{color('[INFO]', Style.CYAN)} New tier: {new_size}")
    print(f"{color('[INFO]', Style.CYAN)} Cost change: {cost_sign}${abs(cost_diff):.0f}/month")
    print()
    print("This will:")
    print("  - Update instance_size variable")
    print("  - Run terraform apply")
    print("  - Restart containers with new resources")
    print()

    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print(f"{color('[INFO]', Style.CYAN)} Cancelled")
        return 0

    # Update tfvars
    if not _update_size(new_size):
        print(f"{color('[ERROR]', Style.RED)} Failed to update terraform.tfvars")
        return 1

    print(f"{color('[OK]', Style.GREEN)} Updated terraform.tfvars")
    print()

    # Run terraform apply
    print(f"{color('[INFO]', Style.CYAN)} Applying changes...")
    exit_code = _run_terraform_apply()

    if exit_code == 0:
        print()
        print(f"{color('[OK]', Style.GREEN)} Scaled to {new_size}")
    else:
        print()
        print(f"{color('[ERROR]', Style.RED)} Terraform apply failed")

    return exit_code


def _parse_cost(cost_str: str) -> float:
    """Parse cost string like '$10-15/month' to midpoint value."""
    # Extract numbers from string like "$10-15/month"
    numbers = [int(s) for s in cost_str.split() if any(c.isdigit() for c in s)]
    if len(numbers) >= 2:
        return (numbers[0] + numbers[1]) / 2.0
    elif len(numbers) == 1:
        return float(numbers[0])
    return 0.0
