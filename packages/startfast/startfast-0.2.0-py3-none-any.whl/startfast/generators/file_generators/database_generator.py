"""
Database Generator
Generates database configuration and connection files
"""

from ...generators.base_generator import BaseGenerator
from ...core.config import DatabaseType


class DatabaseGenerator(BaseGenerator):
    """Generates database configuration files"""

    def generate(self):
        """Generate database files"""
        if self.config.database_type in [
            DatabaseType.SQLITE,
            DatabaseType.POSTGRESQL,
            DatabaseType.MYSQL,
        ]:
            self._generate_sqlalchemy_files()
        elif self.config.database_type == DatabaseType.MONGODB:
            self._generate_mongodb_files()
    
    def _generate_sqlalchemy_files(self):
        """Generate SQLAlchemy database files"""
        database_content = self._get_sqlalchemy_template()
        self.write_file(f"{self.config.path}/app/db/database.py", database_content)

        base_content = self._get_base_model_template()
        self.write_file(f"{self.config.path}/app/db/base.py", base_content)

    def _generate_mongodb_files(self):
        """Generate MongoDB database files"""
        database_content = self._get_mongodb_template()
        self.write_file(f"{self.config.path}/app/db/database.py", database_content)

    def _get_sqlalchemy_template(self) -> str:
        """Get SQLAlchemy database template"""
        template = '''"""
Async SQLAlchemy Database Configuration
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    from app.db.base import Base
    
    async with engine.begin() as conn:
        # Import all models to ensure they are registered with Base
        import app.models.auth 
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all tables - useful for testing"""
    from app.db.base import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
'''
        return template

    def _get_base_model_template(self) -> str:
        """Get base model template"""
        template = '''"""
Base Model Classes
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from app.db.database import Base


class TimestampMixin:
    """Mixin for timestamp fields"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(Base, TimestampMixin):
    """Base model with common fields"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
'''

        return template

    def _get_mongodb_template(self) -> str:
        """Get MongoDB database template"""
        template = '''"""
Async MongoDB Database Configuration
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
import asyncio

# MongoDB client
client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Create database connection"""
    global client
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(database=client.get_default_database(), document_models=[])


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()


async def get_database():
    """Get database instance"""
    return client.get_default_database()
'''
        return template
