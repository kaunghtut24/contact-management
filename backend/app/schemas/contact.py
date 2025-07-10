from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.validators import validate_email, validate_phone, validate_name

class ContactCreate(BaseModel):
    name: str
    designation: Optional[str] = None
    company: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = "Others"
    notes: Optional[str] = None

    # Legacy fields for backward compatibility
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator('name')
    def validate_name_field(cls, v):
        return validate_name(v)

    @validator('email')
    def validate_email_field(cls, v):
        return validate_email(v)

    @validator('telephone')
    def validate_telephone_field(cls, v):
        return validate_phone(v)

    @validator('phone')
    def validate_phone_field(cls, v):
        return validate_phone(v)

    @validator('website')
    def validate_website_field(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    company: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None

    # Legacy fields for backward compatibility
    phone: Optional[str] = None
    address: Optional[str] = None

    @validator('name')
    def validate_name_field(cls, v):
        if v is not None:
            return validate_name(v)
        return v

    @validator('email')
    def validate_email_field(cls, v):
        return validate_email(v)

    @validator('telephone')
    def validate_telephone_field(cls, v):
        return validate_phone(v)

    @validator('phone')
    def validate_phone_field(cls, v):
        return validate_phone(v)

    @validator('website')
    def validate_website_field(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class ContactOut(BaseModel):
    id: int
    name: str
    designation: Optional[str] = None
    company: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    category: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Legacy fields for backward compatibility
    phone: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True