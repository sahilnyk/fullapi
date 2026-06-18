"""Tests for middleware support."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from fullapi.scaffold import scaffold_project
from fullapi.config import ProjectConfig
from fullapi.templates import middleware_new as middleware


class TestMiddlewareSupport:
    """Test cases for middleware support."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_middleware_files_created_with_flag(self):
        """Test that middleware files are created when middleware flag is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check middleware files are created under core/middleware/
        assert (project_path / "core" / "middleware" / "__init__.py").exists()
        assert (project_path / "core" / "middleware" / "config.py").exists()
        assert (project_path / "core" / "middleware" / "cors.py").exists()
        assert (project_path / "core" / "middleware" / "rate_limit.py").exists()
        assert (project_path / "core" / "middleware" / "security_headers.py").exists()
        assert (project_path / "core" / "middleware" / "gzip.py").exists()
        assert (project_path / "core" / "middleware" / "request_logging.py").exists()
        assert (project_path / "core" / "middleware" / "setup.py").exists()

    def test_middleware_files_not_created_without_flag(self):
        """Test that middleware files are not created when middleware flag is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check middleware files are not created
        assert not (project_path / "core" / "middleware" / "config.py").exists()
        assert not (project_path / "core" / "middleware" / "cors.py").exists()
        assert not (project_path / "core" / "middleware" / "rate_limit.py").exists()
        assert not (project_path / "core" / "middleware" / "setup.py").exists()

    def test_middleware_config_content(self):
        """Test that middleware_config.py contains correct configuration."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        middleware_config = (project_path / "core" / "middleware" / "config.py").read_text()
        
        # Check key classes and functions
        assert "class MiddlewareConfig:" in middleware_config
        assert "def __init__(self):" in middleware_config
        assert "def _get_bool_env(" in middleware_config
        assert "def _get_int_env(" in middleware_config
        assert "def _get_list_env(" in middleware_config
        assert "def _get_cors_origins(self) -> List[str]:" in middleware_config
        assert "self.cors_origins: List[str]" in middleware_config
        assert "self.cors_allow_credentials: bool" in middleware_config
        assert "self.cors_allow_methods: List[str]" in middleware_config

    def test_middleware_cors_content(self):
        """Test that middleware_cors.py contains correct CORS setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        cors_middleware = (project_path / "core" / "middleware" / "cors.py").read_text()

        # Check key imports and functions
        assert "from fastapi.middleware.cors import CORSMiddleware" in cors_middleware
        assert "def create_cors_middleware(config: MiddlewareConfig):" in cors_middleware
        assert "return CORSMiddleware(" in cors_middleware

    def test_middleware_rate_limit_content(self):
        """Test that middleware_rate_limit.py contains correct rate limiting setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        rate_limit_middleware = (project_path / "core" / "middleware" / "rate_limit.py").read_text()

        # Check key imports and functions
        assert "from starlette.middleware.base import BaseHTTPMiddleware" in rate_limit_middleware
        assert "from starlette.responses import JSONResponse" in rate_limit_middleware
        assert "class RateLimitMiddleware(BaseHTTPMiddleware):" in rate_limit_middleware
        assert "def __init__(self, app, requests: int = 100, window: int = 60):" in rate_limit_middleware
        assert "def _get_client_id(self, request: Request) -> str:" in rate_limit_middleware
        assert "async def dispatch(self, request: Request, call_next):" in rate_limit_middleware

    def test_middleware_security_content(self):
        """Test that middleware_security.py contains correct security headers setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        security_middleware = (project_path / "core" / "middleware" / "security_headers.py").read_text()

        # Check key imports and functions
        assert "from starlette.middleware.base import BaseHTTPMiddleware" in security_middleware
        assert "from fastapi import Request" in security_middleware
        assert "class SecurityHeadersMiddleware(BaseHTTPMiddleware):" in security_middleware
        assert "async def dispatch(self, request: Request, call_next):" in security_middleware
        assert "response.headers[header] = value" in security_middleware

    def test_middleware_gzip_content(self):
        """Test that middleware_gzip.py contains correct Gzip setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        gzip_middleware = (project_path / "core" / "middleware" / "gzip.py").read_text()

        # Check key imports and functions
        assert "from starlette.middleware.gzip import GZipMiddleware" in gzip_middleware
        assert "def create_gzip_middleware(config: Optional[MiddlewareConfig] = None):" in gzip_middleware
        assert "return GZipMiddleware(" in gzip_middleware

    def test_middleware_logging_content(self):
        """Test that middleware_logging.py contains correct logging setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        logging_middleware = (project_path / "core" / "middleware" / "request_logging.py").read_text()

        # Check key imports and functions
        assert "from starlette.middleware.base import BaseHTTPMiddleware" in logging_middleware
        assert "import logging" in logging_middleware
        assert "class RequestLoggingMiddleware(BaseHTTPMiddleware):" in logging_middleware
        assert "def __init__(self, app, config: Optional[MiddlewareConfig] = None):" in logging_middleware
        assert "async def dispatch(self, request: Request, call_next):" in logging_middleware
        assert "self.logger.info(" in logging_middleware

    def test_middleware_setup_content(self):
        """Test that middleware_setup.py contains correct setup functions."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        setup_middleware = (project_path / "core" / "middleware" / "setup.py").read_text()

        # Check key imports and functions
        assert "from fastapi import FastAPI" in setup_middleware
        assert "def setup_middleware(app: FastAPI, config: Optional[MiddlewareConfig] = None):" in setup_middleware
        assert "app.add_middleware(" in setup_middleware

    def test_middleware_setup_imports(self):
        """Test that middleware setup.py imports are correct."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )

        os.chdir(self.test_dir)
        scaffold_project(config)

        project_path = self.test_dir / "test_project"
        setup_content = (project_path / "core" / "middleware" / "setup.py").read_text()

        assert "from fastapi import FastAPI" in setup_content
        assert "def setup_middleware" in setup_content
        assert "def get_middleware_config" in setup_content

    def test_middleware_with_all_features(self):
        """Test that middleware works correctly with all other features enabled."""
        config = ProjectConfig(
            name="test_full_project",
            mode="full",
            database="postgresql",
            auth=True,
            docker=True,
            redis=True,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_full_project"
        
        # Check all expected files exist
        assert (project_path / "core" / "middleware" / "config.py").exists()
        assert (project_path / "core" / "middleware" / "cors.py").exists()
        assert (project_path / "core" / "middleware" / "rate_limit.py").exists()
        assert (project_path / "core" / "middleware" / "security_headers.py").exists()
        assert (project_path / "core" / "middleware" / "gzip.py").exists()
        assert (project_path / "core" / "middleware" / "request_logging.py").exists()
        assert (project_path / "core" / "middleware" / "setup.py").exists()
        assert (project_path / "core" / "security.py").exists()  # Auth file
        assert (project_path / "alembic.ini").exists()  # Alembic file
        assert (project_path / "Dockerfile").exists()  # Docker file

    def test_middleware_requirements_added(self):
        """Test that middleware requirements are added to requirements.txt when middleware flag is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        requirements = (project_path / "requirements.txt").read_text()
        
        # Check middleware requirements are in requirements
        assert "fastapi>=0.100.0" in requirements

    def test_middleware_requirements_not_added_without_flag(self):
        """Test that middleware requirements are not added when middleware flag is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        requirements = (project_path / "requirements.txt").read_text()
        
        # Check middleware requirements are not in requirements
        assert "starlette" not in requirements.lower()


class TestMiddlewareTemplates:
    """Test middleware template constants."""

    def test_middleware_constants_exist(self):
        """Test that all required middleware template constants exist."""
        assert hasattr(middleware, 'MIDDLEWARE_CONFIG')
        assert hasattr(middleware, 'MIDDLEWARE_CORS')
        assert hasattr(middleware, 'MIDDLEWARE_RATE_LIMIT')
        assert hasattr(middleware, 'MIDDLEWARE_SECURITY_HEADERS')
        assert hasattr(middleware, 'MIDDLEWARE_GZIP')
        assert hasattr(middleware, 'MIDDLEWARE_REQUEST_LOGGING')
        assert hasattr(middleware, 'MIDDLEWARE_SETUP')
        assert hasattr(middleware, 'REQUIREMENTS_MIDDLEWARE')
        assert hasattr(middleware, 'ENV_EXAMPLE_MIDDLEWARE')

    def test_middleware_constants_not_empty(self):
        """Test that middleware template constants are not empty."""
        assert middleware.MIDDLEWARE_CONFIG.strip() != ""
        assert middleware.MIDDLEWARE_CORS.strip() != ""
        assert middleware.MIDDLEWARE_RATE_LIMIT.strip() != ""
        assert middleware.MIDDLEWARE_SECURITY_HEADERS.strip() != ""
        assert middleware.MIDDLEWARE_GZIP.strip() != ""
        assert middleware.MIDDLEWARE_REQUEST_LOGGING.strip() != ""
        assert middleware.MIDDLEWARE_SETUP.strip() != ""
        assert middleware.REQUIREMENTS_MIDDLEWARE.strip() != ""
        assert middleware.ENV_EXAMPLE_MIDDLEWARE.strip() != ""

    def test_middleware_requirements_contains_fastapi(self):
        """Test that requirements string contains fastapi."""
        assert "fastapi" in middleware.REQUIREMENTS_MIDDLEWARE.lower()

    def test_middleware_env_example_contains_all_vars(self):
        """Test that env example contains all middleware variables."""
        env_vars = [
            "CORS_ORIGINS",
            "CORS_ALLOW_CREDENTIALS",
            "CORS_ALLOW_METHODS",
            "CORS_ALLOW_HEADERS",
            "RATE_LIMIT_ENABLED",
            "RATE_LIMIT_REQUESTS",
            "RATE_LIMIT_WINDOW",
            "SECURITY_HEADERS_ENABLED",
            "GZIP_ENABLED",
            "GZIP_MINIMUM_SIZE",
            "REQUEST_LOGGING_ENABLED",
            "REQUEST_LOGGING_FORMAT",
            "REQUEST_LOGGING_EXCLUDE_PATHS",
            "TRUSTED_PROXY_HEADERS",
        ]

        for var in env_vars:
            assert var in middleware.ENV_EXAMPLE_MIDDLEWARE


if __name__ == "__main__":
    pytest.main([__file__])
