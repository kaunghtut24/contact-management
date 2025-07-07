"""
Advanced search service with full-text search capabilities
"""
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from ..models import Contact
from ..models.search import SearchHistory
from ..schemas.search import SearchCriteria, SearchResult, SearchSuggestion

logger = logging.getLogger(__name__)

class AdvancedSearchService:
    def __init__(self):
        self.search_history = []
    
    def full_text_search(
        self, 
        db: Session, 
        query: str, 
        page: int = 1, 
        page_size: int = 20
    ) -> SearchResult:
        """Perform full-text search across all contact fields"""
        start_time = time.time()
        
        # Build search conditions
        search_terms = query.lower().split()
        conditions = []
        
        for term in search_terms:
            term_conditions = [
                func.lower(Contact.name).contains(term),
                func.lower(Contact.email).contains(term),
                func.lower(Contact.phone).contains(term),
                func.lower(Contact.address).contains(term),
                func.lower(Contact.category).contains(term),
                func.lower(Contact.notes).contains(term)
            ]
            conditions.append(or_(*term_conditions))
        
        # Combine all conditions with AND
        final_condition = and_(*conditions) if conditions else text("1=1")
        
        # Get total count
        total_count = db.query(Contact).filter(final_condition).count()
        
        # Get paginated results
        offset = (page - 1) * page_size
        contacts = db.query(Contact).filter(final_condition)\
            .offset(offset).limit(page_size).all()
        
        # Convert to dict format
        contact_dicts = []
        for contact in contacts:
            contact_dicts.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'address': contact.address,
                'category': contact.category,
                'notes': contact.notes,
                'created_at': contact.created_at,
                'updated_at': contact.updated_at
            })
        
        execution_time = int((time.time() - start_time) * 1000)
        total_pages = (total_count + page_size - 1) // page_size
        
        # Log search
        self._log_search(db, query, "full_text", total_count, execution_time)
        
        return SearchResult(
            contacts=contact_dicts,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            execution_time_ms=execution_time
        )
    
    def advanced_search(
        self, 
        db: Session, 
        criteria: SearchCriteria,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20
    ) -> SearchResult:
        """Perform advanced search with specific field criteria"""
        start_time = time.time()
        
        # Build query conditions
        conditions = []
        
        if criteria.query:
            # General search across all fields
            search_terms = criteria.query.lower().split()
            for term in search_terms:
                term_conditions = [
                    func.lower(Contact.name).contains(term),
                    func.lower(Contact.email).contains(term),
                    func.lower(Contact.phone).contains(term),
                    func.lower(Contact.address).contains(term),
                    func.lower(Contact.category).contains(term),
                    func.lower(Contact.notes).contains(term)
                ]
                conditions.append(or_(*term_conditions))
        
        # Specific field searches
        if criteria.name:
            conditions.append(func.lower(Contact.name).contains(criteria.name.lower()))
        
        if criteria.email:
            conditions.append(func.lower(Contact.email).contains(criteria.email.lower()))
        
        if criteria.phone:
            conditions.append(Contact.phone.contains(criteria.phone))
        
        if criteria.address:
            conditions.append(func.lower(Contact.address).contains(criteria.address.lower()))
        
        if criteria.category:
            conditions.append(Contact.category == criteria.category)
        
        if criteria.notes:
            conditions.append(func.lower(Contact.notes).contains(criteria.notes.lower()))
        
        if criteria.created_after:
            conditions.append(Contact.created_at >= criteria.created_after)
        
        if criteria.created_before:
            conditions.append(Contact.created_at <= criteria.created_before)
        
        # Combine conditions
        final_condition = and_(*conditions) if conditions else text("1=1")
        
        # Build query with sorting
        query = db.query(Contact).filter(final_condition)
        
        # Apply sorting
        sort_column = getattr(Contact, sort_by, Contact.name)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        offset = (page - 1) * page_size
        contacts = query.offset(offset).limit(page_size).all()
        
        # Convert to dict format
        contact_dicts = []
        for contact in contacts:
            contact_dicts.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'address': contact.address,
                'category': contact.category,
                'notes': contact.notes,
                'created_at': contact.created_at,
                'updated_at': contact.updated_at
            })
        
        execution_time = int((time.time() - start_time) * 1000)
        total_pages = (total_count + page_size - 1) // page_size
        
        # Log search
        search_query = f"Advanced: {criteria.dict()}"
        self._log_search(db, search_query, "advanced", total_count, execution_time)
        
        return SearchResult(
            contacts=contact_dicts,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            execution_time_ms=execution_time
        )
    
    def get_search_suggestions(self, db: Session, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get search suggestions based on existing data"""
        suggestions = []
        query_lower = query.lower()
        
        # Name suggestions
        names = db.query(Contact.name).filter(
            func.lower(Contact.name).contains(query_lower)
        ).distinct().limit(limit).all()
        
        for name in names:
            if name[0]:
                suggestions.append({
                    'type': 'name',
                    'value': name[0],
                    'count': db.query(Contact).filter(Contact.name == name[0]).count()
                })
        
        # Category suggestions
        categories = db.query(Contact.category).filter(
            func.lower(Contact.category).contains(query_lower)
        ).distinct().limit(limit).all()
        
        for category in categories:
            if category[0]:
                suggestions.append({
                    'type': 'category',
                    'value': category[0],
                    'count': db.query(Contact).filter(Contact.category == category[0]).count()
                })
        
        return suggestions[:limit]
    
    def _log_search(self, db: Session, query: str, search_type: str, results_count: int, execution_time: int):
        """Log search for analytics"""
        try:
            search_log = SearchHistory(
                search_query=query[:500],  # Truncate if too long
                search_type=search_type,
                results_count=results_count,
                execution_time_ms=execution_time
            )
            db.add(search_log)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log search: {e}")

# Global search service instance
search_service = AdvancedSearchService()
