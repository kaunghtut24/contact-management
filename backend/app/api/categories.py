"""
API endpoints for category management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from ..database import get_db
from ..models.category import ContactCategory, CategoryRule
from ..schemas.category import (
    ContactCategoryCreate, ContactCategoryUpdate, ContactCategoryOut,
    CategoryRuleCreate, CategoryRuleOut, CategoryFeedback
)
from ..ml.categorizer import add_categorization_feedback

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/categories", response_model=List[ContactCategoryOut])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all contact categories"""
    categories = db.query(ContactCategory).filter(
        ContactCategory.is_active == True
    ).offset(skip).limit(limit).all()
    return categories

@router.post("/categories", response_model=ContactCategoryOut)
def create_category(category: ContactCategoryCreate, db: Session = Depends(get_db)):
    """Create a new contact category"""
    # Check if category name already exists
    existing = db.query(ContactCategory).filter(
        ContactCategory.name == category.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Create category
    db_category = ContactCategory(
        name=category.name,
        description=category.description,
        color=category.color,
        is_default=False
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    # Create rules if provided
    for rule_data in category.rules:
        db_rule = CategoryRule(
            category_id=db_category.id,
            rule_type=rule_data.rule_type,
            rule_value=rule_data.rule_value,
            field_target=rule_data.field_target,
            priority=rule_data.priority
        )
        db.add(db_rule)
    
    db.commit()
    logger.info(f"Created new category: {category.name}")
    return db_category

@router.put("/categories/{category_id}", response_model=ContactCategoryOut)
def update_category(
    category_id: int, 
    category: ContactCategoryUpdate, 
    db: Session = Depends(get_db)
):
    """Update a contact category"""
    db_category = db.query(ContactCategory).filter(
        ContactCategory.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if trying to update a default category
    if db_category.is_default and category.name:
        raise HTTPException(
            status_code=400, 
            detail="Cannot rename default categories"
        )
    
    # Update fields
    update_data = category.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    logger.info(f"Updated category: {db_category.name}")
    return db_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a contact category (soft delete)"""
    db_category = db.query(ContactCategory).filter(
        ContactCategory.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if db_category.is_default:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete default categories"
        )
    
    # Soft delete
    db_category.is_active = False
    db.commit()
    logger.info(f"Deleted category: {db_category.name}")
    return {"message": "Category deleted successfully"}

@router.post("/categories/{category_id}/rules", response_model=CategoryRuleOut)
def create_category_rule(
    category_id: int, 
    rule: CategoryRuleCreate, 
    db: Session = Depends(get_db)
):
    """Create a new categorization rule"""
    # Check if category exists
    category = db.query(ContactCategory).filter(
        ContactCategory.id == category_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_rule = CategoryRule(
        category_id=category_id,
        rule_type=rule.rule_type,
        rule_value=rule.rule_value,
        field_target=rule.field_target,
        priority=rule.priority
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    logger.info(f"Created rule for category {category.name}: {rule.rule_value}")
    return db_rule

@router.delete("/categories/rules/{rule_id}")
def delete_category_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a categorization rule"""
    db_rule = db.query(CategoryRule).filter(CategoryRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(db_rule)
    db.commit()
    logger.info(f"Deleted categorization rule: {rule_id}")
    return {"message": "Rule deleted successfully"}

@router.post("/categories/feedback")
def submit_categorization_feedback(feedback: CategoryFeedback, db: Session = Depends(get_db)):
    """Submit feedback for improving categorization"""
    # Get the contact
    from ..models import Contact
    contact = db.query(Contact).filter(Contact.id == feedback.contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Convert contact to dict for ML processing
    contact_dict = {
        'id': contact.id,
        'name': contact.name,
        'email': contact.email or '',
        'phone': contact.phone or '',
        'address': contact.address or '',
        'notes': contact.notes or ''
    }
    
    # Add feedback to ML system
    add_categorization_feedback(contact_dict, feedback.correct_category)
    
    # Update the contact's category
    contact.category = feedback.correct_category
    db.commit()
    
    logger.info(f"Received categorization feedback for contact {feedback.contact_id}: {feedback.correct_category}")
    return {"message": "Feedback submitted successfully"}

@router.get("/categories/default")
def initialize_default_categories(db: Session = Depends(get_db)):
    """Initialize default categories if they don't exist"""
    default_categories = [
        {"name": "Work", "description": "Business and professional contacts", "color": "#3B82F6"},
        {"name": "Personal", "description": "Friends, family, and personal contacts", "color": "#10B981"},
        {"name": "Service", "description": "Service providers and vendors", "color": "#F59E0B"},
        {"name": "Uncategorized", "description": "Contacts without a specific category", "color": "#6B7280"}
    ]
    
    created_count = 0
    for cat_data in default_categories:
        existing = db.query(ContactCategory).filter(
            ContactCategory.name == cat_data["name"]
        ).first()
        
        if not existing:
            db_category = ContactCategory(
                name=cat_data["name"],
                description=cat_data["description"],
                color=cat_data["color"],
                is_default=True
            )
            db.add(db_category)
            created_count += 1
    
    db.commit()
    logger.info(f"Initialized {created_count} default categories")
    return {"message": f"Initialized {created_count} default categories"}
