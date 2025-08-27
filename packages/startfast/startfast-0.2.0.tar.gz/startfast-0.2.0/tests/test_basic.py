"""Test configuration and CLI functionality"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.startfast.core.config import (
    ProjectConfig,
    ProjectType,
    DatabaseType,
    AuthType,
)
from src.startfast.generators.project_generator import ProjectGenerator


class TestProjectConfig:
    """Test ProjectConfig class"""

    def test_project_config_creation(self):
        """Test creating a basic project configuration"""
        config = ProjectConfig(
            name="test-project",
            path="/tmp/test-project",
            project_type=ProjectType.API,
            database_type=DatabaseType.SQLITE,
            auth_type=AuthType.JWT,
        )

        assert config.name == "test-project"
        assert config.path == "/tmp/test-project"
        assert config.project_type == ProjectType.API
        assert config.database_type == DatabaseType.SQLITE
        assert config.auth_type == AuthType.JWT
        assert config.include_docker is True  # Default value

    def test_project_config_validation(self):
        """Test project configuration validation"""
        with pytest.raises(ValueError):
            ProjectConfig(
                name="",  # Empty name should raise error
                path="/tmp/test",
                project_type=ProjectType.API,
                database_type=DatabaseType.SQLITE,
                auth_type=AuthType.JWT,
            )


class TestProjectGenerator:
    """Test ProjectGenerator class"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir) / "test-project"

    def teardown_method(self):
        """Clean up test environment"""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_project_generator_initialization(self):
        """Test ProjectGenerator initialization"""
        config = ProjectConfig(
            name="test-project",
            path=str(self.project_path),
            project_type=ProjectType.API,
            database_type=DatabaseType.SQLITE,
            auth_type=AuthType.JWT,
        )

        generator = ProjectGenerator(config)
        assert generator.config == config
        assert len(generator.generators) > 0

    def test_project_structure_creation(self):
        """Test basic project structure creation"""
        config = ProjectConfig(
            name="test-project",
            path=str(self.project_path),
            project_type=ProjectType.API,
            database_type=DatabaseType.SQLITE,
            auth_type=AuthType.JWT,
        )

        generator = ProjectGenerator(config)
        generator._create_project_structure()

        # Check if basic directories were created
        assert self.project_path.exists()
        assert (self.project_path / "app").exists()
        assert (self.project_path / "app" / "__init__.py").exists()
        assert (self.project_path / "tests").exists()
        assert (self.project_path / "docs").exists()


if __name__ == "__main__":
    pytest.main([__file__])
