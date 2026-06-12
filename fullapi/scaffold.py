"""Project scaffolding logic with new architecture."""

import shutil
import sys
import time
from pathlib import Path
from string import Template
from datetime import datetime

from fullapi.config import ProjectConfig
from fullapi.colors import (
    ICON_CHECK, ICON_CROSS, ICON_WARNING, success, error, warning, info, muted, bold, color, Style
)
from fullapi.templates import (
    main_basic, router, schema,
    requirements, alembic, redis,
    terraform as terraform_templates
)
# Import new template modules
from fullapi.templates import (
    exceptions as exceptions_templates,
    responses as responses_templates,
    mixins as mixins_templates,
    crud_base as crud_base_templates,
    dependencies as dependencies_templates,
    middleware_new as middleware_new_templates,
    logging_new as logging_new_templates,
    main_full as main_full_templates,
    config_new as config_new_templates,
    routers_new as routers_new_templates,
    tests_new as tests_new_templates,
)
from fullapi.custom_templates import load_custom_template
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
    # Main application file
    files.append(("main.py", Template(main_basic.TEMPLATE).substitute(template_vars)))
    
    # Routers
    files.append(("routers/__init__.py", ""))
    files.append(("routers/health.py", router.HEALTH_ROUTER))
    
    # Schemas
    files.append(("schemas/__init__.py", ""))
    files.append(("schemas/base.py", schema.BASE_SCHEMA))
    
    # Core configuration (new version)
    files.append(("core/__init__.py", ""))
    files.append(("core/config.py", Template(config_new_templates.CONFIG_BASIC).substitute(template_vars)))
    files.append(("core/responses.py", responses_templates.RESPONSES))
    
    # Exceptions package
    files.append(("exceptions/__init__.py", exceptions_templates.EXCEPTIONS_INIT))
    files.append(("exceptions/errors.py", exceptions_templates.EXCEPTIONS_ERRORS))
    files.append(("exceptions/handlers.py", exceptions_templates.EXCEPTIONS_HANDLERS))
    
    # Requirements
    files.append(("requirements.txt", requirements.BASIC))
    
    # Environment files
    files.append((".env.example", "# Application\nAPP_NAME=${project_name}\nDEBUG=true\nENVIRONMENT=development\n"))
    files.append((".gitignore", _generate_gitignore()))


def _collect_full(files: list, config: ProjectConfig, template_vars: dict):
    """Collect files for full mode with new architecture."""
    # Main application file (built dynamically)
    main_content = main_full_templates.build_main_py(
        project_name=template_vars["project_name"],
        has_logging=config.logging,
        has_middleware=config.middleware,
        has_exceptions=True,  # Always include in full mode
        has_database=(config.database != "none"),
        has_redis=config.redis,
        has_auth=config.auth,
    )
    files.append(("main.py", main_content))
    
    # Core package
    files.append(("core/__init__.py", ""))
    files.append(("core/config.py", Template(config_new_templates.CONFIG).substitute(template_vars)))
    files.append(("core/responses.py", responses_templates.RESPONSES))
    
    # Exceptions package
    files.append(("exceptions/__init__.py", exceptions_templates.EXCEPTIONS_INIT))
    files.append(("exceptions/errors.py", exceptions_templates.EXCEPTIONS_ERRORS))
    files.append(("exceptions/handlers.py", exceptions_templates.EXCEPTIONS_HANDLERS))
    
    # Routers
    files.append(("routers/__init__.py", ""))
    if config.database != "none":
        files.append(("routers/health.py", routers_new_templates.HEALTH_ROUTER))
    else:
        files.append(("routers/health.py", routers_new_templates.HEALTH_ROUTER_NO_DB))
    
    # Schemas
    files.append(("schemas/__init__.py", ""))
    files.append(("schemas/base.py", schema.BASE_SCHEMA))
    
    # Database-specific files
    if config.database != "none":
        from fullapi.templates import model, crud, database, alembic
        
        # Database models and mixins
        files.append(("db/__init__.py", ""))
        files.append(("db/base.py", database.DB_BASE))
        files.append(("db/mixins.py", mixins_templates.DB_MIXINS))
        if config.database == "sqlite":
            files.append(("db/session.py", database.DB_SESSION_SQLITE))
        else:
            files.append(("db/session.py", database.DB_SESSION_POSTGRESQL_MYSQL))
        
        # Models
        files.append(("models/__init__.py", "from .user import User\n"))
        files.append(("models/user.py", model.USER_MODEL))
        
        # CRUD layer
        files.append(("crud/__init__.py", ""))
        files.append(("crud/base.py", crud_base_templates.CRUD_BASE))
        files.append(("crud/user.py", crud.USER_CRUD))
        
        # Dependencies package
        if config.auth:
            files.append(("dependencies/__init__.py", dependencies_templates.DEPENDENCIES_INIT_AUTH_ONLY))
        else:
            files.append(("dependencies/__init__.py", dependencies_templates.DEPENDENCIES_INIT_NO_AUTH))
        files.append(("dependencies/db.py", dependencies_templates.DEPENDENCIES_DB))
        
        # Auth-specific dependencies
        if config.auth:
            files.append(("dependencies/auth.py", dependencies_templates.DEPENDENCIES_AUTH))
        
        # User router and schema
        if config.auth:
            files.append(("routers/users.py", routers_new_templates.USERS_ROUTER))
        else:
            files.append(("routers/users.py", routers_new_templates.USERS_ROUTER_NO_AUTH))
        files.append(("schemas/user.py", schema.USER_SCHEMA))
        
        # Auth router
        if config.auth:
            files.append(("routers/auth.py", routers_new_templates.AUTH_ROUTER))
            files.append(("schemas/auth.py", _generate_auth_schema()))
        
        # Alembic migration support
        db_url = _get_database_url(config.database)
        files.append(("alembic.ini", Template(alembic.ALEMBIC_INI).substitute({"database_url": db_url})))
        files.append(("alembic/env.py", alembic.ENV_PY))
        files.append(("alembic/script.py.mako", alembic.SCRIPT_PY_MAKO))
        files.append(("alembic/versions/__init__.py", ""))
        
        # Initial migration
        create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_migration = Template(alembic.INITIAL_MIGRATION).substitute({"create_date": create_date})
        files.append(("alembic/versions/001_initial_migration.py", initial_migration))
    else:
        # No database - simple dependencies
        files.append(("dependencies/__init__.py", '"""Dependencies package."""\n'))
    
    # Security module
    if config.auth:
        from fullapi.templates import security
        files.append(("core/security.py", security.SECURITY))
    
    # Redis support
    if config.redis:
        files.append(("core/redis_config.py", redis.REDIS_CONFIG))
        files.append(("core/redis_utils.py", redis.REDIS_UTILS))
        files.append(("routers/redis.py", routers_new_templates.REDIS_ROUTER))
        files.append(("dependencies/cache.py", dependencies_templates.DEPENDENCIES_CACHE))
        
        # Update dependencies __init__.py to include cache
        if config.database != "none":
            if config.auth:
                files.append(("dependencies/__init__.py", dependencies_templates.DEPENDENCIES_INIT))
            else:
                files.append(("dependencies/__init__.py", dependencies_templates.DEPENDENCIES_INIT_REDIS_ONLY))
    
    # Middleware (new structure)
    if config.middleware:
        files.append(("core/middleware/__init__.py", middleware_new_templates.MIDDLEWARE_INIT))
        files.append(("core/middleware/config.py", middleware_new_templates.MIDDLEWARE_CONFIG))
        files.append(("core/middleware/cors.py", middleware_new_templates.MIDDLEWARE_CORS))
        files.append(("core/middleware/rate_limit.py", middleware_new_templates.MIDDLEWARE_RATE_LIMIT))
        files.append(("core/middleware/security_headers.py", middleware_new_templates.MIDDLEWARE_SECURITY_HEADERS))
        files.append(("core/middleware/gzip.py", middleware_new_templates.MIDDLEWARE_GZIP))
        files.append(("core/middleware/request_id.py", middleware_new_templates.MIDDLEWARE_REQUEST_ID))
        files.append(("core/middleware/request_logging.py", middleware_new_templates.MIDDLEWARE_REQUEST_LOGGING))
        files.append(("core/middleware/setup.py", middleware_new_templates.MIDDLEWARE_SETUP))
    
    # Logging (new structure)
    if config.logging:
        files.append(("core/logging/__init__.py", logging_new_templates.LOGGING_INIT))
        files.append(("core/logging/config.py", logging_new_templates.LOGGING_CONFIG))
        files.append(("core/logging/formatters.py", logging_new_templates.LOGGING_FORMATTERS))
        files.append(("core/logging/setup.py", logging_new_templates.LOGGING_SETUP))
    
    # Tests
    files.append(("tests/__init__.py", tests_new_templates.TESTS_INIT))
    if config.database != "none" and config.auth:
        files.append(("tests/conftest.py", tests_new_templates.CONFTEST))
    elif config.database != "none":
        files.append(("tests/conftest.py", tests_new_templates.CONFTEST_NO_AUTH))
    else:
        files.append(("tests/conftest.py", tests_new_templates.CONFTEST_SIMPLE))
    if config.database != "none":
        files.append(("tests/test_health.py", tests_new_templates.TEST_HEALTH))
    else:
        files.append(("tests/test_health.py", tests_new_templates.TEST_HEALTH_SIMPLE))
    if config.database != "none":
        if config.auth:
            files.append(("tests/test_users.py", tests_new_templates.TEST_USERS))
        else:
            files.append(("tests/test_users.py", tests_new_templates.TEST_USERS_NO_AUTH))
        if config.auth:
            files.append(("tests/test_auth.py", tests_new_templates.TEST_AUTH))
    
    # Build requirements
    files.append(("requirements.txt", _build_requirements(config)))
    
    # Environment files
    files.append((".env.example", _generate_env_example(config, template_vars)))
    files.append((".gitignore", _generate_gitignore()))
    
    # Docker support
    if config.docker:
        from fullapi.templates import dockerfile, dockercompose
        files.append(("Dockerfile", dockerfile.DOCKERFILE))
        if config.redis:
            files.append(("docker-compose.yml", dockercompose.DOCKERCOMPOSE_WITH_REDIS))
        else:
            files.append(("docker-compose.yml", dockercompose.DOCKERCOMPOSE))


def _build_requirements(config: ProjectConfig) -> str:
    """Build requirements.txt based on configuration."""
    
    req_lines = set()

    # Add base requirements
    for line in requirements.FULL_BASE.strip().split('\n'):
        if line.strip() and not line.strip().startswith('#'):
            req_lines.add(line.strip())

    # Add database-specific requirements
    if config.database == "postgresql":
        for line in requirements.FULL_POSTGRESQL.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())
    elif config.database == "mysql":
        for line in requirements.FULL_MYSQL.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())

    # Add auth requirements
    if config.auth:
        for line in requirements.FULL_AUTH.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())

    # Add alembic requirements
    if config.database != "none":
        for line in alembic.REQUIREMENTS_ALEMBIC.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())

    # Add redis requirements
    if config.redis:
        for line in redis.REQUIREMENTS_REDIS.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())

    # Add middleware requirements
    if config.middleware:
        for line in middleware_new_templates.REQUIREMENTS_MIDDLEWARE.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())

    # Add logging requirements
    if config.logging and hasattr(logging_new_templates, 'REQUIREMENTS_LOGGING'):
        for line in logging_new_templates.REQUIREMENTS_LOGGING.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                req_lines.add(line.strip())

    # Sort and join
    req_content = '\n'.join(sorted(req_lines)) + '\n'
    return req_content


def _generate_env_example(config: ProjectConfig, template_vars: dict) -> str:
    """Generate .env.example file based on configuration."""
    lines = [
        "# Application",
        f"APP_NAME={template_vars['project_name']}",
        "APP_VERSION=1.0.0",
        "DEBUG=true",
        "ENVIRONMENT=development",
        "",
    ]
    
    if config.database != "none":
        lines.extend([
            "# Database",
            f"DATABASE_URL={_get_database_url(config.database)}",
            "DB_POOL_SIZE=5",
            "DB_MAX_OVERFLOW=10",
            "DB_POOL_TIMEOUT=30",
            "",
        ])
    
    if config.auth:
        lines.extend([
            "# JWT Authentication",
            "SECRET_KEY=your-secret-key-change-in-production",
            "ALGORITHM=HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES=30",
            "REFRESH_TOKEN_EXPIRE_DAYS=7",
            "",
        ])
    
    if config.middleware:
        lines.extend([
            "# CORS",
            "CORS_ORIGINS=http://localhost:3000,http://localhost:8000",
            "CORS_ALLOW_CREDENTIALS=true",
            "",
            "# Rate Limiting",
            "RATE_LIMIT_ENABLED=false",
            "RATE_LIMIT_REQUESTS=100",
            "RATE_LIMIT_WINDOW=60",
            "",
            "# Security Headers",
            "SECURITY_HEADERS_ENABLED=true",
            "",
            "# Gzip Compression",
            "GZIP_ENABLED=true",
            "GZIP_MINIMUM_SIZE=1000",
            "",
            "# Request ID",
            "REQUEST_ID_ENABLED=true",
            "REQUEST_ID_HEADER=X-Request-ID",
            "",
            "# Request Logging",
            "REQUEST_LOGGING_ENABLED=false",
            "REQUEST_LOGGING_FORMAT=%(asctime)s - %(levelname)s - %(message)s",
            "",
        ])
    
    if config.redis:
        lines.extend([
            "# Redis",
            "REDIS_URL=redis://localhost:6379/0",
            "REDIS_ENABLED=true",
            "",
        ])
    
    if config.logging:
        lines.extend([
            "# Logging",
            "LOG_LEVEL=INFO",
            "LOG_FILE_PATH=logs/app.log",
            "",
        ])
    
    return "\n".join(lines)


def _generate_gitignore() -> str:
    """Generate comprehensive .gitignore file."""
    return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
ENV/
env/
.venv/

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Logs
*.log
logs/
*.log.*

# Database
*.db
*.sqlite
*.sqlite3

# Docker
.docker/

# Terraform
.terraform/
.terraform.lock.hcl
terraform.tfstate
terraform.tfstate.backup
*.tfvars
!terraform.tfvars.example

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
.cache/
"""


def _generate_auth_schema() -> str:
    """Generate auth schema file."""
    return '''"""Authentication schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request schema."""
    refresh_token: str = Field(..., description="Refresh token to renew access token")


class TokenPayload(BaseModel):
    """Token payload schema (internal use)."""
    sub: str
    exp: int
    type: str = "access"
'''
