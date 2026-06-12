"""Tests for logging support."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from fullapi.scaffold import scaffold_project
from fullapi.config import ProjectConfig
from fullapi.templates import logging_new as logging_templates


class TestLoggingSupport:
    """Test cases for logging support."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_logging_files_created_with_flag(self):
        """Test that logging files are created when logging flag is enabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=False,
            logging=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check logging files are created
        assert (project_path / "core" / "logging_config.py").exists()
        assert (project_path / "core" / "logging_setup.py").exists()

    def test_logging_files_not_created_without_flag(self):
        """Test that logging files are not created when logging flag is disabled."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=False,
            logging=False
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check logging files are not created
        assert not (project_path / "core" / "logging_config.py").exists()
        assert not (project_path / "core" / "logging_setup.py").exists()

    def test_logging_config_content(self):
        """Test that logging_config.py contains correct configuration."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=False,
            logging=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        logging_config = (project_path / "core" / "logging_config.py").read_text()
        
        # Check key classes and functions
        assert "class LoggingConfig:" in logging_config
        assert "def __init__(self):" in logging_config
        assert "self.log_level: str" in logging_config
        assert "self.log_format: str" in logging_config

    def test_logging_setup_content(self):
        """Test that logging_setup.py contains correct setup."""
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            middleware=False,
            logging=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        logging_setup = (project_path / "core" / "logging_setup.py").read_text()
        
        # Check key imports and functions
        assert "import logging" in logging_setup
        assert "def setup_logging(" in logging_setup
        assert "def get_logger(" in logging_setup

    def test_logging_with_all_features(self):
        """Test that logging works correctly with all other features enabled."""
        config = ProjectConfig(
            name="test_full_project",
            mode="full",
            database="postgresql",
            auth=True,
            docker=True,
            redis=True,
            middleware=True,
            logging=True
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_full_project"
        
        # Check all expected files exist
        assert (project_path / "core" / "logging_config.py").exists()
        assert (project_path / "core" / "logging_setup.py").exists()
        assert (project_path / "core" / "security.py").exists()  # Auth file
        assert (project_path / "alembic.ini").exists()  # Alembic file
        assert (project_path / "Dockerfile").exists()  # Docker file

    def test_logging_templates_constants_exist(self):
        """Test that all required logging template constants exist."""
        assert hasattr(logging_templates, 'LOGGING_CONFIG')
        assert hasattr(logging_templates, 'LOGGING_SETUP')

    def test_logging_templates_constants_not_empty(self):
        """Test that logging template constants are not empty."""
        assert logging_templates.LOGGING_CONFIG.strip() != ""
        assert logging_templates.LOGGING_SETUP.strip() != ""


if __name__ == "__main__":
    pytest.main([__file__])
