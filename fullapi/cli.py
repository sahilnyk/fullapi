"""CLI entry point for fullapi."""

import argparse
import sys
from pathlib import Path

from fullapi import __version__
from fullapi.colors import (
    ICON_ARROW, ICON_BOLT, ICON_CROSS,
    error, info, muted, success, bold, color, Style
)
from fullapi.config import ProjectConfig
from fullapi.prompt import prompt_config
from fullapi.scaffold import scaffold_project
from fullapi.add_component import add_component_to_project
from fullapi.doctor import run_doctor
from fullapi.presets import get_preset, apply_preset, list_presets
from fullapi.terraform_ops import (
    terraform_init, terraform_validate, terraform_plan,
    terraform_apply, terraform_destroy, terraform_output
)
from fullapi.docker_ops import docker_build, docker_push
from fullapi.scale_ops import scale_up, scale_down, scale_set, scale_status


def print_banner():
    """Print the fullapi banner."""
    print()
    print(f"  {ICON_BOLT} {bold('fullapi')} {muted(f'v{__version__}')}")
    print(f"  {muted('FastAPI project scaffolder')}")
    print()


def main():
    """Main entry point for the fullapi CLI."""
    parser = argparse.ArgumentParser(
        prog="fullapi",
        description="FastAPI project scaffolder — zero dependencies, one command.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fullapi new my_api                    # Interactive mode
  fullapi new my_api --basic            # Basic mode
  fullapi new my_api --full --db postgresql --auth --docker  # Full setup
  fullapi add router User               # Add User router to existing project
  fullapi add model Product             # Add Product model to existing project

For more help: fullapi new --help or fullapi add --help
        """
    )
    
    parser.add_argument(
        "-h", "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"fullapi v{__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands", description="Commands for creating FastAPI projects")
    
    # 'new' command
    new_parser = subparsers.add_parser(
        "new", 
        help="Create a new FastAPI project",
        description="Generate a complete FastAPI project structure with optional database, auth, and Docker support",
        add_help=False,
        epilog="""
Flags:
  --basic           Minimal structure (main, router, config)
  --full            Complete structure (models, CRUD, auth, DB)
  --db <type>      Database: none, sqlite, postgresql, mysql
  --auth            Add JWT authentication
  --docker          Add Docker and docker-compose
  --redis           Add Redis caching support
  --middleware       Add middleware support
  --logging         Add logging support
  --template <path> Custom template directory

Examples:
  fullapi new my_api --basic
  fullapi new my_api --full --db postgresql
  fullapi new my_api --full --db postgresql --auth --docker --redis --middleware --logging
  fullapi new my_api --template /path/to/custom/templates
        """
    )
    new_parser.add_argument("-h", "--help", action="help", help="Show help for new command")
    new_parser.add_argument("project_name", nargs="?", help="Name of the project")
    new_parser.add_argument("--basic", action="store_true", help="Basic mode, skip prompts")
    new_parser.add_argument("--full", action="store_true", help="Full mode, skip prompts")
    new_parser.add_argument("--db", choices=["none", "sqlite", "postgresql", "mysql"],
                           help="Database: none, sqlite, postgresql, mysql")
    new_parser.add_argument("--auth", action="store_true", help="Add JWT authentication")
    new_parser.add_argument("--docker", action="store_true", help="Add Docker support")
    new_parser.add_argument("--redis", action="store_true", help="Add Redis caching support")
    new_parser.add_argument("--template", type=str, help="Path to custom template directory")
    new_parser.add_argument("--middleware", action="store_true", help="Add middleware support")
    new_parser.add_argument("--logging", action="store_true", help="Add logging support")
    new_parser.add_argument("--preset", type=str, help="Use a named preset (e.g. production, microservice)")
    new_parser.add_argument("--terraform", action="store_true", help="Add Terraform infrastructure")
    
    # 'add' command
    add_parser = subparsers.add_parser(
        "add",
        help="Add components to existing project",
        description="Add routers, models, and other components to an existing fullapi project",
        add_help=False,
        epilog="""
Components:
  router <name>    Add a new router with CRUD operations
  model <name>     Add a new model with schema

Examples:
  fullapi add router User
  fullapi add model Product
        """
    )
    add_parser.add_argument("-h", "--help", action="help", help="Show help for add command")
    add_parser.add_argument("component_type", choices=["router", "model"], help="Type of component to add")
    add_parser.add_argument("component_name", help="Name of the component")

    # 'doctor' command
    subparsers.add_parser(
        "doctor",
        help="Check project health",
        description="Validate project structure and detect issues",
        add_help=False,
    )

    # 'preset' command
    preset_parser = subparsers.add_parser(
        "preset",
        help="Manage and list presets",
        description="List available presets or show preset details",
        add_help=False,
        epilog="""
Examples:
  fullapi preset list                  # List all presets
  fullapi preset show production       # Show preset details
  fullapi new my_api --preset production  # Use a preset
        """
    )
    preset_parser.add_argument("-h", "--help", action="help", help="Show help for preset command")
    preset_parser.add_argument("action", choices=["list", "show"], help="Action: list or show")
    preset_parser.add_argument("preset_name", nargs="?", help="Preset name (for show)")

    # 'terraform' command
    terraform_parser = subparsers.add_parser(
        "terraform",
        help="Terraform operations",
        description="Manage infrastructure with Terraform",
        add_help=False
    )
    terraform_parser.add_argument("-h", "--help", action="help", help="Show help for terraform command")
    terraform_parser.add_argument("action", choices=["init", "validate", "plan", "apply", "destroy", "output"],
                                  help="Terraform action")

    # 'docker' command
    docker_parser = subparsers.add_parser(
        "docker",
        help="Docker operations",
        description="Build and push Docker images",
        add_help=False
    )
    docker_parser.add_argument("-h", "--help", action="help", help="Show help for docker command")
    docker_parser.add_argument("action", choices=["build", "push"], help="Docker action")

    # 'scale' command
    scale_parser = subparsers.add_parser(
        "scale",
        help="Scale infrastructure",
        description="Scale infrastructure resources",
        add_help=False
    )
    scale_parser.add_argument("-h", "--help", action="help", help="Show help for scale command")
    scale_parser.add_argument("action", choices=["up", "down", "set", "status"], help="Scale action")
    scale_parser.add_argument("size", nargs="?", choices=["small", "medium", "large"],
                             help="Instance size (for set action)")

    args = parser.parse_args()
    
    if args.command is None:
        print_banner()
        parser.print_help()
        sys.exit(0)
    
    if args.command == "new":
        print_banner()
        handle_new(args)
    elif args.command == "add":
        print_banner()
        handle_add(args)
    elif args.command == "doctor":
        print_banner()
        handle_doctor()
    elif args.command == "preset":
        print_banner()
        handle_preset(args)
    elif args.command == "terraform":
        handle_terraform(args)
    elif args.command == "docker":
        handle_docker(args)
    elif args.command == "scale":
        handle_scale(args)


def handle_new(args):
    """Handle the 'new' command."""
    if not args.project_name:
        print(f"  {ICON_CROSS}  {error('Missing project name')}")
        print()
        print(f"  {info('Usage:')} fullapi new {bold('<project_name>')}")
        print()
        print(f"  {muted('Examples:')}")
        print(f"    fullapi new my_api          {muted('# Interactive mode')}")
        print(f"    fullapi new my_api --basic    {muted('# Basic mode')}")
        print(f"    fullapi new my_api --full --db postgresql --auth --docker")
        print()
        sys.exit(1)
    
    # Build config from preset, flags, or prompts
    if args.preset:
        preset = get_preset(args.preset)
        if not preset:
            print(f"  {ICON_CROSS}  {error(f'Unknown preset: {args.preset}')}")
            print()
            print(f"  {info('Available presets:')}")
            for name, p in list_presets().items():
                print(f"    {bold(name)} {muted('—')} {muted(p.get('description', ''))}")
            print()
            sys.exit(1)
        config = apply_preset(args.project_name, preset)
        print(f"  {info('Using preset:')} {bold(args.preset)}")
        print()
    elif args.basic or args.full:
        # CLI flags mode
        cloud_provider = None
        region = None
        instance_size = "small"

        # If terraform flag is set, prompt for cloud configuration
        if args.terraform:
            from fullapi.prompt import _prompt_choice
            print()
            cloud_provider_idx = _prompt_choice(
                "Cloud Provider",
                ["AWS", "Google Cloud (GCP)", "Azure"]
            )
            provider_map = {0: "aws", 1: "gcp", 2: "azure"}
            cloud_provider = provider_map[cloud_provider_idx]

            print()
            if cloud_provider == "aws":
                region_idx = _prompt_choice(
                    "AWS Region",
                    ["us-east-1", "us-west-2", "eu-west-1"]
                )
                regions = ["us-east-1", "us-west-2", "eu-west-1"]
            elif cloud_provider == "gcp":
                region_idx = _prompt_choice(
                    "GCP Region",
                    ["us-central1", "us-west1", "europe-west1"]
                )
                regions = ["us-central1", "us-west1", "europe-west1"]
            else:  # azure
                region_idx = _prompt_choice(
                    "Azure Region",
                    ["eastus", "westus2", "westeurope"]
                )
                regions = ["eastus", "westus2", "westeurope"]
            region = regions[region_idx]

            print()
            size_idx = _prompt_choice(
                "Instance Size",
                ["Small (1 vCPU, 2GB RAM) - $10-15/month",
                 "Medium (2 vCPU, 4GB RAM) - $25-35/month",
                 "Large (4 vCPU, 8GB RAM) - $60-80/month"]
            )
            sizes = ["small", "medium", "large"]
            instance_size = sizes[size_idx]
            print()

        config = ProjectConfig(
            name=args.project_name,
            mode="full" if args.full else "basic",
            database=args.db or "none",
            auth=args.auth,
            docker=args.docker,
            redis=args.redis,
            middleware=args.middleware,
            logging=args.logging,
            template=args.template,
            terraform=args.terraform,
            cloud_provider=cloud_provider,
            region=region,
            instance_size=instance_size
        )
    else:
        # Interactive prompt mode
        config = prompt_config(args.project_name)

    # Scaffold the project
    scaffold_project(config)


def handle_add(args):
    """Handle the 'add' command."""
    # Check if we're in a valid project directory
    if not Path("main.py").exists():
        print(f"  {ICON_CROSS}  {error('Not in a valid fullapi project directory')}")
        print()
        print(f"  {info('Requirements:')}")
        print(f"    • main.py file must exist")
        print(f"    • Run from project root directory")
        print()
        sys.exit(1)
    
    # Add the component
    add_component_to_project(args.component_type, args.component_name)


def handle_doctor():
    """Handle the 'doctor' command."""
    if not Path("main.py").exists():
        print(f"  {ICON_CROSS}  {error('Not in a valid fullapi project directory')}")
        print()
        sys.exit(1)
    run_doctor()


def handle_preset(args):
    """Handle the 'preset' command."""
    presets = list_presets()

    if args.action == "list":
        print(f"  {bold('Available Presets')}")
        print()
        for name, preset in presets.items():
            desc = preset.get("description", "")
            print(f"    {color(name, Style.CYAN)}  {muted(desc)}")
        print()
        print(f"  {muted('Usage:')} fullapi new my_api --preset <name>")
        print(f"  {muted('Custom:')} ~/.fullapi/presets.json")
        print()

    elif args.action == "show":
        if not args.preset_name:
            print(f"  {ICON_CROSS}  {error('Specify a preset name: fullapi preset show <name>')}")
            sys.exit(1)
        preset = presets.get(args.preset_name)
        if not preset:
            print(f"  {ICON_CROSS}  {error(f'Unknown preset: {args.preset_name}')}")
            sys.exit(1)
        print(f"  {bold(args.preset_name)}  {muted(preset.get('description', ''))}")
        print()
        for key, value in preset.items():
            if key == "description":
                continue
            if value is True:
                label = color("yes", Style.GREEN)
            elif value is False:
                label = muted("no")
            elif value:
                label = color(str(value), Style.CYAN)
            else:
                label = muted("none")
            print(f"    {key}: {label}")
        print()


def handle_terraform(args):
    """Handle the 'terraform' command."""
    actions = {
        "init": terraform_init,
        "validate": terraform_validate,
        "plan": terraform_plan,
        "apply": terraform_apply,
        "destroy": terraform_destroy,
        "output": terraform_output,
    }

    exit_code = actions[args.action]()
    sys.exit(exit_code)


def handle_docker(args):
    """Handle the 'docker' command."""
    actions = {
        "build": docker_build,
        "push": docker_push,
    }

    exit_code = actions[args.action]()
    sys.exit(exit_code)


def handle_scale(args):
    """Handle the 'scale' command."""
    if args.action == "up":
        exit_code = scale_up()
    elif args.action == "down":
        exit_code = scale_down()
    elif args.action == "set":
        if not args.size:
            print(f"{color('[ERROR]', Style.RED)} Size required: fullapi scale set <small|medium|large>")
            sys.exit(1)
        exit_code = scale_set(args.size)
    elif args.action == "status":
        exit_code = scale_status()
    else:
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
