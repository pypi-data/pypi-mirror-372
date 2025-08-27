"""Docker Generator - Generates Docker configuration"""

from ...generators.base_generator import BaseGenerator


class DockerGenerator(BaseGenerator):
    """Generates Docker files"""

    def should_generate(self):
        return self.config.include_docker

    def generate(self):
        """Generate Docker files"""
        if not self.config.include_docker:
            return

        # Generate Dockerfile
        dockerfile_content = self._get_dockerfile_template()
        self.write_file(f"{self.config.path}/Dockerfile", dockerfile_content)

        # Generate docker-compose.yml
        compose_content = self._get_docker_compose_template()
        self.write_file(f"{self.config.path}/docker-compose.yml", compose_content)

        # Generate .dockerignore
        dockerignore_content = self._get_dockerignore_template()
        self.write_file(f"{self.config.path}/.dockerignore", dockerignore_content)

    def _get_dockerfile_template(self) -> str:
        """Get Dockerfile template"""
        template = f"""FROM python:{self.config.python_version}-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=5 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        return template

    def _get_docker_compose_template(self) -> str:
        """Get docker-compose.yml template"""
        template = f"""version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
    depends_on:
{self._get_database_service_depends()}
    volumes:
      - ./app:/app/app
    restart: unless-stopped

{self._get_database_services()}

{self._get_additional_services()}

volumes:
{self._get_volumes()}

networks:
  default:
    name: {self.config.name.lower().replace("-", "_")}_network
"""
        return template

    def _get_database_service_depends(self) -> str:
        """Get database service dependencies"""
        from ...core.config import DatabaseType

        if self.config.database_type == DatabaseType.POSTGRESQL:
            return "      - postgres"
        elif self.config.database_type == DatabaseType.MYSQL:
            return "      - mysql"
        elif self.config.database_type == DatabaseType.MONGODB:
            return "      - mongodb"
        return ""

    def _get_database_services(self) -> str:
        """Get database services"""
        from ...core.config import DatabaseType

        if self.config.database_type == DatabaseType.POSTGRESQL:
            return """  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: dbname
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped"""

        elif self.config.database_type == DatabaseType.MYSQL:
            return """  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: dbname
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped"""

        elif self.config.database_type == DatabaseType.MONGODB:
            return """  mongodb:
    image: mongo:6.0
    environment:
      MONGO_INITDB_DATABASE: dbname
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped"""

        return ""

    def _get_additional_services(self) -> str:
        """Get additional services"""
        services = []

        if self.config.include_celery:
            services.append(
                """  celery:
    build: .
    command: celery -A app.core.celery worker --loglevel=info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ./app:/app/app
    restart: unless-stopped"""
            )

        if self.config.include_monitoring:
            services.append(
                """  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped"""
            )

        return "\n\n".join(services)

    def _get_volumes(self) -> str:
        """Get Docker volumes"""
        from ...core.config import DatabaseType

        volumes = []

        if self.config.database_type == DatabaseType.POSTGRESQL:
            volumes.append("  postgres_data:")
        elif self.config.database_type == DatabaseType.MYSQL:
            volumes.append("  mysql_data:")
        elif self.config.database_type == DatabaseType.MONGODB:
            volumes.append("  mongodb_data:")

        return "\n".join(volumes)

    def _get_dockerignore_template(self) -> str:
        """Get .dockerignore template"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
docs/
*.md

# Tests
tests/
pytest.ini
.coverage
htmlcov/

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Docker
Dockerfile
docker-compose*.yml
.dockerignore
"""
