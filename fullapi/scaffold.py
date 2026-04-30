"""Project scaffolding logic."""

import shutil
import sys
from pathlib import Path
from string import Template

from fullapi.config import ProjectConfig
from fullapi.colors import (
    ICON_CHECK, ICON_CROSS, ICON_WARNING, ICON_BOLT,
    success, error, warning, info, muted, bold, color, Style
)
from fullapi.templates import main_basic, router, schema, config as config_templates, requirements


def scaffold_project(config: ProjectConfig) -> None:
    """Create the project structure based on config."""
    project_path = Path(config.name)
    
    # Check if directory exists
    if project_path.exists():
        msg = f"Directory '{config.name}' already exists"
        print(f"  {ICON_WARNING}  {warning(msg)}")
        print()
        print(f"     {color('1', Style.CYAN)}) Overwrite")
        print(f"     {color('2', Style.CYAN)}) Cancel")
        
        while True:
            choice = input(f"  {color('→', Style.CYAN)} ").strip()
            if choice == "1":
                shutil.rmtree(project_path)
                break
            elif choice == "2":
                print(f"  {muted('Cancelled.')}")
                sys.exit(0)
            print(f"  {ICON_CROSS} {error('Invalid choice')}")
    
    # Collect all files to create
    files_to_create = []
    template_vars = {"project_name": config.name}
    
    if config.mode == "basic":
        _collect_basic(files_to_create, template_vars)
    else:
        _collect_full(files_to_create, config, template_vars)
    
    # Create project directory
    project_path.mkdir()
    
    print()
    print(f"  {muted('Creating project...')}")
    
    # Create all files with progress
    total = len(files_to_create)
    for i, (relative_path, content) in enumerate(files_to_create, 1):
        full_path = project_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        _show_progress(i, total, relative_path)
    
    print()
    print(f"  {ICON_CHECK}  {success('Project created successfully!')}")
    print()
    print(f"  {bold('Next steps:')}")
    print(f"    {color('cd', Style.CYAN)} {config.name}")
    print(f"    {color('pip install -r', Style.CYAN)} requirements.txt")
    print(f"    {color('uvicorn', Style.CYAN)} main:app --reload")
    print()
    print(f"  {muted('Docs:')} http://localhost:8000/docs")
    print()


def _show_progress(current: int, total: int, filename: str):
    """Show progress bar with file name."""
    width = 20
    progress = int((current / total) * width)
    
    # Colored progress bar
    filled = color("█" * progress, Style.GREEN)
    empty = color("░" * (width - progress), Style.DIM)
    bar = filled + empty
    
    percent = int((current / total) * 100)
    
    # Clear line (ANSI escape code) and show progress
    clear = "\033[K"  # Clear to end of line
    line = f"  {bar} {color(str(percent) + '%', Style.CYAN)} {muted(filename)}"
    
    print(f"\r{clear}{line}", end="", flush=True)
    if current == total:
        print()


def _collect_basic(files: list, template_vars: dict):
    """Collect files for basic mode."""
    files.append(("main.py", Template(main_basic.TEMPLATE).substitute(template_vars)))
    files.append(("routers/health.py", router.HEALTH_ROUTER))
    files.append(("schemas/base.py", schema.BASE_SCHEMA))
    files.append(("core/config.py", Template(config_templates.CONFIG_BASIC).substitute(template_vars)))
    files.append(("requirements.txt", requirements.BASIC))


def _collect_full(files: list, config: ProjectConfig, template_vars: dict):
    """Collect files for full mode."""
    files.append(("main.py", Template(main_basic.TEMPLATE).substitute(template_vars)))
    files.append(("routers/__init__.py", ""))
    files.append(("routers/health.py", router.HEALTH_ROUTER))
    files.append(("schemas/__init__.py", ""))
    files.append(("schemas/base.py", schema.BASE_SCHEMA))
    files.append(("core/__init__.py", ""))
    files.append(("core/config.py", Template(config_templates.CONFIG).substitute(template_vars)))
    files.append(("tests/test_main.py", "# TODO: Add tests\n"))
    
    if config.database != "none":
        from fullapi.templates import model, crud, database, deps
        
        files.append(("routers/users.py", router.USERS_ROUTER))
        files.append(("schemas/user.py", schema.USER_SCHEMA))
        files.append(("models/__init__.py", ""))
        files.append(("models/user.py", model.USER_MODEL))
        files.append(("crud/__init__.py", ""))
        files.append(("crud/user.py", crud.USER_CRUD))
        files.append(("db/__init__.py", ""))
        files.append(("db/session.py", Template(database.DB_SESSION).substitute({"db_type": config.database})))
        deps_content = deps.DEPS_WITH_AUTH if config.auth else deps.DEPS_NO_AUTH
        files.append(("deps.py", deps_content))
    
    if config.auth:
        from fullapi.templates import security
        files.append(("core/security.py", security.SECURITY))
    
    req_content = requirements.FULL
    if config.database == "postgresql":
        req_content += requirements.FULL_POSTGRESQL
    elif config.database == "mysql":
        req_content += requirements.FULL_MYSQL
    if config.auth:
        req_content += requirements.FULL_AUTH
    files.append(("requirements.txt", req_content))
    
    from fullapi.templates import env
    files.append((".env.example", env.ENV_EXAMPLE))
    
    if config.docker:
        from fullapi.templates import dockerfile, dockercompose
        files.append(("Dockerfile", dockerfile.DOCKERFILE))
        files.append(("docker-compose.yml", dockercompose.DOCKERCOMPOSE))
