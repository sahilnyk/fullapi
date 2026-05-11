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
    
    # Build config from flags or prompts
    if args.basic or args.full:
        # CLI flags mode
        config = ProjectConfig(
            name=args.project_name,
            mode="full" if args.full else "basic",
            database=args.db or "none",
            auth=args.auth,
            docker=args.docker,
            redis=args.redis,
            middleware=args.middleware,
            logging=args.logging,
            template=args.template
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


if __name__ == "__main__":
    main()
