from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Query, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
import io
import csv
import os
from io import StringIO
from datetime import datetime, timedelta

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
    from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
    from sqlalchemy.ext.declarative import declarative_base
    from datetime import datetime
    from pydantic import BaseModel, EmailStr
    from passlib.context import CryptContext
    from jose import JWTError, jwt
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    import enum
    
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

    # User model for authentication
    class UserRole(enum.Enum):
        ADMIN = "admin"
        USER = "user"
        VIEWER = "viewer"

    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        username = Column(String(50), unique=True, index=True, nullable=False)
        email = Column(String(255), unique=True, index=True, nullable=False)
        hashed_password = Column(String(255), nullable=False)
        full_name = Column(String(255))
        role = Column(Enum(UserRole), default=UserRole.USER)
        is_active = Column(Boolean, default=True)
        is_verified = Column(Boolean, default=False)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        last_login = Column(DateTime)

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

    # Authentication schemas
    class Token(BaseModel):
        access_token: str
        token_type: str
        expires_in: int

    class UserLogin(BaseModel):
        username: str
        password: str

    class UserRegister(BaseModel):
        username: str
        email: str
        full_name: str = None
        password: str
        confirm_password: str

    class UserOut(BaseModel):
        id: int
        username: str
        email: str
        full_name: str = None
        role: UserRole
        is_active: bool
        created_at: datetime
        last_login: datetime = None

        class Config:
            from_attributes = True

    # Security configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    security = HTTPBearer()

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return username
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_user_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def authenticate_user(db: Session, username: str, password: str):
        user = get_user_by_username(db, username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ):
        token = credentials.credentials
        username = verify_token(token)
        user = get_user_by_username(db, username=username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user

# Create FastAPI app
app = FastAPI(title="Contact Management API", version="1.0.0")

# CORS Configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://contact-management-six-alpha.vercel.app,http://localhost:5173,http://localhost:3000,http://localhost:5174").split(",")

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

# Authentication endpoints
@app.post("/auth/register", response_model=UserOut)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=UserRole.USER,
        is_active=True,
        is_verified=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@app.post("/auth/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.utcnow()
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/auth/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/auth/create-admin")
def create_admin_user(db: Session = Depends(get_db)):
    """Create initial admin user (only if no users exist)"""
    user_count = db.query(User).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists or users are present"
        )

    admin_user = User(
        username="admin",
        email="admin@example.com",
        full_name="System Administrator",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return {"message": "Admin user created successfully", "username": "admin", "password": "admin123"}

# Get all contacts (now requires authentication)
@app.get("/contacts", response_model=List[ContactOut])
def get_contacts(
    search: str = Query(None, description="Search in name, email, company"),
    category: str = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

# Batch export selected contacts
@app.post("/export/batch")
def batch_export_contacts(contact_ids: List[int], db: Session = Depends(get_db)):
    """Export selected contacts to CSV"""
    contacts = db.query(Contact).filter(Contact.id.in_(contact_ids)).all()

    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found with provided IDs")

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
        headers={"Content-Disposition": f"attachment; filename=selected_contacts_{len(contacts)}.csv"}
    )

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Contact Management API", "status": "running", "docs": "/docs"}
