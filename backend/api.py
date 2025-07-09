"""
Clean, deployment-ready API with authentication and contact management
"""
from fastapi import FastAPI, HTTPException, Depends, status, Query, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
import enum
import io
import csv
from io import StringIO

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contact_management.sqlite")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
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
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

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
    category = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str

class UserRegister(UserCreate):
    confirm_password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserLogin(BaseModel):
    username: str
    password: str

class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = "Others"
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None

class ContactOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    designation: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Security configuration with enhanced settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required for production")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Enhanced password hashing with stronger settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Increased rounds for better security
    bcrypt__ident="2b"  # Use latest bcrypt variant
)
security = HTTPBearer()

# Admin user configuration from environment variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@company.com")
ADMIN_FULL_NAME = os.getenv("ADMIN_FULL_NAME", "System Administrator")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Default user configuration from environment variables
DEFAULT_USER_USERNAME = os.getenv("DEFAULT_USER_USERNAME")
DEFAULT_USER_EMAIL = os.getenv("DEFAULT_USER_EMAIL")
DEFAULT_USER_FULL_NAME = os.getenv("DEFAULT_USER_FULL_NAME")
DEFAULT_USER_PASSWORD = os.getenv("DEFAULT_USER_PASSWORD")

# Security functions
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

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Create FastAPI app
app = FastAPI(
    title="Contact Management System API",
    description="Secure contact management with authentication",
    version="2.0.0"
)

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

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Contact Management System API v2.0 is running"}

# OCR status check
@app.get("/ocr/status")
def ocr_status():
    """Check OCR availability and configuration"""
    try:
        import pytesseract
        from PIL import Image
        import shutil
        import subprocess

        def find_tesseract():
            """Find Tesseract executable in common locations"""
            # Try environment variable first
            env_path = os.getenv('TESSERACT_PATH')
            if env_path and os.path.isfile(env_path):
                return env_path

            # Try shutil.which (Python's built-in)
            which_result = shutil.which('tesseract')
            if which_result:
                return which_result

            # Common Tesseract paths to try
            common_paths = [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract',
                '/opt/homebrew/bin/tesseract',  # macOS with Homebrew
            ]

            for path in common_paths:
                if os.path.isfile(path):
                    return path

            return None

        tesseract_path = find_tesseract()

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

            try:
                version = pytesseract.get_tesseract_version()
                return {
                    "ocr_available": True,
                    "tesseract_path": tesseract_path,
                    "tesseract_version": str(version),
                    "message": "OCR is fully functional"
                }
            except Exception as e:
                return {
                    "ocr_available": False,
                    "tesseract_path": tesseract_path,
                    "error": str(e),
                    "message": "Tesseract found but not working"
                }
        else:
            return {
                "ocr_available": False,
                "tesseract_path": None,
                "message": "Tesseract not found in common locations"
            }

    except ImportError as e:
        return {
            "ocr_available": False,
            "error": str(e),
            "message": "OCR dependencies not installed"
        }

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
        is_active=True
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

@app.post("/auth/login/simple", response_model=Token)
def login_simple(user_data: UserLogin, db: Session = Depends(get_db)):
    """Simple login endpoint for JSON requests"""
    user = authenticate_user(db, user_data.username, user_data.password)
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
    """Create initial admin user from environment variables (only if no users exist)"""
    user_count = db.query(User).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin user already exists or users are present"
        )

    # Validate required environment variables
    if not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_PASSWORD environment variable is required"
        )

    # Check if admin user already exists by username
    existing_admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{ADMIN_USERNAME}' already exists"
        )

    admin_user = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        full_name=ADMIN_FULL_NAME,
        hashed_password=get_password_hash(ADMIN_PASSWORD),
        role=UserRole.ADMIN,
        is_active=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return {
        "message": "Admin user created successfully",
        "username": ADMIN_USERNAME,
        "email": ADMIN_EMAIL,
        "full_name": ADMIN_FULL_NAME,
        "note": "Password is securely stored and hashed"
    }

@app.post("/auth/create-default-user")
def create_default_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create default user from environment variables (admin only)"""
    # Only admin can create default users
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create default users"
        )

    # Validate required environment variables
    if not all([DEFAULT_USER_USERNAME, DEFAULT_USER_EMAIL, DEFAULT_USER_PASSWORD]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DEFAULT_USER_USERNAME, DEFAULT_USER_EMAIL, and DEFAULT_USER_PASSWORD environment variables are required"
        )

    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == DEFAULT_USER_USERNAME) | (User.email == DEFAULT_USER_EMAIL)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{DEFAULT_USER_USERNAME}' or email '{DEFAULT_USER_EMAIL}' already exists"
        )

    default_user = User(
        username=DEFAULT_USER_USERNAME,
        email=DEFAULT_USER_EMAIL,
        full_name=DEFAULT_USER_FULL_NAME or "Default User",
        hashed_password=get_password_hash(DEFAULT_USER_PASSWORD),
        role=UserRole.USER,
        is_active=True
    )

    db.add(default_user)
    db.commit()
    db.refresh(default_user)

    return {
        "message": "Default user created successfully",
        "username": DEFAULT_USER_USERNAME,
        "email": DEFAULT_USER_EMAIL,
        "full_name": default_user.full_name,
        "role": "user",
        "note": "Password is securely stored and hashed"
    }

@app.get("/security/info")
def security_info(current_user: User = Depends(require_admin)):
    """Get security configuration information (admin only)"""
    return {
        "password_hashing": {
            "algorithm": "bcrypt",
            "rounds": 12,
            "variant": "2b"
        },
        "jwt": {
            "algorithm": ALGORITHM,
            "token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
        },
        "environment_variables": {
            "jwt_secret_key_configured": bool(SECRET_KEY),
            "admin_username_configured": bool(ADMIN_USERNAME),
            "admin_password_configured": bool(ADMIN_PASSWORD),
            "default_user_configured": bool(DEFAULT_USER_USERNAME and DEFAULT_USER_EMAIL and DEFAULT_USER_PASSWORD)
        },
        "security_features": [
            "JWT-based authentication",
            "bcrypt password hashing with 12 rounds",
            "Role-based access control",
            "Environment variable configuration",
            "Secure secret management"
        ]
    }

# Contact endpoints (all require authentication)
@app.get("/contacts", response_model=List[ContactOut])
def get_contacts(
    search: str = Query(None, description="Search in name, email, company"),
    category: str = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of contacts to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of contacts to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all contacts with optional search and filtering"""
    query = db.query(Contact)

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Contact.name.ilike(search_term)) |
            (Contact.email.ilike(search_term)) |
            (Contact.company.ilike(search_term)) |
            (Contact.phone.ilike(search_term))
        )

    # Apply category filter
    if category:
        query = query.filter(Contact.category == category)

    # Apply pagination
    contacts = query.offset(skip).limit(limit).all()
    return contacts

@app.post("/contacts", response_model=ContactOut)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contact"""
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/contacts/{contact_id}", response_model=ContactOut)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contact by ID"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@app.put("/contacts/{contact_id}", response_model=ContactOut)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    contact.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)
    return contact

@app.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

@app.delete("/contacts/batch")
def batch_delete_contacts(
    contact_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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

@app.get("/export")
def export_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export all contacts to CSV"""
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

@app.post("/export/batch")
def batch_export_contacts(
    contact_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
