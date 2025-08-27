"""
Main Project Generator
Orchestrates the creation of FastAPI projects
"""

import os
import shutil
from typing import Dict, Any, List
from pathlib import Path
import logging

from .base_generator import BaseGenerator
from ..core.config import ProjectConfig

logger = logging.getLogger(__name__)


class ProjectGenerator(BaseGenerator):
    """Main project generator that orchestrates the entire project creation"""

    def __init__(self, config: ProjectConfig):
        super().__init__(config)
        self._setup_generators()

    def _setup_generators(self):
        """Initialize all file generators"""
        # Import generators here to avoid circular imports
        from .file_generators.requirements_generator import RequirementsGenerator
        from .file_generators.environment_generator import EnvironmentGenerator
        from .file_generators.main_app_generator import MainAppGenerator
        from .file_generators.config_generator import ConfigGenerator
        from .file_generators.database_generator import DatabaseGenerator
        from .file_generators.auth_generator import AuthGenerator
        from .file_generators.api_generator import APIGenerator
        from .file_generators.schemas_generator import SchemasGenerator
        from .file_generators.utils_generator import UtilsGenerator
        from .file_generators.docker_generator import DockerGenerator
        from .file_generators.tests_generator import TestsGenerator
        from .file_generators.docs_generator import DocsGenerator

        self.generators = {
            "requirements": RequirementsGenerator(self.config),
            "environment": EnvironmentGenerator(self.config),
            "main": MainAppGenerator(self.config),
            "config": ConfigGenerator(self.config),
            "database": DatabaseGenerator(self.config),
            "auth": AuthGenerator(self.config),
            "api": APIGenerator(self.config),
            "schemas": SchemasGenerator(self.config),
            "utils": UtilsGenerator(self.config),
            "docker": DockerGenerator(self.config),
            "tests": TestsGenerator(self.config),
            "docs": DocsGenerator(self.config),
        }

        if self.config.include_monitoring:
            from .file_generators.monitoring_generator import MonitoringGenerator

            self.generators["monitoring"] = MonitoringGenerator(self.config)

        if self.config.include_celery:
            from .file_generators.celery_generator import CeleryGenerator

            self.generators["celery"] = CeleryGenerator(self.config)

    def generate(self):
        """Generate the complete project"""
        logger.info(f"Generating FastAPI project: {self.config.name}")

        # Create project directory
        self._create_project_structure()

        # Generate all files
        self._generate_files()

        logger.info("Project generation completed successfully!")

    def _create_project_structure(self):
        """Create the basic project directory structure"""
        project_path = Path(self.config.path)

        # Remove existing directory if it exists
        if project_path.exists():
            shutil.rmtree(project_path)

        # Create main project directories
        directories = [
            "app",
            "app/api",
            "app/api/v1",
            "app/core",
            "app/db",
            "app/models",
            "app/schemas",
            "app/services",
            "app/utils",
            "tests",
            "docs",
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

        # Create __init__.py files
        init_files = [
            "app/__init__.py",
            "app/api/__init__.py",
            "app/api/v1/__init__.py",
            "app/core/__init__.py",
            "app/db/__init__.py",
            "app/models/__init__.py",
            "app/schemas/__init__.py",
            "app/services/__init__.py",
            "app/utils/__init__.py",
            "tests/__init__.py",
        ]

        for init_file in init_files:
            (project_path / init_file).touch()

    def _generate_files(self):
        """Generate all project files using the configured generators"""
        for name, generator in self.generators.items():
            if generator.should_generate():
                logger.info(f"Generating {name} files...")
                try:
                    generator.generate()
                except Exception as e:
                    logger.error(f"Failed to generate {name} files: {e}")
                    raise

    def get_generation_summary(self) -> Dict[str, Any]:
        """Get a summary of what was generated"""
        return {
            "project_name": self.config.name,
            "project_path": self.config.path,
            "project_type": self.config.project_type.value,
            "database_type": self.config.database_type.value,
            "auth_type": self.config.auth_type.value,
            "generators_used": list(self.generators.keys()),
            "features": {
                "docker": self.config.include_docker,
                "tests": self.config.include_tests,
                "docs": self.config.include_docs,
                "monitoring": self.config.include_monitoring,
                "celery": self.config.include_celery,
            },
        }
