"""
API endpoints for advanced search and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from ..database import get_db
from ..models.search import SavedFilter
from ..schemas.search import (
    AdvancedSearchRequest, SearchResult, SavedFilterCreate, 
    SavedFilterUpdate, SavedFilterOut, SearchSuggestion
)
from ..services.search_service import search_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search", response_model=SearchResult)
def full_text_search(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Perform full-text search across all contact fields"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    result = search_service.full_text_search(db, q.strip(), page, page_size)
    logger.info(f"Full-text search for '{q}' returned {result.total_count} results")
    return result

@router.post("/search/advanced", response_model=SearchResult)
def advanced_search(
    search_request: AdvancedSearchRequest,
    db: Session = Depends(get_db)
):
    """Perform advanced search with specific field criteria"""
    result = search_service.advanced_search(
        db=db,
        criteria=search_request.criteria,
        sort_by=search_request.sort_by,
        sort_order=search_request.sort_order,
        page=search_request.page,
        page_size=search_request.page_size
    )
    logger.info(f"Advanced search returned {result.total_count} results")
    return result

@router.get("/search/suggestions")
def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    db: Session = Depends(get_db)
):
    """Get search suggestions based on existing data"""
    if len(q.strip()) < 2:
        return []
    
    suggestions = search_service.get_search_suggestions(db, q.strip(), limit)
    return suggestions

@router.get("/filters", response_model=List[SavedFilterOut])
def get_saved_filters(
    skip: int = 0, 
    limit: int = 100, 
    favorites_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get saved search filters"""
    query = db.query(SavedFilter)
    
    if favorites_only:
        query = query.filter(SavedFilter.is_favorite == True)
    
    filters = query.order_by(SavedFilter.last_used_at.desc().nullslast(), 
                           SavedFilter.created_at.desc())\
                  .offset(skip).limit(limit).all()
    return filters

@router.post("/filters", response_model=SavedFilterOut)
def create_saved_filter(filter_data: SavedFilterCreate, db: Session = Depends(get_db)):
    """Create a new saved filter"""
    # Check if filter name already exists
    existing = db.query(SavedFilter).filter(SavedFilter.name == filter_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Filter name already exists")
    
    db_filter = SavedFilter(
        name=filter_data.name,
        description=filter_data.description,
        filter_criteria=filter_data.filter_criteria,
        is_favorite=filter_data.is_favorite
    )
    db.add(db_filter)
    db.commit()
    db.refresh(db_filter)
    
    logger.info(f"Created saved filter: {filter_data.name}")
    return db_filter

@router.put("/filters/{filter_id}", response_model=SavedFilterOut)
def update_saved_filter(
    filter_id: int, 
    filter_data: SavedFilterUpdate, 
    db: Session = Depends(get_db)
):
    """Update a saved filter"""
    db_filter = db.query(SavedFilter).filter(SavedFilter.id == filter_id).first()
    if not db_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    # Check if new name conflicts with existing filters
    if filter_data.name and filter_data.name != db_filter.name:
        existing = db.query(SavedFilter).filter(
            SavedFilter.name == filter_data.name,
            SavedFilter.id != filter_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Filter name already exists")
    
    # Update fields
    update_data = filter_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_filter, field, value)
    
    db_filter.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_filter)
    
    logger.info(f"Updated saved filter: {db_filter.name}")
    return db_filter

@router.delete("/filters/{filter_id}")
def delete_saved_filter(filter_id: int, db: Session = Depends(get_db)):
    """Delete a saved filter"""
    db_filter = db.query(SavedFilter).filter(SavedFilter.id == filter_id).first()
    if not db_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    db.delete(db_filter)
    db.commit()
    
    logger.info(f"Deleted saved filter: {db_filter.name}")
    return {"message": "Filter deleted successfully"}

@router.post("/filters/{filter_id}/use", response_model=SearchResult)
def use_saved_filter(
    filter_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Apply a saved filter and return results"""
    db_filter = db.query(SavedFilter).filter(SavedFilter.id == filter_id).first()
    if not db_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    # Update usage statistics
    db_filter.usage_count += 1
    db_filter.last_used_at = datetime.utcnow()
    db.commit()
    
    # Apply the filter
    try:
        from ..schemas.search import SearchCriteria
        criteria = SearchCriteria(**db_filter.filter_criteria)
        
        result = search_service.advanced_search(
            db=db,
            criteria=criteria,
            page=page,
            page_size=page_size
        )
        
        logger.info(f"Applied saved filter '{db_filter.name}' - {result.total_count} results")
        return result
        
    except Exception as e:
        logger.error(f"Error applying saved filter: {e}")
        raise HTTPException(status_code=400, detail="Invalid filter criteria")

@router.post("/filters/{filter_id}/favorite")
def toggle_filter_favorite(filter_id: int, db: Session = Depends(get_db)):
    """Toggle favorite status of a saved filter"""
    db_filter = db.query(SavedFilter).filter(SavedFilter.id == filter_id).first()
    if not db_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    
    db_filter.is_favorite = not db_filter.is_favorite
    db_filter.updated_at = datetime.utcnow()
    db.commit()
    
    status = "added to" if db_filter.is_favorite else "removed from"
    logger.info(f"Filter '{db_filter.name}' {status} favorites")
    return {"message": f"Filter {status} favorites", "is_favorite": db_filter.is_favorite}
