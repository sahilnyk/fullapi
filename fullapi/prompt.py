"""Interactive prompts for project configuration."""

from fullapi.colors import (
    error, info, muted, bold, color, Style
)
from fullapi.config import ProjectConfig


def prompt_config(project_name: str) -> ProjectConfig:
    """Prompt user for configuration interactively."""
    print()
    print(f"  {bold('Creating project:')} {info(project_name)}")
    print()
    
    mode = _prompt_choice(
        "Mode",
        ["Minimal structure", 
         "Production-ready"]
    )
    mode = "basic" if mode == 1 else "full"
    print()
    
    database = _prompt_choice(
        "Database",
        ["No database",
         "SQLite",
         "PostgreSQL",
         "MySQL"]
    )
    db_map = {1: "none", 2: "sqlite", 3: "postgresql", 4: "mysql"}
    database = db_map[database]
    print()
    
    auth = _prompt_choice(
        "Authentication",
        ["No auth",
         "JWT authentication"]
    )
    auth = auth == 2
    print()
    
    docker = _prompt_choice(
        "Docker",
        ["Skip Docker",
         "Add Docker files"]
    )
    docker = docker == 2
    
    return ProjectConfig(
        name=project_name,
        mode=mode,
        database=database,
        auth=auth,
        docker=docker
    )


def _prompt_choice(title: str, options: list) -> int:
    """Simple numbered selection menu."""
    print(f"  {bold(title)}")
    
    for i, desc in enumerate(options, 1):
        num = color(str(i), Style.CYAN, Style.BOLD)
        print(f"    {num}. {desc}")
    
    print()
    
    while True:
        try:
            choice = input(f"  Select: ").strip()
            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(options):
                    return idx
            print(f"    {error('Invalid')} — enter 1-{len(options)}")
        except (KeyboardInterrupt, EOFError):
            print("\n  Cancelled")
            exit(0)
