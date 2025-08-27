"""Utils Generator - Generates utility functions"""

from ...generators.base_generator import BaseGenerator


class UtilsGenerator(BaseGenerator):
    """Generates utility files"""

    def generate(self):
        """Generate utility files"""
        # Generate common utilities
        utils_content = self._get_utils_template()
        self.write_file(f"{self.config.path}/app/utils/common.py", utils_content)

        # Generate response utilities
        response_content = self._get_response_template()
        self.write_file(f"{self.config.path}/app/utils/responses.py", response_content)

        # Generate validation utilities
        validation_content = self._get_validation_template()
        self.write_file(
            f"{self.config.path}/app/utils/validation.py", validation_content
        )

    def _get_utils_template(self) -> str:
        """Get common utilities template"""
        template = f'''"""
Common utilities for {self.config.name}
"""

import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from pathlib import Path


def generate_random_string(length: int = 32) -> str:
    """Generate a random string of specified length"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """Generate hash for given data"""
    if algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {{algorithm}}")


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string"""
    return datetime.strptime(dt_str, format_str)


def ensure_directory(path: str) -> Path:
    """Ensure directory exists, create if it doesn't"""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def paginate_query(query, page: int = 1, per_page: int = 10):
    """Paginate query results"""
    offset = (page - 1) * per_page
    return query.offset(offset).limit(per_page)


def calculate_pagination_info(total: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Calculate pagination information"""
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return {{
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else None,
        "next_page": page + 1 if has_next else None,
    }}
'''
        return template

    def _get_response_template(self) -> str:
        """Get response utilities template"""
        template = '''"""
Response utilities
"""

from typing import Any, Dict, List, Optional, Union
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """Create a success response"""
    response = APIResponse(
        success=True,
        message=message,
        data=data
    )
    return JSONResponse(
        content=response.dict(exclude_none=True),
        status_code=status_code
    )


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[str]] = None,
    status_code: int = 400
) -> JSONResponse:
    """Create an error response"""
    response = APIResponse(
        success=False,
        message=message,
        errors=errors or []
    )
    return JSONResponse(
        content=response.dict(exclude_none=True),
        status_code=status_code
    )


def paginated_response(
    data: List[Any],
    pagination_info: Dict[str, Any],
    message: str = "Success"
) -> JSONResponse:
    """Create a paginated response"""
    response_data = {
        "items": data,
        "pagination": pagination_info
    }
    
    return success_response(
        data=response_data,
        message=message
    )


def validation_error_response(errors: Dict[str, Any]) -> JSONResponse:
    """Create a validation error response"""
    error_messages = []
    
    for field, messages in errors.items():
        if isinstance(messages, list):
            for msg in messages:
                error_messages.append(f"{field}: {msg}")
        else:
            error_messages.append(f"{field}: {messages}")
    
    return error_response(
        message="Validation failed",
        errors=error_messages,
        status_code=422
    )
'''
        return template

    def _get_validation_template(self) -> str:
        """Get validation utilities template"""
        template = '''"""
Validation utilities
"""

import re
from typing import Optional, Any, Dict, List
from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str) -> bool:
    """Validate email address"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def is_valid_phone(phone: str) -> bool:
    """Validate phone number (basic validation)"""    # Remove common separators
    clean_phone = re.sub(r'[+\s\(\)-]', '', phone)
    
    # Check if it contains only digits and is reasonable length
    return clean_phone.isdigit() and 7 <= len(clean_phone) <= 15


def is_valid_password(password: str, min_length: int = 8) -> Dict[str, Any]:
    """
    Validate password strength
    Returns dict with 'valid' boolean and 'errors' list
    """
    errors = []
    
    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate that required fields are present and not empty"""
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Field '{field}' is required")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Field '{field}' cannot be empty")
    
    return errors


def sanitize_input(value: str) -> str:
    """Basic input sanitization"""
    if not isinstance(value, str):
        return value
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Remove null bytes
    value = value.replace('\\x00', '')
    
    return value


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_ext in [ext.lower().lstrip('.') for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes
'''
        return template
