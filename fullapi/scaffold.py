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
from fullapi.templates import terraform as terraform_templates
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

    # Generate Terraform files if requested
    if config.terraform:
        _generate_terraform_files(project_path, config)

    print()
    show_loading_animation("Finalizing project setup", 0.5)

    print(f"  {ICON_CHECK}  {success('Project created successfully!')}")
    print()

    # Show Terraform warning if enabled
    if config.terraform:
        print(f"  {color('[WARNING] Cross-validate Terraform files before applying', Style.YELLOW)}")
        print()

    print(f"  {bold('Next steps:')}")
    print(f"    {color('cd', Style.CYAN)} {config.name}")
    print(f"    {color('pip install -r', Style.CYAN)} requirements.txt")
    if config.terraform:
        print(f"    {color('fullapi terraform init', Style.CYAN)}")
        print(f"    {color('fullapi terraform plan', Style.CYAN)}")
    print(f"    {color('uvicorn', Style.CYAN)} main:app --reload")
    print()
    print(f"  {muted('Docs:')} http://localhost:8000/docs")
    print()


def _generate_terraform_files(project_path: Path, config: ProjectConfig):
    """Generate Terraform configuration files."""
    terraform_dir = project_path / "terraform"
    terraform_dir.mkdir(exist_ok=True)

    enable_database = config.database != "none"
    enable_cache = config.redis

    # Generate main.tf
    main_tf_content = terraform_templates.main_tf(
        config.name,
        config.cloud_provider,
        enable_database,
        enable_cache
    )
    (terraform_dir / "main.tf").write_text(main_tf_content)

    # Generate variables.tf
    variables_tf_content = terraform_templates.variables_tf(
        config.cloud_provider,
        enable_database,
        enable_cache
    )
    (terraform_dir / "variables.tf").write_text(variables_tf_content)

    # Generate outputs.tf
    outputs_tf_content = terraform_templates.outputs_tf(
        enable_database,
        enable_cache
    )
    (terraform_dir / "outputs.tf").write_text(outputs_tf_content)

    # Generate terraform.tfvars
    tfvars_content = terraform_templates.terraform_tfvars(config)
    (terraform_dir / "terraform.tfvars").write_text(tfvars_content)

    # Generate README
    readme_content = terraform_templates.readme_terraform()
    (terraform_dir / "README.md").write_text(readme_content)

    # Update .gitignore
    gitignore_path = project_path / ".gitignore"
    if gitignore_path.exists():
        current = gitignore_path.read_text()
        gitignore_path.write_text(current + terraform_templates.gitignore_additions())
    else:
        gitignore_path.write_text(terraform_templates.gitignore_additions())


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
    
    # Build requirements as a set to avoid duplicates
    req_lines = set()

    # Add base requirements
    for line in requirements.FULL_BASE.strip().split('\n'):
        if line.strip():
            req_lines.add(line.strip())

    # Add database-specific requirements
    if config.database == "postgresql":
        for line in requirements.FULL_POSTGRESQL.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())
    elif config.database == "mysql":
        for line in requirements.FULL_MYSQL.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())

    # Add auth requirements
    if config.auth:
        for line in requirements.FULL_AUTH.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())

    # Add alembic requirements
    if config.database != "none":
        for line in alembic.REQUIREMENTS_ALEMBIC.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())

    # Add redis requirements
    if config.redis:
        for line in redis.REQUIREMENTS_REDIS.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())

    # Add middleware requirements
    if config.middleware:
        for line in middleware.REQUIREMENTS_MIDDLEWARE.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())

    # Add logging requirements (if any)
    if config.logging and hasattr(logging_templates, 'REQUIREMENTS_LOGGING'):
        for line in logging_templates.REQUIREMENTS_LOGGING.strip().split('\n'):
            if line.strip():
                req_lines.add(line.strip())

    # Sort and join, filtering out comments
    req_lines = {line for line in req_lines if not line.startswith('#')}
    req_content = '\n'.join(sorted(req_lines)) + '\n'
    files.append(("requirements.txt", req_content))
    
    from fullapi.templates import env
    files.append((".env.example", env.ENV_EXAMPLE))
    
    if config.docker:
        from fullapi.templates import dockerfile, dockercompose
        files.append(("Dockerfile", dockerfile.DOCKERFILE))
        files.append(("docker-compose.yml", dockercompose.DOCKERCOMPOSE))
