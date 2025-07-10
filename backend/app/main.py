from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import io
import csv
from io import StringIO
from app.models import Contact, Base
from app.schemas.contact import ContactCreate, ContactUpdate, ContactOut
from app.database import SessionLocal, engine
from app.parsers.parse import parse_pdf, parse_docx, parse_image
from app.utils.nlp import categorize_contact
# from app.ml.categorizer import categorize_contact_ml
# from app.api.categories import router as categories_router
# from app.api.search import router as search_router
from app.config import settings
from app.exceptions import (
    ContactNotFoundError,
    FileProcessingError,
    ValidationError,
    contact_not_found_handler,
    file_processing_error_handler,
    validation_error_handler
)
from app.validators import validate_file_size, validate_file_type
from app.logging_config import setup_logging
from app.api.auth import router as auth_router

# Setup logging
logger = setup_logging()



app = FastAPI()

# Include routers (temporarily disabled)
# app.include_router(categories_router, prefix="/api", tags=["categories"])
# app.include_router(search_router, prefix="/api", tags=["search"])
app.include_router(auth_router)

# Add exception handlers
app.add_exception_handler(ContactNotFoundError, contact_not_found_handler)
app.add_exception_handler(FileProcessingError, file_processing_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Contact Management System API is running"}

@app.get("/db-info")
def database_info():
    """Check which database is being used"""
    from app.config import settings
    from app.database import engine

    db_url = settings.DATABASE_URL
    db_type = "Unknown"

    if db_url.startswith("sqlite"):
        db_type = "SQLite (Local)"
    elif db_url.startswith("postgresql"):
        db_type = "PostgreSQL (Neon)"
    elif db_url.startswith("mysql"):
        db_type = "MySQL"

    try:
        # Test connection
        with engine.connect() as conn:
            if db_url.startswith("sqlite"):
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            elif db_url.startswith("postgresql"):
                result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            else:
                result = conn.execute(text("SELECT 1"))

            tables = [row[0] for row in result] if db_url.startswith(("sqlite", "postgresql")) else ["connection_test"]

            return {
                "database_type": db_type,
                "database_url": db_url[:50] + "..." if len(db_url) > 50 else db_url,
                "connection_status": "Connected",
                "tables": tables
            }
    except Exception as e:
        return {
            "database_type": db_type,
            "database_url": db_url[:50] + "..." if len(db_url) > 50 else db_url,
            "connection_status": "Failed",
            "error": str(e)
        }

# Get all contacts with search and filter
@app.get("/contacts", response_model=List[ContactOut])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    search: str = Query(None),
    category: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Contact)
    if search:
        query = query.filter(
            (Contact.name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%")) |
            (Contact.phone.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(Contact.category == category)
    return query.offset(skip).limit(limit).all()

# Get contact by ID
@app.get("/contacts/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise ContactNotFoundError(contact_id)
    return contact

# Create a new contact
@app.post("/contacts", response_model=ContactOut)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new contact: {contact.name}")

    # Convert to dict and handle field mapping
    contact_data = contact.dict()

    # Map legacy fields to new fields if new fields are empty
    if not contact_data.get('telephone') and contact_data.get('phone'):
        contact_data['telephone'] = contact_data['phone']
    if not contact_data.get('company') and contact_data.get('address'):
        # Try to extract company from address if it looks like a business address
        address = contact_data['address']
        if any(biz_word in address.lower() for biz_word in ['office', 'building', 'tower', 'complex', 'center']):
            contact_data['company'] = address

    db_contact = Contact(**contact_data)

    # Use enhanced categorization with new fields
    db_contact.category = categorize_contact(db_contact)

    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    logger.info(f"Contact created successfully with ID: {db_contact.id}")
    return db_contact

# Update a contact
@app.put("/contacts/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise ContactNotFoundError(contact_id)
    update_data = contact.dict(exclude_unset=True)

    # Check if user explicitly set a category
    user_set_category = 'category' in update_data

    for key, value in update_data.items():
        setattr(db_contact, key, value)

    # Only auto-categorize if user didn't explicitly set a category
    # and if address or notes were updated
    if not user_set_category and ('address' in update_data or 'notes' in update_data):
        new_category = categorize_contact(db_contact)
        db_contact.category = new_category if new_category else "Others"

    # Ensure category is never None
    if db_contact.category is None:
        db_contact.category = "Others"

    db.commit()
    db.refresh(db_contact)
    return db_contact

# Batch delete contacts (must come before single delete route)
@app.delete("/contacts/batch")
def batch_delete_contacts(contact_ids: List[int], db: Session = Depends(get_db)):
    """Delete multiple contacts by their IDs"""
    deleted_count = 0
    failed_ids = []

    for contact_id in contact_ids:
        db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
        if db_contact:
            db.delete(db_contact)
            deleted_count += 1
        else:
            failed_ids.append(contact_id)

    db.commit()

    return {
        "message": f"Batch delete completed",
        "deleted_count": deleted_count,
        "failed_count": len(failed_ids),
        "failed_ids": failed_ids
    }

# Delete a contact
@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not db_contact:
        raise ContactNotFoundError(contact_id)
    db.delete(db_contact)
    db.commit()
    return {"detail": "Contact deleted"}

# Upload and parse file
@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Processing file upload: {file.filename}")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = validate_file_type(file.filename)
    file_content = file.file.read()
    validate_file_size(len(file_content), settings.MAX_FILE_SIZE)
    file.file.seek(0)

    logger.info(f"File validated successfully. Type: {ext}, Size: {len(file_content)} bytes")

    contacts = []
    try:
        if ext in ["csv", "txt"]:
            if ext == "csv":
                try:
                    import pandas as pd
                    df = pd.read_csv(io.StringIO(file_content.decode("utf-8")))
                    for _, row in df.iterrows():
                        contacts.append({
                            "name": row.get("name", ""),
                            "designation": row.get("designation", ""),
                            "company": row.get("company", ""),
                            "telephone": row.get("telephone", "") or row.get("phone", ""),
                            "email": row.get("email", ""),
                            "website": row.get("website", ""),
                            "category": row.get("category", "Others"),
                            "notes": row.get("notes", ""),
                            # Legacy fields for backward compatibility
                            "phone": row.get("phone", ""),
                            "address": row.get("address", "")
                        })
                except ImportError:
                    # Fallback to text parsing
                    content = file_content.decode("utf-8")
                    contacts = parse_txt(content.encode("utf-8"))
            else:
                contacts = parse_txt(file_content)
        elif ext in ["xls", "xlsx"]:
            try:
                import pandas as pd
                df = pd.read_excel(io.BytesIO(file_content))
                for _, row in df.iterrows():
                    contacts.append({
                        "name": row.get("name", ""),
                        "designation": row.get("designation", ""),
                        "company": row.get("company", ""),
                        "telephone": row.get("telephone", "") or row.get("phone", ""),
                        "email": row.get("email", ""),
                        "website": row.get("website", ""),
                        "category": row.get("category", "Others"),
                        "notes": row.get("notes", ""),
                        # Legacy fields for backward compatibility
                        "phone": row.get("phone", ""),
                        "address": row.get("address", "")
                    })
            except ImportError:
                raise FileProcessingError(file.filename, "pandas required for Excel file processing")
        elif ext == "pdf":
            contacts = parse_pdf(file_content)
        elif ext == "docx":
            contacts = parse_docx(file_content)
        elif ext in ["vcf", "vcard"]:
            contacts = parse_vcf(file_content)
        elif ext in ["jpg", "jpeg", "png"]:
            contacts = parse_image(file_content)
        else:
            raise FileProcessingError(file.filename, "Unsupported file type")
    except FileProcessingError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        raise FileProcessingError(file.filename, str(e))

    for c in contacts:
        c["category"] = categorize_contact(c)
        db.add(Contact(**c))
    db.commit()

    return {"message": f"{len(contacts)} contacts imported successfully"}

# Export contacts to CSV with new column structure
@app.get("/export")
def export_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    si = StringIO()
    writer = csv.writer(si)

    # Updated column structure with Address
    writer.writerow(["ID", "Name", "Designation", "Company", "Telephone", "Email", "Website", "Category", "Address", "Notes"])

    for c in contacts:
        writer.writerow([
            c.id,
            c.name,
            getattr(c, 'designation', '') or '',
            getattr(c, 'company', '') or '',
            getattr(c, 'telephone', '') or getattr(c, 'phone', '') or '',
            c.email or '',
            getattr(c, 'website', '') or '',
            c.category or '',
            getattr(c, 'address', '') or '',
            c.notes or ''
        ])

    si.seek(0)
    response = StreamingResponse(si, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=contacts.csv"
    return response

# Batch export selected contacts
@app.post("/export/batch")
def batch_export_contacts(contact_ids: List[int], db: Session = Depends(get_db)):
    """Export selected contacts to CSV"""
    contacts = db.query(Contact).filter(Contact.id.in_(contact_ids)).all()

    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found with provided IDs")

    si = StringIO()
    writer = csv.writer(si)

    # Updated column structure with Address
    writer.writerow(["ID", "Name", "Designation", "Company", "Telephone", "Email", "Website", "Category", "Address", "Notes"])

    for c in contacts:
        writer.writerow([
            c.id,
            c.name,
            getattr(c, 'designation', '') or '',
            getattr(c, 'company', '') or '',
            getattr(c, 'telephone', '') or getattr(c, 'phone', '') or '',
            c.email or '',
            getattr(c, 'website', '') or '',
            c.category or '',
            getattr(c, 'address', '') or '',
            c.notes or ''
        ])

    si.seek(0)
    response = StreamingResponse(si, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=selected_contacts_{len(contacts)}.csv"
    return response