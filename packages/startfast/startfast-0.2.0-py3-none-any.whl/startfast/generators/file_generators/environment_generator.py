"""Environment Generator - Generates .env and environment configuration files"""

from ...generators.base_generator import BaseGenerator


class EnvironmentGenerator(BaseGenerator):
    """Generates environment configuration files"""

    def generate(self):
        """Generate .env file"""
        env_content = self._get_env_template()
        self.write_file(f"{self.config.path}/.env", env_content)

        # Also generate .env.example
        env_example_content = self._get_env_example_template()
        self.write_file(f"{self.config.path}/.env.example", env_example_content)

    def _get_env_template(self) -> str:
        """Get environment template with actual values"""
        template = f"""# Application Configuration
APP_NAME={self.config.name}
APP_VERSION=1.0.0
DEBUG=true
API_PREFIX=/api/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
{self._get_database_env_vars()}

# Security Configuration
{self._get_security_env_vars()}

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=

{self._get_additional_env_vars()}
"""
        return template

    def _get_env_example_template(self) -> str:
        """Get environment example template"""
        template = f"""# Application Configuration
APP_NAME={self.config.name}
APP_VERSION=1.0.0
DEBUG=false
API_PREFIX=/api/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
{self._get_database_env_vars_example()}

# Security Configuration
{self._get_security_env_vars_example()}

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=

{self._get_additional_env_vars_example()}
"""
        return template

    def _get_database_env_vars(self) -> str:
        """Get database environment variables"""
        from ...core.config import DatabaseType

        if self.config.database_type == DatabaseType.SQLITE:
            return "DATABASE_URL=sqlite+aiosqlite:///./app.db"
        elif self.config.database_type == DatabaseType.POSTGRESQL:
            return """DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=dbname
DATABASE_USER=user
DATABASE_PASSWORD=password"""
            
        elif self.config.database_type == DatabaseType.MYSQL:
            return """DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=dbname
DATABASE_USER=user
DATABASE_PASSWORD=password"""
            
        elif self.config.database_type == DatabaseType.MONGODB:
            return """MONGODB_URL=mongodb://localhost:27017/dbname
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_NAME=dbname"""
        return ""

    def _get_database_env_vars_example(self) -> str:
        """Get database environment variables for example file"""
        from ...core.config import DatabaseType

        if self.config.database_type == DatabaseType.SQLITE:
            return "DATABASE_URL=sqlite+aiosqlite:///./app.db"
        elif self.config.database_type == DatabaseType.POSTGRESQL:
            return """DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password"""
            
        elif self.config.database_type == DatabaseType.MYSQL:
            return """DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password"""
            
        elif self.config.database_type == DatabaseType.MONGODB:
            return """MONGODB_URL=mongodb://localhost:27017/dbname
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_NAME=your_db_name"""
        return ""

    def _get_security_env_vars(self) -> str:
        """Get security environment variables"""
        from ...core.config import AuthType

        if self.config.auth_type == AuthType.JWT:
            return """SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30"""
        elif self.config.auth_type == AuthType.OAUTH2:
            return """SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OAUTH2_CLIENT_ID=your-oauth2-client-id
OAUTH2_CLIENT_SECRET=your-oauth2-client-secret"""
        elif self.config.auth_type == AuthType.API_KEY:
            return """API_KEY=your-api-key-here-change-in-production"""
        return ""

    def _get_security_env_vars_example(self) -> str:
        """Get security environment variables for example file"""
        from ...core.config import AuthType

        if self.config.auth_type == AuthType.JWT:
            return """SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30"""
        elif self.config.auth_type == AuthType.OAUTH2:
            return """SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OAUTH2_CLIENT_ID=your-oauth2-client-id
OAUTH2_CLIENT_SECRET=your-oauth2-client-secret"""
        elif self.config.auth_type == AuthType.API_KEY:
            return """API_KEY=your-api-key-here-change-in-production"""
        return ""

    def _get_additional_env_vars(self) -> str:
        """Get additional environment variables based on configuration"""
        vars_list = []

        if self.config.include_celery:
            vars_list.append(
                """# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0"""
            )

        if self.config.include_monitoring:
            vars_list.append(
                """# Monitoring Configuration
SENTRY_DSN=
PROMETHEUS_PORT=9090"""
            )

        return "\n\n".join(vars_list)

    def _get_additional_env_vars_example(self) -> str:
        """Get additional environment variables for example file"""
        vars_list = []

        if self.config.include_celery:
            vars_list.append(
                """# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0"""
            )

        if self.config.include_monitoring:
            vars_list.append(
                """# Monitoring Configuration
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_PORT=9090"""
            )

        return "\n\n".join(vars_list)
