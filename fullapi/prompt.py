"""Interactive prompts for project configuration."""

from fullapi.colors import (
    ICON_ARROW, ICON_CROSS, 
    error, info, muted, bold, color, Style
)
from fullapi.config import ProjectConfig


def prompt_config(project_name: str) -> ProjectConfig:
    """Prompt user for configuration interactively."""
    print(f"  {bold('Creating project:')} {info(project_name)}")
    print()
    
    mode = _prompt_choice(
        "Mode",
        ["Minimal structure (good for small APIs)", 
         "Production-ready (models, CRUD, auth, DB)"]
    )
    mode = "basic" if mode == 1 else "full"
    
    database = _prompt_choice(
        "Database",
        ["No database",
         "SQLite (embedded, good for dev)",
         "PostgreSQL (production ready)",
         "MySQL"]
    )
    db_map = {1: "none", 2: "sqlite", 3: "postgresql", 4: "mysql"}
    database = db_map[database]
    
    auth_choice = _prompt_choice(
        "Authentication",
        ["No auth",
         "JWT token authentication"]
    )
    auth = auth_choice == 2
    
    docker_choice = _prompt_choice(
        "Docker",
        ["Skip Docker",
         "Add Dockerfile and docker-compose.yml"]
    )
    docker = docker_choice == 2
    
    return ProjectConfig(
        name=project_name,
        mode=mode,
        database=database,
        auth=auth,
        docker=docker
    )


def _prompt_choice(title: str, options: list) -> int:
    """Prompt user to select from options. Returns 1-based index."""
    print(f"  {bold(title)}")
    for i, desc in enumerate(options, 1):
        num = color(str(i), Style.CYAN, Style.BOLD)
        print(f"    {num}. {desc}")
    print()
    
    while True:
        prompt = color("?", Style.GREEN, Style.BOLD)
        choice = input(f"  {prompt} {bold(title)}: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print(f"    {ICON_CROSS} {error('Invalid choice')} — enter 1-{len(options)}")
        print()
