from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import io
import csv
import os
from io import StringIO

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contact_db.sqlite")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import models and schemas (we'll need to flatten these too)
try:
    import sys
    sys.path.append('.')
    from app.models import Contact, Base
    from app.schemas import ContactCreate, ContactUpdate, ContactOut
    print("Successfully imported from app modules")
except ImportError as e:
    print(f"Import error: {e}")
    # Create minimal models inline
    from sqlalchemy import Column, Integer, String, Text, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from datetime import datetime
    from pydantic import BaseModel
    
    Base = declarative_base()
    
    class Contact(Base):
        __tablename__ = "contacts"
        
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(255), nullable=False)
        email = Column(String(255))
        phone = Column(String(50))
        company = Column(String(255))
        designation = Column(String(255))
        website = Column(String(255))
        address = Column(Text)
        category = Column(String(100), default="Others")
        notes = Column(Text)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    class ContactCreate(BaseModel):
        name: str
        email: str = None
        phone: str = None
        company: str = None
        designation: str = None
        website: str = None
        address: str = None
        category: str = "Others"
        notes: str = None
    
    class ContactUpdate(BaseModel):
        name: str = None
        email: str = None
        phone: str = None
        company: str = None
        designation: str = None
        website: str = None
        address: str = None
        category: str = None
        notes: str = None
    
    class ContactOut(BaseModel):
        id: int
        name: str
        email: str = None
        phone: str = None
        company: str = None
        designation: str = None
        website: str = None
        address: str = None
        category: str = "Others"
        notes: str = None
        
        class Config:
            from_attributes = True

# Create FastAPI app
app = FastAPI(title="Contact Management API", version="1.0.0")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

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

# Get all contacts
@app.get("/contacts", response_model=List[ContactOut])
def get_contacts(
    search: str = Query(None, description="Search in name, email, company"),
    category: str = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    query = db.query(Contact)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Contact.name.ilike(search_filter)) |
            (Contact.email.ilike(search_filter)) |
            (Contact.company.ilike(search_filter))
        )
    
    if category:
        query = query.filter(Contact.category == category)
    
    contacts = query.all()
    return contacts

# Create contact
@app.post("/contacts", response_model=ContactOut)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

# Get contact by ID
@app.get("/contacts/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

# Update contact
@app.put("/contacts/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, contact_update: ContactUpdate, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)
    
    db.commit()
    db.refresh(contact)
    return contact

# Delete contact
@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

# Export contacts
@app.get("/export")
def export_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Name', 'Email', 'Phone', 'Company', 'Designation', 'Website', 'Address', 'Category', 'Notes'])
    
    # Write data
    for contact in contacts:
        writer.writerow([
            contact.name or '',
            contact.email or '',
            contact.phone or '',
            contact.company or '',
            contact.designation or '',
            contact.website or '',
            contact.address or '',
            contact.category or '',
            contact.notes or ''
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"}
    )

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Contact Management API", "status": "running", "docs": "/docs"}
