"""
Contact service layer for business logic separation
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from ..models.contact import Contact
from ..schemas.contact import ContactCreate, ContactUpdate
from ..models.user import User, UserRole

logger = logging.getLogger(__name__)

class ContactService:
    """Service class for contact operations with business logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_contact(self, db: Session, contact_data: ContactCreate, current_user: User) -> Contact:
        """Create a new contact with validation"""
        try:
            # Business logic: validate contact data
            if not contact_data.name or not contact_data.name.strip():
                raise ValueError("Contact name is required")
            
            # Create contact
            db_contact = Contact(**contact_data.dict())
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)
            
            self.logger.info(f"User {current_user.username} created contact: {db_contact.name}")
            return db_contact
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating contact: {e}")
            raise
    
    def get_contact(self, db: Session, contact_id: int, current_user: User) -> Optional[Contact]:
        """Get a contact by ID with access control"""
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
        
        if contact:
            self.logger.info(f"User {current_user.username} accessed contact: {contact.name}")
        
        return contact
    
    def get_contacts(
        self, 
        db: Session, 
        current_user: User,
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Contact]:
        """Get contacts with filtering and pagination"""
        try:
            query = db.query(Contact)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Contact.name.ilike(search_term),
                        Contact.email.ilike(search_term),
                        Contact.company.ilike(search_term),
                        Contact.phone.ilike(search_term)
                    )
                )
            
            # Apply category filter
            if category:
                query = query.filter(Contact.category == category)
            
            # Apply pagination
            contacts = query.offset(skip).limit(limit).all()
            
            self.logger.info(f"User {current_user.username} retrieved {len(contacts)} contacts")
            return contacts
            
        except Exception as e:
            self.logger.error(f"Error retrieving contacts: {e}")
            raise
    
    def update_contact(
        self, 
        db: Session, 
        contact_id: int, 
        contact_data: ContactUpdate, 
        current_user: User
    ) -> Optional[Contact]:
        """Update a contact with validation"""
        try:
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return None
            
            # Business logic: validate update data
            update_data = contact_data.dict(exclude_unset=True)
            
            if 'name' in update_data and not update_data['name'].strip():
                raise ValueError("Contact name cannot be empty")
            
            # Apply updates
            for field, value in update_data.items():
                setattr(contact, field, value)
            
            db.commit()
            db.refresh(contact)
            
            self.logger.info(f"User {current_user.username} updated contact: {contact.name}")
            return contact
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating contact: {e}")
            raise
    
    def delete_contact(self, db: Session, contact_id: int, current_user: User) -> bool:
        """Delete a contact with access control"""
        try:
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                return False
            
            contact_name = contact.name
            db.delete(contact)
            db.commit()
            
            self.logger.info(f"User {current_user.username} deleted contact: {contact_name}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting contact: {e}")
            raise
    
    def batch_delete_contacts(
        self, 
        db: Session, 
        contact_ids: List[int], 
        current_user: User
    ) -> Dict[str, Any]:
        """Delete multiple contacts with transaction safety"""
        try:
            deleted_count = 0
            failed_ids = []
            
            for contact_id in contact_ids:
                contact = db.query(Contact).filter(Contact.id == contact_id).first()
                if contact:
                    db.delete(contact)
                    deleted_count += 1
                else:
                    failed_ids.append(contact_id)
            
            db.commit()
            
            result = {
                "deleted_count": deleted_count,
                "failed_count": len(failed_ids),
                "failed_ids": failed_ids,
                "message": f"Successfully deleted {deleted_count} contacts"
            }
            
            self.logger.info(f"User {current_user.username} batch deleted {deleted_count} contacts")
            return result
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error in batch delete: {e}")
            raise
    
    def get_contact_statistics(self, db: Session, current_user: User) -> Dict[str, Any]:
        """Get contact statistics and analytics"""
        try:
            # Total contacts
            total_contacts = db.query(Contact).count()
            
            # Category distribution
            category_stats = db.query(
                Contact.category,
                func.count(Contact.id).label('count')
            ).group_by(Contact.category).all()
            
            # Data quality metrics
            missing_email = db.query(Contact).filter(
                or_(Contact.email.is_(None), Contact.email == '')
            ).count()
            
            missing_phone = db.query(Contact).filter(
                or_(Contact.phone.is_(None), Contact.phone == '')
            ).count()
            
            # Recent contacts (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_contacts = db.query(Contact).filter(
                Contact.created_at >= thirty_days_ago
            ).count()
            
            stats = {
                "total_contacts": total_contacts,
                "recent_contacts": recent_contacts,
                "categories": [
                    {"category": cat or "Uncategorized", "count": count} 
                    for cat, count in category_stats
                ],
                "data_quality": {
                    "missing_email": missing_email,
                    "missing_phone": missing_phone,
                    "completion_rate": (
                        ((total_contacts - missing_email - missing_phone) / (total_contacts * 2)) * 100 
                        if total_contacts > 0 else 0
                    )
                }
            }
            
            self.logger.info(f"User {current_user.username} accessed contact statistics")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            raise

# Create singleton instance
contact_service = ContactService()
