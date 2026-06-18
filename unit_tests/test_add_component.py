"""Tests for the add_component functionality."""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch

from fullapi.add_component import add_component_to_project
from fullapi.cli import handle_add


class TestAddComponent:
    """Test cases for adding components to existing projects."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_basic_project(self):
        """Create a basic fullapi project for testing."""
        # Create main.py
        main_py = """from fastapi import FastAPI
from routers.health import router as health_router

app = FastAPI(title="test_project")

app.include_router(health_router, tags=["health"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        Path("main.py").write_text(main_py)
        
        # Create routers directory and health router
        Path("routers").mkdir()
        health_router = """from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}
"""
        Path("routers/health.py").write_text(health_router)

    def create_full_project(self):
        """Create a full fullapi project with database support."""
        self.create_basic_project()
        
        # Create database-related directories
        Path("db").mkdir()
        Path("models").mkdir()
        Path("schemas").mkdir()
        Path("crud").mkdir()
        
        # Create db/session.py
        db_session = """from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
        Path("db/session.py").write_text(db_session)
        
        # Create db/base.py
        db_base = """from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
"""
        Path("db/base.py").write_text(db_base)

    def test_add_router_to_basic_project(self):
        """Test adding a router to a basic project."""
        self.create_basic_project()
        
        add_component_to_project("router", "Product")
        
        # Check router file was created
        router_path = Path("routers/product.py")
        assert router_path.exists()
        
        # Check router content
        content = router_path.read_text()
        assert "class Product" in content or "Product router" in content
        assert "APIRouter" in content
        
        # Check main.py was updated
        main_content = Path("main.py").read_text()
        assert "from routers import product" in main_content
        assert "app.include_router(product.router" in main_content

    def test_add_router_already_exists(self):
        """Test adding a router that already exists."""
        self.create_basic_project()
        
        # Add router first time
        add_component_to_project("router", "Product")
        
        # Try to add same router again — file still exists (no overwrite)
        router_mtime_before = Path("routers/product.py").stat().st_mtime
        add_component_to_project("router", "Product")
        # File should not have changed
        assert Path("routers/product.py").stat().st_mtime == router_mtime_before

    def test_add_model_to_full_project(self):
        """Test adding a model to a full project with database."""
        self.create_full_project()
        
        add_component_to_project("model", "User")
        
        # Check model file was created
        model_path = Path("models/user.py")
        assert model_path.exists()
        
        # Check schema file was created
        schema_path = Path("schemas/user.py")
        assert schema_path.exists()
        
        # Check CRUD file was created
        crud_path = Path("crud/user.py")
        assert crud_path.exists()
        
        # Check model content
        model_content = model_path.read_text()
        assert "class User(Base):" in model_content
        assert "__tablename__ = \"users\"" in model_content

    def test_add_model_to_basic_project(self):
        """Test adding a model to a basic project without database."""
        self.create_basic_project()
        
        # Should not create model files without db/ directory
        add_component_to_project("model", "User")
        assert not Path("models/user.py").exists()

    def test_add_model_already_exists(self):
        """Test adding a model that already exists."""
        self.create_full_project()
        
        # Add model first time
        add_component_to_project("model", "User")
        
        # Try to add same model again — should not overwrite
        model_mtime_before = Path("models/user.py").stat().st_mtime
        add_component_to_project("model", "User")
        assert Path("models/user.py").stat().st_mtime == model_mtime_before

    def test_add_component_invalid_project(self):
        """Test adding component to non-fullapi project."""
        # Don't create any project files
        
        with patch('fullapi.add_component.print'):
            with pytest.raises(SystemExit):
                from fullapi.cli import handle_add
                from argparse import Namespace
                
                args = Namespace(component_type="router", component_name="Product")
                handle_add(args)

    def test_component_name_capitalization(self):
        """Test that component names are properly capitalized."""
        self.create_basic_project()
        
        add_component_to_project("router", "product")
        
        # Check router file was created with lowercase name
        router_path = Path("routers/product.py")
        assert router_path.exists()
        
        # Check content uses proper capitalization
        content = router_path.read_text()
        assert "Product router" in content

    def test_multiple_routers(self):
        """Test adding multiple routers."""
        self.create_basic_project()
        
        # Add first router
        add_component_to_project("router", "Product")
        
        # Add second router
        add_component_to_project("router", "User")
        
        # Check both routers exist
        assert Path("routers/product.py").exists()
        assert Path("routers/user.py").exists()
        
        # Check main.py includes both
        main_content = Path("main.py").read_text()
        assert "from routers import product, user" in main_content
        assert "app.include_router(product.router" in main_content
        assert "app.include_router(user.router" in main_content


class TestCLIIntegration:
    """Test CLI integration for add command."""

    def setup_method(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_cli_add_command(self):
        """Test CLI add command."""
        self.create_basic_project()
        
        from argparse import Namespace
        
        with patch('fullapi.cli.add_component_to_project') as mock_add:
            args = Namespace(component_type="router", component_name="Product")
            handle_add(args)

            mock_add.assert_called_once_with("router", "Product")

    def create_basic_project(self):
        """Create a basic fullapi project for testing."""
        Path("main.py").write_text("# test main.py")


if __name__ == "__main__":
    pytest.main([__file__])
