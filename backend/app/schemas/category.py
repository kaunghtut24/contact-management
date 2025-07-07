"""
Pydantic schemas for category management
"""
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

class CategoryRuleCreate(BaseModel):
    rule_type: str  # 'keyword', 'domain', 'pattern'
    rule_value: str
    field_target: str  # 'name', 'email', 'address', 'notes', 'all'
    priority: Optional[int] = 1
    
    @validator('rule_type')
    def validate_rule_type(cls, v):
        allowed_types = ['keyword', 'domain', 'pattern']
        if v not in allowed_types:
            raise ValueError(f'rule_type must be one of {allowed_types}')
        return v
    
    @validator('field_target')
    def validate_field_target(cls, v):
        allowed_targets = ['name', 'email', 'address', 'notes', 'all']
        if v not in allowed_targets:
            raise ValueError(f'field_target must be one of {allowed_targets}')
        return v

class CategoryRuleOut(CategoryRuleCreate):
    id: int
    category_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContactCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6B7280"
    rules: Optional[List[CategoryRuleCreate]] = []
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Category name must be at least 2 characters long')
        return v.strip()
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
        return v

class ContactCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or len(v.strip()) < 2):
            raise ValueError('Category name must be at least 2 characters long')
        return v.strip() if v else v
    
    @validator('color')
    def validate_color(cls, v):
        if v and (not v.startswith('#') or len(v) != 7):
            raise ValueError('Color must be a valid hex color code (e.g., #FF0000)')
        return v

class ContactCategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    rules: List[CategoryRuleOut] = []
    
    class Config:
        from_attributes = True

class CategoryFeedback(BaseModel):
    contact_id: int
    correct_category: str
    
    @validator('correct_category')
    def validate_category(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Category must be at least 2 characters long')
        return v.strip()
