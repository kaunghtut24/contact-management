"""
Pydantic schemas for search and filtering
"""
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class SearchCriteria(BaseModel):
    query: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
class AdvancedSearchRequest(BaseModel):
    criteria: SearchCriteria
    sort_by: Optional[str] = "name"
    sort_order: Optional[str] = "asc"
    page: Optional[int] = 1
    page_size: Optional[int] = 20
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['name', 'email', 'phone', 'category', 'created_at', 'updated_at']
        if v not in allowed_fields:
            raise ValueError(f'sort_by must be one of {allowed_fields}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order must be "asc" or "desc"')
        return v

class SavedFilterCreate(BaseModel):
    name: str
    description: Optional[str] = None
    filter_criteria: Dict[str, Any]
    is_favorite: Optional[bool] = False
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Filter name must be at least 2 characters long')
        return v.strip()

class SavedFilterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    is_favorite: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or len(v.strip()) < 2):
            raise ValueError('Filter name must be at least 2 characters long')
        return v.strip() if v else v

class SavedFilterOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    filter_criteria: Dict[str, Any]
    is_public: bool
    is_favorite: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SearchResult(BaseModel):
    contacts: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    execution_time_ms: int

class SearchSuggestion(BaseModel):
    type: str  # 'name', 'email', 'category', etc.
    value: str
    count: int  # Number of contacts matching this suggestion
