"""Tests for Alembic migration support."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from fullapi.scaffold import scaffold_project
from fullapi.config import ProjectConfig
from fullapi.templates import alembic


class TestAlembicSupport:
    """Test cases for Alembic migration support."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_alembic_files_created_with_database(self):
        """Test that Alembic files are created when database is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check Alembic files are created
        assert (project_path / "alembic.ini").exists()
        assert (project_path / "alembic" / "env.py").exists()
        assert (project_path / "alembic" / "script.py.mako").exists()
        assert (project_path / "alembic" / "versions" / "__init__.py").exists()
        assert (project_path / "alembic" / "versions" / "001_initial_migration.py").exists()

    def test_alembic_files_not_created_without_database(self):
        """Test that Alembic files are not created when database is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="none",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check Alembic files are not created
        assert not (project_path / "alembic.ini").exists()
        assert not (project_path / "alembic").exists()

    def test_alembic_ini_content(self):
        """Test that alembic.ini contains correct configuration."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        alembic_ini = (project_path / "alembic.ini").read_text()
        
        # Check key configuration elements
        assert "script_location = alembic" in alembic_ini
        assert "sqlalchemy.url = sqlite:///./app.db" in alembic_ini
        assert "[loggers]" in alembic_ini
        assert "[handlers]" in alembic_ini
        assert "[formatters]" in alembic_ini

    def test_alembic_env_content(self):
        """Test that alembic/env.py contains correct imports and setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="postgresql",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        env_py = (project_path / "alembic" / "env.py").read_text()
        
        # Check key imports and setup
        assert "from alembic import context" in env_py
        assert "from sqlalchemy import engine_from_config" in env_py
        assert "from db.base import Base" in env_py
        assert "from models import *" in env_py
        assert "target_metadata = Base.metadata" in env_py
        assert "def get_database_url():" in env_py

    def test_alembic_script_mako_content(self):
        """Test that script.py.mako contains correct template."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        script_mako = (project_path / "alembic" / "script.py.mako").read_text()
        
        # Check Mako template syntax
        assert "${message}" in script_mako
        assert "${up_revision}" in script_mako
        assert "${down_revision | comma,n}" in script_mako
        assert "def upgrade() -> None:" in script_mako
        assert "def downgrade() -> None:" in script_mako

    def test_initial_migration_content(self):
        """Test that initial migration is created correctly."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        initial_migration = (project_path / "alembic" / "versions" / "001_initial_migration.py").read_text()
        
        # Check migration structure
        assert "Revision ID: 001" in initial_migration
        assert "down_revision = None" in initial_migration
        assert "def upgrade() -> None:" in initial_migration
        assert "def downgrade() -> None:" in initial_migration
        assert "# Create initial tables" in initial_migration

    def test_alembic_requirements_added(self):
        """Test that Alembic is added to requirements.txt when database is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        requirements = (project_path / "requirements.txt").read_text()
        
        # Check Alembic is in requirements
        assert "alembic>=1.12.0" in requirements

    def test_alembic_requirements_not_added_without_database(self):
        """Test that Alembic is not added to requirements.txt when database is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="none",
            auth=False,
            docker=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        requirements = (project_path / "requirements.txt").read_text()
        
        # Check Alembic is not in requirements
        assert "alembic" not in requirements.lower()

    def test_different_database_urls(self):
        """Test that different databases get correct URLs in alembic.ini."""
        test_cases = [
            ("sqlite", "sqlite:///./app.db"),
            ("postgresql", "postgresql://user:password@localhost:5432/app"),
            ("mysql", "mysql+pymysql://root:password@localhost:3306/app")
        ]
        
        for db_type, expected_url in test_cases:
            config = ProjectConfig(
                name=f"test_{db_type}",
                mode="full",
                database=db_type,
                auth=False,
                docker=False
            )
            
            os.chdir(self.test_dir)
            scaffold_project(config)
            
            project_path = self.test_dir / f"test_{db_type}"
            alembic_ini = (project_path / "alembic.ini").read_text()
            
            assert expected_url in alembic_ini

    def test_alembic_with_auth_and_docker(self):
        """Test that Alembic works correctly with auth and Docker enabled."""
        config = ProjectConfig(
            name="test_full_project",
            mode="full",
            database="postgresql",
            auth=True,
            docker=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_full_project"
        
        # Check all expected files exist
        assert (project_path / "alembic.ini").exists()
        assert (project_path / "alembic" / "env.py").exists()
        assert (project_path / "core" / "security.py").exists()  # Auth file
        assert (project_path / "Dockerfile").exists()  # Docker file
        assert (project_path / "docker-compose.yml").exists()  # Docker Compose file


class TestAlembicTemplates:
    """Test Alembic template constants."""

    def test_alembic_constants_exist(self):
        """Test that all required Alembic template constants exist."""
        assert hasattr(alembic, 'ALEMBIC_INI')
        assert hasattr(alembic, 'ENV_PY')
        assert hasattr(alembic, 'SCRIPT_PY_MAKO')
        assert hasattr(alembic, 'REQUIREMENTS_ALEMBIC')
        assert hasattr(alembic, 'INITIAL_MIGRATION')

    def test_alembic_constants_not_empty(self):
        """Test that Alembic template constants are not empty."""
        assert alembic.ALEMBIC_INI.strip() != ""
        assert alembic.ENV_PY.strip() != ""
        assert alembic.SCRIPT_PY_MAKO.strip() != ""
        assert alembic.REQUIREMENTS_ALEMBIC.strip() != ""
        assert alembic.INITIAL_MIGRATION.strip() != ""

    def test_alembic_requirements_contains_alembic(self):
        """Test that requirements string contains alembic."""
        assert "alembic" in alembic.REQUIREMENTS_ALEMBIC.lower()
        assert "1.12.0" in alembic.REQUIREMENTS_ALEMBIC


if __name__ == "__main__":
    pytest.main([__file__])
