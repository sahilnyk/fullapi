"""CLI entry point for fullapi."""

import argparse
import sys

from fullapi import __version__
from fullapi.colors import (
    ICON_ARROW, ICON_BOLT, ICON_CROSS, 
    error, info, muted, success, bold, color, Style
)
from fullapi.config import ProjectConfig
from fullapi.prompt import prompt_config
from fullapi.scaffold import scaffold_project


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
        add_help=False
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
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # 'new' command
    new_parser = subparsers.add_parser(
        "new", 
        help="Create a new FastAPI project",
        add_help=False
    )
    new_parser.add_argument("-h", "--help", action="help", help="Show help for new command")
    new_parser.add_argument("project_name", nargs="?", help="Name of the project")
    new_parser.add_argument("--basic", action="store_true", help="Basic mode, skip prompts")
    new_parser.add_argument("--full", action="store_true", help="Full mode, skip prompts")
    new_parser.add_argument("--db", choices=["none", "sqlite", "postgresql", "mysql"],
                           help="Database: none, sqlite, postgresql, mysql")
    new_parser.add_argument("--auth", action="store_true", help="Add JWT authentication")
    new_parser.add_argument("--docker", action="store_true", help="Add Docker support")
    
    args = parser.parse_args()
    
    if args.command is None:
        print_banner()
        parser.print_help()
        sys.exit(0)
    
    if args.command == "new":
        print_banner()
        handle_new(args)


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
            docker=args.docker
        )
    else:
        # Interactive prompt mode
        config = prompt_config(args.project_name)
    
    # Scaffold the project
    scaffold_project(config)


if __name__ == "__main__":
    main()
