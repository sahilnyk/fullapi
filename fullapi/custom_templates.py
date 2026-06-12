"""Custom template loader and manager."""

import shutil
from pathlib import Path
from typing import Dict, Optional

from fullapi.colors import warning, info, error


class CustomTemplateManager:
    """Manages custom templates for project scaffolding."""
    
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all template files from the custom template directory."""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_path}")
        
        # Load all .py files as templates
        for template_file in self.template_path.glob("*.py"):
            template_name = template_file.stem
            try:
                content = template_file.read_text()
                self.templates[template_name] = content
            except Exception as e:
                print(f"{warning('Warning:')} Could not load template {template_name}: {e}")
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a specific template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> Dict[str, str]:
        """Get all available templates."""
        return self.templates.copy()
    
    def validate_template_structure(self) -> bool:
        """Validate that template directory has required structure."""
        required_files = [
            "main.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for req_file in required_files:
            if not (self.template_path / req_file).exists():
                missing_files.append(req_file)
        
        if missing_files:
            print(f"{error('Error:')} Missing required template files: {', '.join(missing_files)}")
            print(f"{info('Required files:')} {', '.join(required_files)}")
            return False
        
        return True
    
    def get_template_files(self) -> Dict[str, str]:
        """Get all template files with their content."""
        template_files = {}
        
        for file_path in self.template_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.template_path)
                try:
                    content = file_path.read_text()
                    template_files[str(relative_path)] = content
                except Exception as e:
                    print(f"{warning('Warning:')} Could not read {relative_path}: {e}")
        
        return template_files


def load_custom_template(template_path: str) -> Optional[CustomTemplateManager]:
    """Load custom template from path."""
    try:
        return CustomTemplateManager(template_path)
    except FileNotFoundError as e:
        print(f"{error('Error:')} {e}")
        return None
    except Exception as e:
        print(f"{error('Error:')} Failed to load custom templates: {e}")
        return None


def create_template_from_project(project_path: str, output_path: str) -> bool:
    """Create a custom template from an existing project."""
    try:
        project_dir = Path(project_path)
        output_dir = Path(output_path)
        
        if not project_dir.exists():
            print(f"{error('Error:')} Project directory not found: {project_path}")
            return False
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy project files to template directory
        for file_path in project_dir.rglob("*"):
            if file_path.is_file():
                # Skip certain files
                if file_path.name in ['.git', '__pycache__', '.env', 'app.db']:
                    continue
                
                relative_path = file_path.relative_to(project_dir)
                output_file = output_dir / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, output_file)
        
        print(f"{info('Success:')} Template created at {output_path}")
        return True
        
    except Exception as e:
        print(f"{error('Error:')} Failed to create template: {e}")
        return False


def list_available_templates() -> None:
    """List available built-in template information."""
    print(f"{info('Built-in templates:')}")
    print("  • Basic mode: Minimal FastAPI structure")
    print("  • Full mode: Complete production structure")
    print()
    print(f"{info('Custom templates:')}")
    print("  Use --template /path/to/templates to specify custom templates")
    print()
    print(f"{info('Template structure:')}")
    print("  • main.py: Main FastAPI application")
    print("  • requirements.txt: Project dependencies")
    print("  • routers/: API router files")
    print("  • models/: Database model files")
    print("  • schemas/: Pydantic schema files")
    print("  • crud/: CRUD operation files")
    print("  • core/: Core configuration files")
    print("  • db/: Database configuration files")
    print("  • tests/: Test files")
    print("  • Dockerfile: Docker configuration (optional)")
    print("  • docker-compose.yml: Docker Compose (optional)")
    print("  • alembic/: Database migration files (optional)")
    print("  • .env.example: Environment variables example (optional)")
