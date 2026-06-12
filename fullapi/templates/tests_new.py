"""Test templates with comprehensive fixtures and examples."""

# tests/__init__.py
TESTS_INIT = '''"""Test package for the application."""
'''

# tests/conftest.py - Simple test fixtures (no database)
CONFTEST_SIMPLE = '''"""Test configuration and fixtures."""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create a test client without database dependencies."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_payload() -> dict:
    """Sample payload for health endpoint tests."""
    return {"status": "ok"}
'''

# tests/conftest.py - Test fixtures with database (no auth)
CONFTEST_NO_AUTH = '''"""Test configuration and fixtures."""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from db.base import Base
from dependencies.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user_create_data() -> dict:
    """Sample user creation data."""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
    }


@pytest.fixture
def user_update_data() -> dict:
    """Sample user update data."""
    return {"username": "updateduser"}
'''

# tests/conftest.py - Comprehensive test fixtures (with database and auth)
CONFTEST = '''"""Test configuration and fixtures."""

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from main import app
from db.base import Base
from dependencies.db import get_db
from models.user import User
from core.security import get_password_hash


# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with connection pooling for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(db_session: Session) -> User:
    """Create an admin test user in the database."""
    user = User(
        email="admin@example.com",
        username="adminuser",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, test_user: User) -> dict:
    """Get authentication headers for test user."""
    # Login to get token
    response = client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "testpassword123"},
    )
    assert response.status_code == 200
    
    tokens = response.json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture(scope="function")
def admin_auth_headers(client: TestClient, admin_user: User) -> dict:
    """Get authentication headers for admin user."""
    # Login to get token
    response = client.post(
        "/auth/login",
        data={"username": admin_user.email, "password": "adminpassword123"},
    )
    assert response.status_code == 200
    
    tokens = response.json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# Test data factories
@pytest.fixture
def user_create_data() -> dict:
    """Sample user creation data."""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
    }


@pytest.fixture
def user_update_data() -> dict:
    """Sample user update data."""
    return {"username": "updateduser"}
'''

# tests/test_health.py - Health endpoint tests (no database)
TEST_HEALTH_SIMPLE = '''"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test suite for health check endpoint."""

    def test_health_check_success(self, client: TestClient):
        """Test that health check returns successful status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data

        health_data = data["data"]
        assert "app_name" in health_data
        assert "app_version" in health_data
        assert "environment" in health_data

    def test_root_endpoint(self, client: TestClient):
        """Test that root endpoint returns application info."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data

        root_data = data["data"]
        assert "app_name" in root_data
        assert "app_version" in root_data
'''

# tests/test_health.py - Health endpoint tests (with database)
TEST_HEALTH = '''"""Tests for health check endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test suite for health check endpoint."""
    
    def test_health_check_success(self, client: TestClient):
        """Test that health check returns successful status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert "data" in data
        assert "message" in data
        
        # Check health data
        health_data = data["data"]
        assert "app_name" in health_data
        assert "app_version" in health_data
        assert "environment" in health_data
        assert "database" in health_data
        
        # Check database status
        db_status = health_data["database"]
        assert db_status["status"] == "healthy"
        assert "Database connection successful" in db_status["message"]
    
    def test_root_endpoint(self, client: TestClient):
        """Test that root endpoint returns application info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        root_data = data["data"]
        assert "app_name" in root_data
        assert "app_version" in root_data


class TestHealthWithDatabaseIssues:
    """Test health check with database problems."""
    
    def test_health_check_database_down(self, client: TestClient, db_session, monkeypatch):
        """Test health check when database is unavailable."""
        # Mock database to raise an exception
        def mock_execute(*args, **kwargs):
            raise Exception("Database connection failed")
        
        monkeypatch.setattr(db_session, "execute", mock_execute)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return 200 but with unhealthy status
        health_data = data["data"]
        assert health_data["database"]["status"] == "unhealthy"
        assert "failed" in health_data["database"]["message"].lower()
'''

# tests/test_users.py - User CRUD tests (no auth)
TEST_USERS_NO_AUTH = '''"""Tests for user CRUD endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestUserCreation:
    """Test suite for user creation."""

    def test_create_user_success(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test successful user creation."""
        response = client.post("/users/", json=user_create_data)

        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        assert data["message"] == "User created successfully"

        user_data = data["data"]
        assert user_data["email"] == user_create_data["email"]
        assert user_data["username"] == user_create_data["username"]
        assert "id" in user_data

    def test_create_user_duplicate_email(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test that duplicate email is rejected."""
        client.post("/users/", json=user_create_data)
        response = client.post("/users/", json=user_create_data)

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"]

    def test_create_user_duplicate_username(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test that duplicate username is rejected."""
        duplicate_data = {
            "email": "different@example.com",
            "username": user_create_data["username"],
            "password": "password123",
        }
        client.post("/users/", json=user_create_data)
        response = client.post("/users/", json=duplicate_data)

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"]


class TestUserRetrieval:
    """Test suite for user retrieval."""

    def test_list_users_success(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test successful user listing."""
        client.post("/users/", json=user_create_data)
        response = client.get("/users/")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_get_user_by_id_success(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test getting a user by ID."""
        create = client.post("/users/", json=user_create_data)
        user_id = create.json()["data"]["id"]

        response = client.get(f"/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == user_id
        assert data["data"]["email"] == user_create_data["email"]

    def test_get_user_not_found(self, client: TestClient):
        """Test getting a non-existent user."""
        response = client.get("/users/99999")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False


class TestUserUpdate:
    """Test suite for user updates."""

    def test_update_user_success(
        self,
        client: TestClient,
        user_create_data: dict,
        user_update_data: dict,
    ):
        """Test updating a user."""
        create = client.post("/users/", json=user_create_data)
        user_id = create.json()["data"]["id"]

        response = client.patch(
            f"/users/{user_id}",
            json=user_update_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["username"] == user_update_data["username"]


class TestUserDeletion:
    """Test suite for user deletion."""

    def test_delete_user_success(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test deleting a user."""
        create = client.post("/users/", json=user_create_data)
        user_id = create.json()["data"]["id"]

        response = client.delete(f"/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_soft_delete_hides_user(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test that soft-deleted user is not found."""
        create = client.post("/users/", json=user_create_data)
        user_id = create.json()["data"]["id"]

        client.delete(f"/users/{user_id}")
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 404

    def test_delete_nonexistent_user(self, client: TestClient):
        """Test deleting a non-existent user."""
        response = client.delete("/users/99999")
        assert response.status_code == 404
'''

# tests/test_users.py - User CRUD tests (with auth)
TEST_USERS = '''"""Tests for user CRUD endpoints."""

import pytest
from fastapi.testclient import TestClient
from models.user import User


class TestUserCreation:
    """Test suite for user creation."""
    
    def test_create_user_success(
        self,
        client: TestClient,
        user_create_data: dict,
    ):
        """Test successful user creation."""
        response = client.post("/users/", json=user_create_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "User created successfully"
        
        user_data = data["data"]
        assert user_data["email"] == user_create_data["email"]
        assert user_data["username"] == user_create_data["username"]
        assert "id" in user_data
        assert "hashed_password" not in user_data  # Password should not be returned
    
    def test_create_user_duplicate_email(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test that duplicate email is rejected."""
        duplicate_data = {
            "email": test_user.email,
            "username": "differentuser",
            "password": "password123",
        }
        
        response = client.post("/users/", json=duplicate_data)
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"]
    
    def test_create_user_duplicate_username(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test that duplicate username is rejected."""
        duplicate_data = {
            "email": "different@example.com",
            "username": test_user.username,
            "password": "password123",
        }
        
        response = client.post("/users/", json=duplicate_data)
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"]


class TestUserRetrieval:
    """Test suite for user retrieval."""
    
    def test_list_users_requires_auth(self, client: TestClient):
        """Test that listing users requires authentication."""
        response = client.get("/users/")
        assert response.status_code == 401
    
    def test_list_users_success(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
    ):
        """Test successful user listing."""
        response = client.get("/users/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        
        # Should have at least one user (test_user)
        assert data["total"] >= 1
        assert len(data["data"]) >= 1
    
    def test_list_users_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
    ):
        """Test user listing with pagination."""
        # Create multiple users
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password="hashed",
                is_active=True,
            )
            db_session.add(user)
        db_session.commit()
        
        # Test pagination
        response = client.get(
            "/users/?skip=0&limit=3",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 3
        assert data["per_page"] == 3
        assert data["total"] >= 5
    
    def test_get_user_by_id_success(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
    ):
        """Test getting a user by ID."""
        response = client.get(
            f"/users/{test_user.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email
    
    def test_get_user_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test getting a non-existent user."""
        response = client.get(
            "/users/99999",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]["message"].lower()
    
    def test_get_current_user(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
    ):
        """Test getting current user info."""
        response = client.get("/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["data"]["id"] == test_user.id
        assert data["data"]["email"] == test_user.email


class TestUserUpdate:
    """Test suite for user updates."""
    
    def test_update_own_profile(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
        user_update_data: dict,
    ):
        """Test updating own profile."""
        response = client.patch(
            f"/users/{test_user.id}",
            json=user_update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "User updated successfully"
        assert data["data"]["username"] == user_update_data["username"]
    
    def test_update_other_user_forbidden(
        self,
        client: TestClient,
        test_user: User,
        admin_user: User,
        auth_headers: dict,
        user_update_data: dict,
    ):
        """Test that regular user cannot update other users."""
        response = client.patch(
            f"/users/{admin_user.id}",
            json=user_update_data,
            headers=auth_headers,
        )
        
        assert response.status_code == 403
        data = response.json()
        assert data["success"] is False
        assert "own profile" in data["error"]["message"].lower()
    
    def test_admin_update_any_user(
        self,
        client: TestClient,
        test_user: User,
        admin_auth_headers: dict,
        user_update_data: dict,
    ):
        """Test that admin can update any user."""
        response = client.patch(
            f"/users/{test_user.id}",
            json=user_update_data,
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestUserDeletion:
    """Test suite for user deletion."""
    
    def test_delete_own_account(
        self,
        client: TestClient,
        test_user: User,
        auth_headers: dict,
    ):
        """Test deleting own account."""
        response = client.delete(
            f"/users/{test_user.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User deleted successfully"
    
    def test_delete_other_user_forbidden(
        self,
        client: TestClient,
        admin_user: User,
        auth_headers: dict,
    ):
        """Test that regular user cannot delete other users."""
        response = client.delete(
            f"/users/{admin_user.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 403
    
    def test_admin_delete_any_user(
        self,
        client: TestClient,
        test_user: User,
        admin_auth_headers: dict,
    ):
        """Test that admin can delete any user."""
        response = client.delete(
            f"/users/{test_user.id}",
            headers=admin_auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
'''

# tests/test_auth.py - Authentication tests
TEST_AUTH = '''"""Tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from models.user import User
from core.security import get_password_hash


class TestLogin:
    """Test suite for login endpoint."""
    
    def test_login_success_with_email(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test successful login with email."""
        response = client.post(
            "/auth/login",
            data={"username": test_user.email, "password": "testpassword123"},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "Login successful"
        
        tokens = data["data"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
    
    def test_login_success_with_username(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test successful login with username."""
        response = client.post(
            "/auth/login",
            data={"username": test_user.username, "password": "testpassword123"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
    
    def test_login_wrong_password(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test login with incorrect password."""
        response = client.post(
            "/auth/login",
            data={"username": test_user.email, "password": "wrongpassword"},
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "incorrect" in data["error"]["message"].lower()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@example.com", "password": "password123"},
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False


class TestRegister:
    """Test suite for registration endpoint."""
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "User registered successfully"
        assert data["data"]["email"] == user_data["email"]
    
    def test_register_duplicate_email(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test registration with duplicate email."""
        user_data = {
            "email": test_user.email,
            "username": "differentuser",
            "password": "password123",
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["error"]["message"]


class TestTokenRefresh:
    """Test suite for token refresh endpoint."""
    
    def test_refresh_token_success(
        self,
        client: TestClient,
        test_user: User,
    ):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/auth/login",
            data={"username": test_user.email, "password": "testpassword123"},
        )
        assert login_response.status_code == 200
        
        refresh_token = login_response.json()["data"]["refresh_token"]
        
        # Refresh the token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["message"] == "Token refreshed successfully"
        
        tokens = data["data"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
    
    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "invalid" in data["error"]["message"].lower() or "expired" in data["error"]["message"].lower()


class TestLogout:
    """Test suite for logout endpoint."""
    
    def test_logout_success(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test successful logout."""
        response = client.post("/auth/logout", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "logout successful" in data["message"].lower()
    
    def test_logout_requires_auth(self, client: TestClient):
        """Test that logout requires authentication."""
        response = client.post("/auth/logout")
        assert response.status_code == 401
'''
