"""Project scaffolding logic."""

import shutil
import sys
import time
from pathlib import Path
from string import Template

from fullapi.config import ProjectConfig
from fullapi.colors import (
    ICON_CHECK, ICON_CROSS, ICON_WARNING, ICON_BOLT,
    success, error, warning, info, muted, bold, color, Style
)
from fullapi.templates import main_basic, router, schema, config as config_templates, requirements, alembic, redis, middleware, logging as logging_templates
from fullapi.custom_templates import load_custom_template, CustomTemplateManager
from fullapi.metadata import write_metadata
from fullapi.prompt import show_loading_animation


def _get_database_url(db_type: str) -> str:
    """Get database URL for Alembic configuration."""
    if db_type == "sqlite":
        return "sqlite:///./app.db"
    elif db_type == "postgresql":
        return "postgresql://user:password@localhost:5432/app"
    elif db_type == "mysql":
        return "mysql+pymysql://root:password@localhost:3306/app"
    else:
        return "sqlite:///./app.db"


def _scaffold_with_custom_template(config: ProjectConfig, project_path: Path) -> None:
    """Scaffold project using custom templates."""
    custom_template = load_custom_template(config.template)
    if not custom_template:
        error_msg = error('Failed to load custom templates')
        print(f"  {ICON_CROSS}  {error_msg}")
        return
    
    if not custom_template.validate_template_structure():
        return
    
    print()
    info_msg = info(config.template)
    print(f"  {bold('Using custom templates from:')} {info_msg}")
    print()
    
    # Get all template files
    template_files = custom_template.get_template_files()
    template_vars = {"project_name": config.name}
    
    # Create project directory
    project_path.mkdir()
    
    # Show loading animation
    show_loading_animation("Initializing custom template project", 0.8)
    
    # Create all files with progress
    total = len(template_files)
    
    for i, (relative_path, content) in enumerate(template_files.items(), 1):
        # Apply template substitution for .py files
        if relative_path.endswith('.py'):
            content = Template(content).substitute(template_vars)
        
        full_path = project_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        _show_progress(i, total, relative_path)
    
    # Write project metadata
    write_metadata(project_path, config)

    print()
    show_loading_animation("Finalizing custom template project", 0.5)

    success_msg = success('Project created successfully!')
    print(f"  {ICON_CHECK}  {success_msg}")
    print()
    print(f"  {bold('Next steps:')}")
    print(f"    {color('cd', Style.CYAN)} {config.name}")
    print(f"    {color('pip install -r', Style.CYAN)} requirements.txt")
    print(f"    {color('uvicorn', Style.CYAN)} main:app --reload")
    print()
    docs_msg = muted('Docs: http://localhost:8000/docs')
    print(f"  {docs_msg}")
    print()


def scaffold_project(config: ProjectConfig) -> None:
    """Create the project structure based on config."""
    project_path = Path(config.name)
    
    # Handle custom templates
    if config.template:
        return _scaffold_with_custom_template(config, project_path)
    
    # Continue with built-in templates
    
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
    
    # Show loading animation before starting
    show_loading_animation("Initializing project structure", 0.8)
    
    # Create all files with progress
    total = len(files_to_create)
    
    for i, (relative_path, content) in enumerate(files_to_create, 1):
        full_path = project_path / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        _show_progress(i, total, relative_path)
    
    # Write project metadata
    write_metadata(project_path, config)

    print()
    show_loading_animation("Finalizing project setup", 0.5)

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
    """Render progress bar with file name."""
    width = 20
    progress = int((current / total) * width)
    
    filled = color("█" * progress, Style.GREEN)
    empty = color("░" * (width - progress), Style.DIM)
    bar = filled + empty
    
    percent = int((current / total) * 100)
    
    clear = "\033[K"  # Clear to end of line
    line = f"  {bar} {color(str(percent) + '%', Style.CYAN)} {muted(filename)}"
    
    print(f"\r{clear}{line}", end="", flush=True)
    
    if current == total:
        print()
    else:
        time.sleep(0.05)


def _collect_basic(files: list, template_vars: dict):
    """Collect files for basic mode."""
    files.append(("main.py", Template(main_basic.TEMPLATE).substitute(template_vars)))
    files.append(("routers/health.py", router.HEALTH_ROUTER))
    files.append(("schemas/base.py", schema.BASE_SCHEMA))
    files.append(("core/config.py", Template(config_templates.CONFIG_BASIC).substitute(template_vars)))
    files.append(("requirements.txt", requirements.BASIC))


def _build_full_main(config: ProjectConfig, template_vars: dict) -> str:
    """Build main.py content for full mode with proper imports."""
    imports = ["from fastapi import FastAPI"]
    imports.append("from routers.health import router as health_router")

    routers = ['app.include_router(health_router, tags=["health"])']

    if config.database != "none":
        imports.append("from routers.users import router as users_router")
        routers.append('app.include_router(users_router, prefix="/users", tags=["users"])')

    if config.redis:
        imports.append("from routers.redis import router as redis_router")
        routers.append('app.include_router(redis_router, prefix="/redis", tags=["redis"])')

    name = template_vars["project_name"]
    lines = imports + ["", f'app = FastAPI(title="{name}")', ""] + routers
    lines += ["", "", 'if __name__ == "__main__":',
              "    import uvicorn",
              '    uvicorn.run(app, host="0.0.0.0", port=8000)',
              ""]
    return "\n".join(lines)


def _collect_full(files: list, config: ProjectConfig, template_vars: dict):
    """Collect files for full mode."""
    files.append(("main.py", _build_full_main(config, template_vars)))
    files.append(("routers/__init__.py", ""))
    files.append(("routers/health.py", router.HEALTH_ROUTER))
    files.append(("schemas/__init__.py", ""))
    files.append(("schemas/base.py", schema.BASE_SCHEMA))
    files.append(("core/__init__.py", ""))
    files.append(("core/config.py", Template(config_templates.CONFIG).substitute(template_vars)))
    files.append(("tests/test_main.py", "# TODO: Add tests\n"))
    
    if config.database != "none":
        from fullapi.templates import model, crud, database, deps, alembic
        
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
        
        # Add Alembic migration support
        db_url = _get_database_url(config.database)
        files.append(("alembic.ini", Template(alembic.ALEMBIC_INI).substitute({"database_url": db_url})))
        files.append(("alembic/env.py", alembic.ENV_PY))
        files.append(("alembic/script.py.mako", alembic.SCRIPT_PY_MAKO))
        files.append(("alembic/versions/__init__.py", ""))
        
        # Add initial migration
        import datetime
        create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_migration = Template(alembic.INITIAL_MIGRATION).substitute({"create_date": create_date})
        files.append(("alembic/versions/001_initial_migration.py", initial_migration))
    
    if config.auth:
        from fullapi.templates import security
        files.append(("core/security.py", security.SECURITY))
    
    if config.redis:
        files.append(("core/redis_config.py", redis.REDIS_CONFIG))
        files.append(("core/redis_utils.py", redis.REDIS_UTILS))
        files.append(("routers/redis.py", redis.REDIS_ROUTER))
        files.append(("deps_redis.py", redis.REDIS_DEPS))
    
    if config.middleware:
        files.append(("core/middleware_config.py", middleware.MIDDLEWARE_CONFIG))
        files.append(("core/middleware_cors.py", middleware.MIDDLEWARE_CORS))
        files.append(("core/middleware_rate_limit.py", middleware.MIDDLEWARE_RATE_LIMIT))
        files.append(("core/middleware_security.py", middleware.MIDDLEWARE_SECURITY))
        files.append(("core/middleware_gzip.py", middleware.MIDDLEWARE_GZIP))
        files.append(("core/middleware_logging.py", middleware.MIDDLEWARE_LOGGING))
        files.append(("core/middleware_trusted_proxy.py", middleware.MIDDLEWARE_TRUSTED_PROXY))
        files.append(("core/middleware_setup.py", middleware.MIDDLEWARE_SETUP))
        files.append(("main_with_middleware.py", middleware.MIDDLEWARE_MAIN))
    
    if config.logging:
        files.append(("core/logging_config.py", logging_templates.LOGGING_CONFIG))
        files.append(("core/logging_setup.py", logging_templates.LOGGING_SETUP))
    
    req_content = requirements.FULL
    if config.database == "postgresql":
        req_content += requirements.FULL_POSTGRESQL
    elif config.database == "mysql":
        req_content += requirements.FULL_MYSQL
    if config.auth:
        req_content += requirements.FULL_AUTH
    if config.database != "none":
        req_content += alembic.REQUIREMENTS_ALEMBIC
    if config.redis:
        req_content += redis.REQUIREMENTS_REDIS
    if config.middleware:
        req_content += middleware.REQUIREMENTS_MIDDLEWARE
    if config.logging:
        req_content += logging_templates.REQUIREMENTS_LOGGING
    files.append(("requirements.txt", req_content))
    
    from fullapi.templates import env
    files.append((".env.example", env.ENV_EXAMPLE))
    
    if config.docker:
        from fullapi.templates import dockerfile, dockercompose
        files.append(("Dockerfile", dockerfile.DOCKERFILE))
        files.append(("docker-compose.yml", dockercompose.DOCKERCOMPOSE))
