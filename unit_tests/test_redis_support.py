"""Tests for Redis caching support."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from fullapi.scaffold import scaffold_project
from fullapi.config import ProjectConfig
from fullapi.templates import redis


class TestRedisSupport:
    """Test cases for Redis caching support."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_redis_files_created_with_flag(self):
        """Test that Redis files are created when Redis flag is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check Redis files are created
        assert (project_path / "core" / "redis_config.py").exists()
        assert (project_path / "core" / "redis_utils.py").exists()
        assert (project_path / "routers" / "redis.py").exists()
        assert (project_path / "deps_redis.py").exists()

    def test_redis_files_not_created_without_flag(self):
        """Test that Redis files are not created when Redis flag is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check Redis files are not created
        assert not (project_path / "core" / "redis_config.py").exists()
        assert not (project_path / "core" / "redis_utils.py").exists()
        assert not (project_path / "routers" / "redis.py").exists()
        assert not (project_path / "deps_redis.py").exists()

    def test_redis_config_content(self):
        """Test that redis_config.py contains correct configuration."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        redis_config = (project_path / "core" / "redis_config.py").read_text()
        
        # Check key classes and functions
        assert "class RedisConfig:" in redis_config
        assert "class RedisClient:" in redis_config
        assert "def get_redis_url(self) -> str:" in redis_config
        assert "def health_check(self) -> dict:" in redis_config
        assert "redis_client = RedisClient()" in redis_config

    def test_redis_utils_content(self):
        """Test that redis_utils.py contains correct utility functions."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        redis_utils = (project_path / "core" / "redis_utils.py").read_text()
        
        # Check key functions
        assert "def cache_key(prefix: str, identifier: str) -> str:" in redis_utils
        assert "def set_cache(" in redis_utils
        assert "def get_cache(" in redis_utils
        assert "def delete_cache(key: str) -> bool:" in redis_utils
        assert "def cache_result(" in redis_utils
        assert "class CacheManager:" in redis_utils

    def test_redis_router_content(self):
        """Test that redis.py router contains correct endpoints."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        redis_router = (project_path / "routers" / "redis.py").read_text()
        
        # Check key endpoints
        assert "@router.get(\"/health\"" in redis_router
        assert "@router.post(\"/clear\"" in redis_router
        assert "@router.get(\"/info\"" in redis_router
        assert "@router.get(\"/config\"" in redis_router
        assert "def redis_health():" in redis_router
        assert "def clear_redis_cache(" in redis_router

    def test_redis_deps_content(self):
        """Test that deps_redis.py contains correct dependencies."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        redis_deps = (project_path / "deps_redis.py").read_text()
        
        # Check key functions
        assert "def get_redis_client():" in redis_deps
        assert "def get_cache_manager(prefix: str = \"app\"):" in redis_deps
        assert "from core.redis_config import redis_client" in redis_deps

    def test_redis_requirements_added(self):
        """Test that Redis is added to requirements.txt when Redis flag is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        requirements = (project_path / "requirements.txt").read_text()
        
        # Check Redis is in requirements
        assert "redis>=5.0.0" in requirements

    def test_redis_requirements_not_added_without_flag(self):
        """Test that Redis is not added to requirements.txt when Redis flag is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        requirements = (project_path / "requirements.txt").read_text()
        
        # Check Redis is not in requirements
        assert "redis" not in requirements.lower()

    def test_redis_with_all_features(self):
        """Test that Redis works correctly with all other features enabled."""
        config = ProjectConfig(
            name="test_full_project",
            mode="full",
            database="postgresql",
            auth=True,
            docker=True,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_full_project"
        
        # Check all expected files exist
        assert (project_path / "core" / "redis_config.py").exists()
        assert (project_path / "core" / "redis_utils.py").exists()
        assert (project_path / "routers" / "redis.py").exists()
        assert (project_path / "deps_redis.py").exists()
        assert (project_path / "core" / "security.py").exists()  # Auth file
        assert (project_path / "alembic.ini").exists()  # Alembic file
        assert (project_path / "Dockerfile").exists()  # Docker file

    def test_redis_environment_variables(self):
        """Test that Redis config uses correct environment variables."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        redis_config = (project_path / "core" / "redis_config.py").read_text()
        
        # Check environment variable usage
        assert "os.getenv(\"REDIS_URL\"" in redis_config
        assert "os.getenv(\"REDIS_HOST\"" in redis_config
        assert "os.getenv(\"REDIS_PORT\"" in redis_config
        assert "os.getenv(\"REDIS_PASSWORD\"" in redis_config
        assert "os.getenv(\"REDIS_SSL\"" in redis_config

    def test_redis_cache_manager_methods(self):
        """Test that CacheManager has all required methods."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        redis_utils = (project_path / "core" / "redis_utils.py").read_text()
        
        # Check CacheManager methods
        assert "def get(self, identifier: str, default: Any = None) -> Any:" in redis_utils
        assert "def set(self, identifier: str, value: Any, expire:" in redis_utils
        assert "def delete(self, identifier: str) -> bool:" in redis_utils
        assert "def clear_all(self) -> int:" in redis_utils


class TestRedisTemplates:
    """Test Redis template constants."""

    def test_redis_constants_exist(self):
        """Test that all required Redis template constants exist."""
        assert hasattr(redis, 'REDIS_CONFIG')
        assert hasattr(redis, 'REDIS_UTILS')
        assert hasattr(redis, 'REDIS_ROUTER')
        assert hasattr(redis, 'REDIS_DEPS')
        assert hasattr(redis, 'REQUIREMENTS_REDIS')
        assert hasattr(redis, 'ENV_EXAMPLE_REDIS')

    def test_redis_constants_not_empty(self):
        """Test that Redis template constants are not empty."""
        assert redis.REDIS_CONFIG.strip() != ""
        assert redis.REDIS_UTILS.strip() != ""
        assert redis.REDIS_ROUTER.strip() != ""
        assert redis.REDIS_DEPS.strip() != ""
        assert redis.REQUIREMENTS_REDIS.strip() != ""
        assert redis.ENV_EXAMPLE_REDIS.strip() != ""

    def test_redis_requirements_contains_redis(self):
        """Test that requirements string contains redis."""
        assert "redis" in redis.REQUIREMENTS_REDIS.lower()
        assert "5.0.0" in redis.REQUIREMENTS_REDIS

    def test_redis_env_example_contains_all_vars(self):
        """Test that env example contains all Redis variables."""
        env_vars = [
            "REDIS_URL",
            "REDIS_HOST", 
            "REDIS_PORT",
            "REDIS_DB",
            "REDIS_PASSWORD",
            "REDIS_SSL",
            "REDIS_DECODE_RESPONSES",
            "REDIS_SOCKET_TIMEOUT",
            "REDIS_SOCKET_CONNECT_TIMEOUT",
            "REDIS_HEALTH_CHECK_INTERVAL",
            "REDIS_MAX_CONNECTIONS"
        ]
        
        for var in env_vars:
            assert var in redis.ENV_EXAMPLE_REDIS


if __name__ == "__main__":
    pytest.main([__file__])
