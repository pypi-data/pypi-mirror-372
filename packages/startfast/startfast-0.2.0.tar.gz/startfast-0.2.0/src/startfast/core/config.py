"""
Configuration classes and enums for StartFast project generator
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Available project types"""

    API = "api"
    CRUD = "crud"


class DatabaseType(Enum):
    """Database options"""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"


class AuthType(Enum):
    """Authentication options"""

    NONE = "none"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    API_KEY = "api-key"


@dataclass
class ProjectConfig:
    """Configuration for project generation"""

    name: str
    path: str
    project_type: ProjectType
    database_type: DatabaseType
    auth_type: AuthType
    include_docker: bool = True
    include_tests: bool = True
    include_docs: bool = True
    include_monitoring: bool = False
    include_celery: bool = False
    python_version: str = "3.11"

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.name:
            raise ValueError("Project name cannot be empty")

        if not self.path:
            raise ValueError("Project path cannot be empty")

        # Ensure enum types
        if isinstance(self.project_type, str):
            self.project_type = ProjectType(self.project_type)
        if isinstance(self.database_type, str):
            self.database_type = DatabaseType(self.database_type)
        if isinstance(self.auth_type, str):
            self.auth_type = AuthType(self.auth_type)
