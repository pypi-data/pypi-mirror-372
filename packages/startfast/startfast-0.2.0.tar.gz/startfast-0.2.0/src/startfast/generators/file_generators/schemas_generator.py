"""Schemas Generator - Generates Pydantic schemas"""

from ...generators.base_generator import BaseGenerator


class SchemasGenerator(BaseGenerator):
    """Generates Pydantic schema files"""

    def generate(self):
        """Generate schema files"""
        # Generate base schemas
        base_schemas_content = self._get_base_schemas_template()
        self.write_file(
            f"{self.config.path}/app/schemas/__init__.py", base_schemas_content
        )  # Generate auth schemas if auth is enabled
        if self.config.auth_type.value != "none":
            user_schemas_content = self._get_user_schemas_template()
            self.write_file(
                f"{self.config.path}/app/schemas/user.py", user_schemas_content
            )

            # Also create auth.py that imports from user.py for convenience
            auth_schemas_content = self._get_auth_schemas_template()
            self.write_file(
                f"{self.config.path}/app/schemas/auth.py", auth_schemas_content
            )

    def _get_base_schemas_template(self) -> str:
        """Get base schemas template"""
        template = '''"""
Base schemas for Pydantic models
"""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema with common fields"""
    
    class Config:
        from_attributes = True
        populate_by_name = True


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IDMixin(BaseModel):
    """Mixin for ID field"""
    id: Optional[int] = None


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response schema"""
    items: List[Any]
    pagination: dict


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    errors: Optional[List[str]] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: datetime
    details: Optional[dict] = None
'''
        return template

    def _get_user_schemas_template(self) -> str:
        """Get user schemas template"""
        template = '''"""
User schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from . import BaseSchema, TimestampMixin, IDMixin


class UserBase(BaseSchema):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase, IDMixin, TimestampMixin):
    """User schema for database representation"""
    hashed_password: str


class User(UserBase, IDMixin, TimestampMixin):
    """User schema for API responses"""
    pass


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[int] = None
    email: Optional[str] = None
'''
        return template

    def _get_auth_schemas_template(self) -> str:
        """Get auth schemas template that imports from user.py for convenience"""
        template = '''"""
Auth schemas - Convenience imports from user schemas
"""

# Import all auth-related schemas from user.py for convenience
from .user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    User,
    UserLogin,
    Token,
    TokenData
)

__all__ = [
    "UserBase",
    "UserCreate", 
    "UserUpdate",
    "UserInDB",
    "User",
    "UserLogin",
    "Token",
    "TokenData"
]
'''
        return template
