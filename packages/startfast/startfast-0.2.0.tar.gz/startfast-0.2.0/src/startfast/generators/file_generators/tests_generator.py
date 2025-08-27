"""Tests Generator - Generates test files"""

from ...generators.base_generator import BaseGenerator


class TestsGenerator(BaseGenerator):
    """Generates test files"""

    def should_generate(self):
        return self.config.include_tests

    def generate(self):
        """Generate test files"""
        if not self.config.include_tests:
            return

        # Generate conftest.py
        conftest_content = self._get_conftest_template()
        self.write_file(f"{self.config.path}/tests/conftest.py", conftest_content)

        # Generate test_main.py
        test_main_content = self._get_test_main_template()
        self.write_file(f"{self.config.path}/tests/test_main.py", test_main_content)

        # Generate test_api.py
        test_api_content = self._get_test_api_template()
        self.write_file(f"{self.config.path}/tests/test_api.py", test_api_content)

        # Generate pytest.ini
        pytest_ini_content = self._get_pytest_ini_template()
        self.write_file(f"{self.config.path}/pytest.ini", pytest_ini_content)

    def _get_conftest_template(self) -> str:
        """Get conftest.py template"""
        template = '''"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authentication headers fixture"""
    # Add authentication logic here if needed
    return {"Authorization": "Bearer test-token"}
'''
        return template

    def _get_test_main_template(self) -> str:
        """Get test_main.py template"""
        template = f'''"""
Tests for main application
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Welcome to {self.config.name}!"


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "{self.config.name}"


def test_docs_endpoint(client: TestClient):
    """Test docs endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint(client: TestClient):
    """Test OpenAPI endpoint"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
'''
        return template

    def _get_test_api_template(self) -> str:
        """Get test_api.py template"""
        template = '''"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient


def test_api_v1_base(client: TestClient):
    """Test API v1 base endpoint"""
    response = client.get("/api/v1/")
    # Add appropriate assertions based on your API structure
    pass


# Add more API tests here based on your specific endpoints
'''
        return template

    def _get_pytest_ini_template(self) -> str:
        """Get pytest.ini template"""
        template = f"""[tool:pytest]
minversion = 6.0
addopts = -ra -q --strict-markers
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
"""
        return template
