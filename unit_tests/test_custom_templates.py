"""Tests for custom templates support."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from fullapi.scaffold import scaffold_project
from fullapi.config import ProjectConfig
from fullapi.custom_templates import CustomTemplateManager, create_template_from_project


class TestCustomTemplates:
    """Test cases for custom templates support."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_custom_template_manager_creation(self):
        """Test CustomTemplateManager creation."""
        # Create a temporary template directory
        template_dir = self.test_dir / "templates"
        template_dir.mkdir()
        
        # Create a simple template file
        template_file = template_dir / "main.py"
        template_file.write_text("""# Main FastAPI application
from fastapi import FastAPI

app = FastAPI(title="${project_name}")
""")
        
        try:
            manager = CustomTemplateManager(str(template_dir))
            assert manager.templates["main"] is not None
            assert "FastAPI(title=\"${project_name}\")" in manager.templates["main"]
        except Exception as e:
            pytest.fail(f"Failed to create CustomTemplateManager: {e}")

    def test_custom_template_manager_invalid_directory(self):
        """Test CustomTemplateManager with invalid directory."""
        with pytest.raises(FileNotFoundError):
            CustomTemplateManager("/nonexistent/directory")

    def test_custom_template_validation(self):
        """Test template structure validation."""
        # Create a temporary template directory
        template_dir = self.test_dir / "templates"
        template_dir.mkdir()
        
        # Create required files
        (template_dir / "main.py").write_text("# Main file")
        (template_dir / "requirements.txt").write_text("fastapi")
        
        manager = CustomTemplateManager(str(template_dir))
        assert manager.validate_template_structure() is True
        
        # Test with missing file
        (template_dir / "main.py").unlink()
        manager = CustomTemplateManager(str(template_dir))
        assert manager.validate_template_structure() is False

    def test_scaffold_with_custom_template(self):
        """Test scaffolding with custom template."""
        # Create a custom template directory
        template_dir = self.test_dir / "custom_templates"
        template_dir.mkdir()
        
        # Create template files
        (template_dir / "main.py").write_text("""# Main FastAPI application
from fastapi import FastAPI

app = FastAPI(title="${project_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""")
        
        (template_dir / "requirements.txt").write_text("fastapi\nuvicorn")
        
        config = ProjectConfig(
            name="test_project",
            mode="basic",
            database="none",
            auth=False,
            docker=False,
            redis=False,
            template=str(template_dir)
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check project was created
        assert project_path.exists()
        assert (project_path / "main.py").exists()
        assert (project_path / "requirements.txt").exists()
        
        # Check content was properly substituted
        main_content = (project_path / "main.py").read_text()
        assert "FastAPI(title=\"test_project\")" in main_content

    def test_scaffold_with_invalid_custom_template(self):
        """Test scaffolding with invalid custom template path."""
        config = ProjectConfig(
            name="test_project",
            mode="basic",
            database="none",
            auth=False,
            docker=False,
            redis=False,
            template="/nonexistent/template/path"
        )
        
        os.chdir(self.test_dir)
        
        # Should not raise exception, but should handle gracefully
        scaffold_project(config)
        
        # Project should not be created due to invalid template
        project_path = self.test_dir / "test_project"
        assert not project_path.exists()

    def test_create_template_from_project(self):
        """Test creating template from existing project."""
        # Create a source project
        source_dir = self.test_dir / "source_project"
        source_dir.mkdir()
        
        (source_dir / "main.py").write_text("""# Main FastAPI application
from fastapi import FastAPI

app = FastAPI(title="source_project")
""")
        
        (source_dir / "requirements.txt").write_text("fastapi\nuvicorn")
        
        output_dir = self.test_dir / "output_template"
        
        result = create_template_from_project(str(source_dir), str(output_dir))
        
        assert result is True
        assert output_dir.exists()
        assert (output_dir / "main.py").exists()
        assert (output_dir / "requirements.txt").exists()

    def test_create_template_from_nonexistent_project(self):
        """Test creating template from nonexistent project."""
        result = create_template_from_project(
            "/nonexistent/project", 
            str(self.test_dir / "output_template")
        )
        
        assert result is False

    def test_template_file_loading(self):
        """Test loading of various template file types."""
        # Create a temporary template directory
        template_dir = self.test_dir / "templates"
        template_dir.mkdir()
        
        # Create different file types
        (template_dir / "main.py").write_text("# Python main file")
        (template_dir / "config.yaml").write_text("# YAML config file")
        (template_dir / "Dockerfile").write_text("# Docker file")
        
        manager = CustomTemplateManager(str(template_dir))
        templates = manager.list_templates()
        
        # Check all files were loaded
        assert "main.py" in templates
        assert "config.yaml" in templates
        assert "Dockerfile" in templates
        assert templates["main.py"] == "# Python main file"
        assert templates["config.yaml"] == "# YAML config file"

    def test_template_substitution(self):
        """Test template variable substitution."""
        # Create a temporary template directory
        template_dir = self.test_dir / "templates"
        template_dir.mkdir()
        
        # Create template with variables
        template_content = """# Project: ${project_name}
# Mode: ${mode}
# Database: ${database}
"""
        
        (template_dir / "config.py").write_text(template_content)
        
        manager = CustomTemplateManager(str(template_dir))
        manager.get_template_files()
        
        # Test substitution
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="postgresql",
            auth=True,
            docker=True,
            redis=True
        )
        
        substituted = template_content.replace("${project_name}", "test_project")
        substituted = substituted.replace("${mode}", config.mode)
        substituted = substituted.replace("${database}", config.database)
        
        assert substituted == "# Project: test_project\n# Mode: full\n# Database: postgresql\n"

    def test_custom_template_with_all_features(self):
        """Test custom template with all features enabled."""
        # Create a comprehensive custom template
        template_dir = self.test_dir / "full_templates"
        template_dir.mkdir()
        
        # Create full template structure
        (template_dir / "main.py").write_text("""# Main FastAPI application
from fastapi import FastAPI
from routers import health
from core.config import get_settings

app = FastAPI(title="${project_name}")

app.include_router(health.router, tags=["health"])
""")
        
        (template_dir / "routers" / "__init__.py").write_text("")
        (template_dir / "routers" / "health.py").write_text("""# Health check router
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}
""")
        
        (template_dir / "core" / "__init__.py").write_text("")
        (template_dir / "core" / "config.py").write_text("""# Configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "${project_name}"
""")
        
        config = ProjectConfig(
            name="test_project",
            mode="full",
            database="sqlite",
            auth=False,
            docker=False,
            redis=False,
            template=str(template_dir)
        )
        
        os.chdir(self.test_dir)
        scaffold_project(config)
        
        project_path = self.test_dir / "test_project"
        
        # Check complex structure was created
        assert (project_path / "main.py").exists()
        assert (project_path / "routers" / "__init__.py").exists()
        assert (project_path / "routers" / "health.py").exists()
        assert (project_path / "core" / "__init__.py").exists()
        assert (project_path / "core" / "config.py").exists()


class TestCustomTemplateUtilities:
    """Test custom template utility functions."""

    def test_list_available_templates(self):
        """Test listing available templates information."""
        from fullapi.custom_templates import list_available_templates
        
        # Should not raise exception
        list_available_templates()

    def test_template_file_filtering(self):
        """Test that certain files are filtered out when creating templates."""
        # Create a source project with various files
        source_dir = self.test_dir / "source_project"
        source_dir.mkdir()
        
        # Create various files including ones that should be filtered
        (source_dir / "main.py").write_text("# Main file")
        (source_dir / "requirements.txt").write_text("fastapi")
        (source_dir / ".git").mkdir()  # Should be filtered
        (source_dir / "__pycache__").mkdir()  # Should be filtered
        (source_dir / ".env").write_text("SECRET=123")  # Should be filtered
        (source_dir / "app.db").write_text("data")  # Should be filtered
        
        output_dir = self.test_dir / "output_template"
        
        result = create_template_from_project(str(source_dir), str(output_dir))
        
        assert result is True
        assert (output_dir / "main.py").exists()
        assert (output_dir / "requirements.txt").exists()
        
        # Check filtered files are not included
        assert not (output_dir / ".git").exists()
        assert not (output_dir / "__pycache__").exists()
        assert not (output_dir / ".env").exists()
        assert not (output_dir / "app.db").exists()


if __name__ == "__main__":
    pytest.main([__file__])
