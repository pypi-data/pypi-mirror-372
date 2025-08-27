"""
Authentication Generator
Generates authentication and security files
"""

from ...generators.base_generator import BaseGenerator
from ...core.config import AuthType


class AuthGenerator(BaseGenerator):
    """Generates authentication files"""

    def should_generate(self) -> bool:
        """Only generate if authentication is enabled"""
        return self.config.auth_type != AuthType.NONE

    def generate(self):
        """Generate authentication files"""
        # Generate security.py
        security_content = self._get_security_template()
        self.write_file(f"{self.config.path}/app/core/security.py", security_content)

        # Generate auth models and schemas only if using SQL database and JWT/OAuth2
        if (
            self.config.auth_type in [AuthType.JWT, AuthType.OAUTH2]
            and self.should_generate_sqlalchemy_files()
        ):
            auth_models_content = self._get_auth_models_template()
            self.write_file(
                f"{self.config.path}/app/models/auth.py", auth_models_content
            )

            auth_schemas_content = self._get_auth_schemas_template()
            self.write_file(
                f"{self.config.path}/app/schemas/auth.py", auth_schemas_content
            )
        elif self.config.auth_type in [AuthType.JWT, AuthType.OAUTH2]:
            # For NoSQL databases (MongoDB), generate simplified auth schemas
            auth_schemas_content = self._get_nosql_auth_schemas_template()
            self.write_file(
                f"{self.config.path}/app/schemas/auth.py", auth_schemas_content
            )

    def _get_security_template(self) -> str:
        """Get security template based on auth type"""
        if self.config.auth_type == AuthType.JWT:
            return self._get_jwt_template()
        elif self.config.auth_type == AuthType.OAUTH2:
            return self._get_oauth2_template()
        elif self.config.auth_type == AuthType.API_KEY:
            return self._get_api_key_template()
        return ""

    def _get_jwt_template(self) -> str:
        """Get JWT authentication template"""

        # Original SQL-based JWT template
        template = '''"""
JWT Authentication Security
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.auth import User
from app.schemas.auth import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update(dict(exp=expire))
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return TokenData(email=email)
    except JWTError:
        return None


{user_functions}


{authenticate_function}


{current_user_function}
'''

        user_functions = '''
async def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    from sqlalchemy import select
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(db: Session, email: str, password: str) -> User:
    """Create new user"""
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
'''

        authenticate_function = '''
async def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
'''

        current_user_function = '''
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = await get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user
'''
        return template.format(
            user_functions=user_functions,
            authenticate_function=authenticate_function,
            current_user_function=current_user_function,
        )

    def _get_oauth2_template(self) -> str:
        """Get OAuth2 authentication template"""
        if self.should_generate_sqlalchemy_files():
            # OAuth2 with database backend
            return self._get_oauth2_with_db_async_template()
        else:
            # OAuth2 without database (simple in-memory or external provider)
            return self._get_oauth2_simple_template()

    def _get_oauth2_with_db_async_template(self) -> str:
        """Get OAuth2 template with async database support"""
        template = '''"""
OAuth2 Authentication Security with Database
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.db.database import get_db
from app.models.auth import User
from app.schemas.auth import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme with token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return TokenData(user_id=int(user_id))
    except JWTError as e:
        print(f"JWT Error: {e}")  # Debugging line
        return None
    except Exception as e:
        print(f"Unexpected error in verify_token: {e}")  # Debugging line
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user_by_user_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by user ID"""
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, email: str, password: str) -> User:
    """Create new user"""
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Authenticate user with user ID and password"""
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from OAuth2 token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception

    user = await get_user_by_user_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

'''
        return template


    def _get_oauth2_simple_template(self) -> str:
        """Get simple OAuth2 template without database"""
        template = '''"""
OAuth2 Authentication Security (Simple)
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.config import settings

# OAuth2 scheme with token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/token")

# In-memory user store (replace with your preferred storage)
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        "disabled": False,
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user from fake database"""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return user_dict
    return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current authenticated user from OAuth2 token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Get current active user"""
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
'''

        return template

    def _get_api_key_template(self) -> str:
        """Get API Key authentication template"""
        template = '''"""
API Key Authentication Security
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)):
    """Validate API key"""
    # In production, store API keys in database or secure storage
    valid_api_keys = ["your-api-key-here"]  # Replace with actual API keys
    
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    return api_key
'''

        return template

    def _get_auth_models_template(self) -> str:
        """Get authentication models template"""
        template = '''"""
Authentication Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import BaseModel


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"
'''

        return template

    def _get_auth_schemas_template(self) -> str:
        """Get authentication schemas template"""
        template = '''"""
Authentication Schemas
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class UserBase(BaseModel):
    """User base schema"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(UserBase):
    """User update schema"""
    password: Optional[str] = None


class User(UserBase):
    """User response schema"""
    id: int
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
'''

        return template

    def _get_nosql_auth_schemas_template(self) -> str:
        """Get auth schemas template for NoSQL databases"""
        template = '''"""
Authentication Schemas for NoSQL Databases
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class UserBase(BaseModel):
    """User base schema"""
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class User(UserBase):
    """User response schema"""
    id: str  # For MongoDB ObjectId
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
'''
        return template

    