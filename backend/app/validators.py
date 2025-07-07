import re
from typing import Optional
from app.exceptions import ValidationError

def validate_email(email: Optional[str]) -> Optional[str]:
    """Validate email format"""
    if not email:
        return email
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("email", "Invalid email format")
    return email

def validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate phone number format"""
    if not phone:
        return phone

    # Allow more flexible phone formats for international numbers
    # Remove all non-alphanumeric characters except + and -
    cleaned_phone = re.sub(r'\D', '', phone)

    # Check if it's a valid length (7-20 digits for international flexibility)
    if cleaned_phone and (len(cleaned_phone) < 7 or len(cleaned_phone) > 20):
        raise ValidationError("phone", "Phone number must be between 7-20 digits")

    return phone

def validate_name(name: str) -> str:
    """Validate name field"""
    if not name or not name.strip():
        raise ValidationError("name", "Name is required and cannot be empty")
    
    if len(name.strip()) < 2:
        raise ValidationError("name", "Name must be at least 2 characters long")
    
    return name.strip()

def validate_file_size(file_size: int, max_size: int = 10485760) -> None:
    """Validate file size (default 10MB)"""
    if file_size > max_size:
        raise ValidationError("file", f"File size exceeds maximum allowed size of {max_size} bytes")

def validate_file_type(filename: str, allowed_types: list = None) -> str:
    """Validate file type"""
    if allowed_types is None:
        allowed_types = ['csv', 'xlsx', 'xls', 'pdf', 'docx', 'txt', 'vcf', 'vcard', 'jpg', 'jpeg', 'png']
    
    if not filename:
        raise ValidationError("file", "Filename is required")
    
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in allowed_types:
        raise ValidationError("file", f"File type '{file_extension}' not supported. Allowed types: {', '.join(allowed_types)}")
    
    return file_extension
