"""
Base Generator Class
Provides common functionality for all generators
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from ..core.config import ProjectConfig
import logging

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """Base class for all file generators"""

    def __init__(self, config: ProjectConfig):
        self.config = config

    def should_generate(self) -> bool:
        """Determine if this generator should run based on configuration"""
        return True

    @abstractmethod
    def generate(self):
        """Generate the files for this component"""
        pass

    def write_file(self, file_path: str, content: str):
        """Write content to a file, creating directories if needed"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def get_template_vars(self) -> Dict[str, Any]:
        """Get template variables for string formatting"""
        return {
            "project_name": self.config.name,
            "project_name_snake": self.config.name.lower().replace("-", "_"),
            "project_name_pascal": "".join(
                word.capitalize()
                for word in self.config.name.replace("-", "_").split("_")
            ),
            "database_type": self.config.database_type.value,
            "auth_type": self.config.auth_type.value,
            "python_version": self.config.python_version,
            "include_docker": self.config.include_docker,
            "include_tests": self.config.include_tests,
            "include_docs": self.config.include_docs,
            "include_monitoring": self.config.include_monitoring,
            "include_celery": self.config.include_celery,
        }

    def format_template(self, template: str) -> str:
        """Format a template string with project variables"""
        return template.format(**self.get_template_vars())

    def get_database_imports(self) -> dict:
        """Get database-specific imports based on configuration"""
        from ..core.config import DatabaseType

        if self.config.database_type in [
            DatabaseType.SQLITE,
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
        ]:
            return {
                "session_import": "from sqlalchemy.ext.asyncio import AsyncSession",
                "session_type": "AsyncSession",
                "base_import": "from app.db.base import BaseModel",
                "dependency_import": "from app.db.database import get_db",
                "dependency_type": "AsyncSession = Depends(get_db)",
            }
        elif self.config.database_type == DatabaseType.MONGODB:
            return {
                "session_import": (
                    "from motor.motor_asyncio import AsyncIOMotorClient"
                ),
                "session_type": (
                    "AsyncIOMotorClient"
                ),
                "base_import": (
                    "from beanie import Document"
                ),
                "dependency_import": "from app.db.database import get_db",
                "dependency_type": (
                    "AsyncIOMotorClient = Depends(get_db)"
                ),
            }

        # Default fallback
        return {
            "session_import": "from sqlalchemy.orm import Session",
            "session_type": "Session",
            "base_import": "from app.db.base import BaseModel",
            "dependency_import": "from app.db.database import get_db",
            "dependency_type": "Session = Depends(get_db)",
        }

    def get_model_base_class(self) -> str:
        """Get the appropriate base class for models"""
        from ..core.config import DatabaseType

        if self.config.database_type in [
            DatabaseType.SQLITE,
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
        ]:
            return "BaseModel"
        elif self.config.database_type == DatabaseType.MONGODB:
            return "Document"

        return "BaseModel"

    def should_generate_sqlalchemy_files(self) -> bool:
        """Check if SQLAlchemy files should be generated"""
        from ..core.config import DatabaseType

        return self.config.database_type in [
            DatabaseType.SQLITE,
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
        ]

    def should_generate_auth_models(self) -> bool:
        """Check if auth models should be generated (requires SQL database)"""
        from ..core.config import AuthType

        return (
            self.config.auth_type != AuthType.NONE
            and self.should_generate_sqlalchemy_files()
        )
