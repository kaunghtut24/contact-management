"""
Clean, deployment-ready API with authentication and contact management
"""
from fastapi import FastAPI, HTTPException, Depends, status, Query, UploadFile, File, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from datetime import datetime, timedelta
from typing import Optional, List
import os
import enum
import io
import csv
import warnings
from io import StringIO

# Suppress bcrypt version warning and other non-critical warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*error reading bcrypt version.*")

# Configure logging for production
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress the specific passlib bcrypt warning
logging.getLogger("passlib").setLevel(logging.ERROR)

# Create logger for this module
logger = logging.getLogger(__name__)

# Database setup with connection pooling and SSL configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contact_management.sqlite")

# Configure engine with proper connection pooling and SSL settings
if "postgresql" in DATABASE_URL:
    # PostgreSQL configuration with connection pooling and SSL
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        connect_args={
            "sslmode": "require",
            "connect_timeout": 10,
            "application_name": "contact_management_api"
        }
    )
else:
    # SQLite configuration for local development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

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
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # For development/testing, use a default key with warning
    SECRET_KEY = "development-secret-key-change-in-production-minimum-32-characters"
    logger.warning("Using default JWT secret key. Set JWT_SECRET_KEY environment variable in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 hours default

# Enhanced password hashing with stronger settings
try:
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=12,  # Increased rounds for better security
        bcrypt__ident="2b"  # Use latest bcrypt variant
    )
except Exception as e:
    logger.warning(f"bcrypt configuration warning (non-critical): {e}")
    # Fallback to basic bcrypt configuration
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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
    """Verify JWT token and return username"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except ExpiredSignatureError:
        # Handle expired tokens gracefully
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # Use proper logging instead of print
        error_msg = str(e)
        if "Signature verification failed" in error_msg:
            logger.info(f"JWT signature verification failed - likely due to secret key change: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired due to security update. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            logger.warning(f"JWT verification failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        # Catch any other unexpected errors
        import logging
        logging.error(f"Unexpected error in token verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Please login again.",
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

# Simplified database dependency to avoid context manager issues
def get_db():
    """Database dependency with simplified error handling"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user with improved error handling"""
    try:
        token = credentials.credentials
        username = verify_token(token)

        # Query user with error handling
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
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any unexpected database or other errors
        import logging
        logging.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

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

# CORS Configuration for local development and production
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    # Allow all origins for local development
    ALLOWED_ORIGINS = ["*"]
    ALLOW_CREDENTIALS = False  # Can't use credentials with wildcard origins
else:
    # Specific origins for production
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://contact-management-six-alpha.vercel.app").split(",")
    ALLOW_CREDENTIALS = True

logger.info(f"CORS Configuration - Environment: {ENVIRONMENT}")
logger.info(f"CORS Allowed Origins: {ALLOWED_ORIGINS}")
logger.info(f"CORS Allow Credentials: {ALLOW_CREDENTIALS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper CORS headers"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Create tables
Base.metadata.create_all(bind=engine)

# Startup message
logger.info("Contact Management System API v2.0 starting...")
logger.info("Authentication: JWT with bcrypt password hashing")
logger.info("Database: Connected and tables created")
logger.info("System ready for requests")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Contact Management System API v2.0", "status": "running", "docs": "/docs"}

# Health check
@app.get("/health")
def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "message": "Contact Management System API v2.0 is running",
        "timestamp": datetime.utcnow().isoformat()
    }

# Database health check
@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """Check database connectivity"""
    try:
        # Test database connection
        result = db.execute(text("SELECT 1 as test")).fetchone()
        user_count = db.query(User).count()
        contact_count = db.query(Contact).count()

        return {
            "status": "healthy",
            "database": "connected",
            "test_query": "successful",
            "users_count": user_count,
            "contacts_count": contact_count,
            "message": "Database is accessible and responsive"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "message": "Database connection failed"
        }

# Database connection pool status
@app.get("/health/db/pool")
def database_pool_status():
    """Check database connection pool status"""
    try:
        pool = engine.pool
        return {
            "status": "healthy",
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "message": "Connection pool status retrieved successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to retrieve connection pool status"
        }

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

            # Set bundled tessdata path
            bundled_tessdata = os.path.join(os.path.dirname(__file__), 'tessdata')
            if os.path.isdir(bundled_tessdata) and os.path.isfile(os.path.join(bundled_tessdata, 'eng.traineddata')):
                os.environ['TESSDATA_PREFIX'] = bundled_tessdata
                tessdata_source = "bundled"
                tessdata_path = bundled_tessdata
            else:
                tessdata_path = os.getenv('TESSDATA_PREFIX', 'system default')
                tessdata_source = "system"

            try:
                version = pytesseract.get_tesseract_version()

                # List available languages
                available_languages = []
                if tessdata_source == "bundled":
                    try:
                        lang_files = [f for f in os.listdir(bundled_tessdata) if f.endswith('.traineddata')]
                        available_languages = [f.replace('.traineddata', '') for f in lang_files]
                    except:
                        pass

                return {
                    "ocr_available": True,
                    "tesseract_path": tesseract_path,
                    "tesseract_version": str(version),
                    "tessdata_source": tessdata_source,
                    "tessdata_path": tessdata_path,
                    "available_languages": available_languages,
                    "message": "OCR is fully functional"
                }
            except Exception as e:
                return {
                    "ocr_available": False,
                    "tesseract_path": tesseract_path,
                    "tessdata_source": tessdata_source,
                    "tessdata_path": tessdata_path,
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

@app.get("/debug/env-check")
def check_environment_variables():
    """Check what environment variables are configured (temporary diagnostic endpoint)"""
    return {
        "admin_username_configured": bool(ADMIN_USERNAME),
        "admin_username_value": ADMIN_USERNAME if ADMIN_USERNAME else "NOT_SET",
        "admin_email_configured": bool(ADMIN_EMAIL),
        "admin_email_value": ADMIN_EMAIL if ADMIN_EMAIL else "NOT_SET",
        "admin_password_configured": bool(ADMIN_PASSWORD),
        "jwt_secret_configured": bool(SECRET_KEY),
        "environment_variables_status": {
            "ADMIN_USERNAME": "SET" if ADMIN_USERNAME else "NOT_SET",
            "ADMIN_EMAIL": "SET" if ADMIN_EMAIL else "NOT_SET",
            "ADMIN_PASSWORD": "SET" if ADMIN_PASSWORD else "NOT_SET",
            "JWT_SECRET_KEY": "SET" if SECRET_KEY else "NOT_SET"
        }
    }

@app.post("/auth/reset-admin")
def reset_admin_user(db: Session = Depends(get_db)):
    """Reset admin user with current environment variables (emergency endpoint)"""
    if not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_PASSWORD environment variable is required"
        )

    # Find existing admin user
    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()

    if admin_user:
        # Update existing admin with new credentials
        admin_user.username = ADMIN_USERNAME
        admin_user.email = ADMIN_EMAIL
        admin_user.full_name = ADMIN_FULL_NAME
        admin_user.hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin_user.is_active = True

        db.commit()
        db.refresh(admin_user)

        return {
            "message": "Admin user updated successfully",
            "username": ADMIN_USERNAME,
            "email": ADMIN_EMAIL,
            "full_name": ADMIN_FULL_NAME,
            "note": "Admin credentials updated from environment variables"
        }
    else:
        # Create new admin if none exists
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
            "note": "New admin user created from environment variables"
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

# Batch operations must come before parameterized routes to avoid conflicts
class BatchDeleteRequest(BaseModel):
    contact_ids: List[int]

@app.delete("/contacts/batch")
def batch_delete_contacts(
    request: BatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple contacts by their IDs"""
    deleted_count = 0
    failed_ids = []

    for contact_id in request.contact_ids:
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

class BatchExportRequest(BaseModel):
    contact_ids: List[int]

@app.post("/export/batch")
def batch_export_contacts(
    request: BatchExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export selected contacts to CSV"""
    contacts = db.query(Contact).filter(Contact.id.in_(request.contact_ids)).all()

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

# File upload and processing endpoints
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process contact files (CSV, VCF, images, etc.) with timeout handling"""
    import asyncio

    try:
        # Calculate overall timeout based on file size (optimized for Render)
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        file_size_mb = len(content) / (1024 * 1024)

        # Reject files that are too large for Render processing
        is_render = os.getenv("ENVIRONMENT") == "production"
        max_size_mb = 1.5 if is_render else 2.0

        if file_size_mb > max_size_mb:
            logger.warning(f"File too large for processing: {file_size_mb:.1f}MB (max: {max_size_mb}MB)")
            return {
                "message": "File too large for processing",
                "filename": file.filename,
                "contacts_created": 0,
                "errors": [f"File size {file_size_mb:.1f}MB exceeds maximum {max_size_mb}MB for reliable processing on our servers. Please compress or resize the image."],
                "total_errors": 1,
                "file_too_large": True
            }

        # Use environment variables for timeout configuration (Render-optimized)
        base_timeout = float(os.getenv("UPLOAD_TIMEOUT_OVERALL", "30"))

        if file_size_mb > 1.0:
            overall_timeout = min(base_timeout - 5, 25.0)  # Max 25s for 1-1.5MB
        else:
            overall_timeout = min(base_timeout - 10, 20.0)  # Max 20s for <1MB

        logger.info(f"Processing {file_size_mb:.1f}MB file with {overall_timeout}s overall timeout")

        # Add overall timeout for the entire upload process
        return await asyncio.wait_for(_process_upload_file(file, db), timeout=overall_timeout)
    except asyncio.TimeoutError:
        logger.error(f"Upload processing timed out for file: {file.filename}")
        return {
            "message": "File upload timed out",
            "filename": file.filename,
            "contacts_created": 0,
            "errors": [f"Upload processing timed out after {overall_timeout} seconds. Please try with a smaller file."],
            "total_errors": 1,
            "timeout": True
        }
    except Exception as e:
        logger.error(f"Upload processing failed for file {file.filename}: {str(e)}")
        return {
            "message": "File upload failed",
            "filename": file.filename,
            "contacts_created": 0,
            "errors": [f"Upload failed: {str(e)}"],
            "total_errors": 1
        }

async def _process_upload_file(file: UploadFile, db: Session):
    """Internal function to process uploaded files"""
    try:
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()

        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10MB."
            )

        # Reset file pointer
        await file.seek(0)

        # Determine file type and process accordingly
        filename = file.filename.lower()
        contacts_created = 0
        errors = []

        if filename.endswith('.csv'):
            # Process CSV file
            content_str = content.decode('utf-8')
            lines = content_str.strip().split('\n')

            if len(lines) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSV file must have at least a header and one data row"
                )

            # Simple CSV processing (assuming standard format)
            header = lines[0].split(',')
            for line in lines[1:]:
                try:
                    values = line.split(',')
                    if len(values) >= 2:  # At least name and one other field
                        contact_data = {
                            'name': values[0].strip('"'),
                            'email': values[1].strip('"') if len(values) > 1 else None,
                            'phone': values[2].strip('"') if len(values) > 2 else None,
                            'company': values[3].strip('"') if len(values) > 3 else None,
                            'category': 'Others'
                        }

                        # Create contact
                        db_contact = Contact(**contact_data)
                        db.add(db_contact)
                        contacts_created += 1

                except Exception as e:
                    errors.append(f"Error processing line: {line[:50]}... - {str(e)}")

            db.commit()

        elif filename.endswith('.vcf'):
            # Process VCF file
            content_str = content.decode('utf-8')
            vcf_contacts = content_str.split('BEGIN:VCARD')

            for vcf_contact in vcf_contacts[1:]:  # Skip first empty element
                try:
                    lines = vcf_contact.split('\n')
                    contact_data = {'name': '', 'email': None, 'phone': None, 'category': 'Others'}

                    for line in lines:
                        if line.startswith('FN:'):
                            contact_data['name'] = line[3:].strip()
                        elif line.startswith('EMAIL'):
                            contact_data['email'] = line.split(':')[1].strip()
                        elif line.startswith('TEL'):
                            contact_data['phone'] = line.split(':')[1].strip()
                        elif line.startswith('ORG:'):
                            contact_data['company'] = line[4:].strip()

                    if contact_data['name']:
                        db_contact = Contact(**contact_data)
                        db.add(db_contact)
                        contacts_created += 1

                except Exception as e:
                    errors.append(f"Error processing VCF contact - {str(e)}")

            db.commit()

        elif filename.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            # Process image files with OCR (with timeout handling)
            try:
                import asyncio
                from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
                # Import the fast parsing function
                try:
                    from app.parsers.parse import parse_image_fast
                    parse_func = parse_image_fast
                except ImportError:
                    # Fallback to regular parse_image if fast version not available
                    from app.parsers.parse import parse_image
                    parse_func = parse_image

                # Calculate timeout based on file size (Render-optimized)
                file_size_mb = len(content) / (1024 * 1024)

                # Use environment variables for OCR timeout (Render deployment)
                # More aggressive timeouts for Render
                is_render = os.getenv("ENVIRONMENT") == "production"

                if is_render:
                    # Render: Very aggressive timeouts
                    if file_size_mb > 1.0:
                        ocr_timeout = 15  # 15s max for 1-1.5MB files on Render
                    else:
                        ocr_timeout = 10  # 10s for small files on Render
                else:
                    # Local/other deployments: Use environment variables
                    small_timeout = int(os.getenv("OCR_TIMEOUT_SMALL", "15"))
                    medium_timeout = int(os.getenv("OCR_TIMEOUT_MEDIUM", "20"))

                    if file_size_mb > 1.0:
                        ocr_timeout = medium_timeout  # 20s for medium files
                    else:
                        ocr_timeout = small_timeout  # 15s for small files

                logger.info(f"Processing {file_size_mb:.1f}MB image with {ocr_timeout}s timeout")

                # Use a thread pool to run OCR with dynamic timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    try:
                        future = executor.submit(parse_func, content)
                        contacts_data = future.result(timeout=ocr_timeout)

                        for contact_data in contacts_data:
                            try:
                                # Create contact
                                db_contact = Contact(**contact_data)
                                db.add(db_contact)
                                contacts_created += 1
                            except Exception as e:
                                errors.append(f"Error creating contact from OCR: {str(e)}")

                        db.commit()

                        return {
                            "message": "Image processed with OCR successfully",
                            "filename": file.filename,
                            "contacts_created": contacts_created,
                            "errors": errors,
                            "total_errors": len(errors),
                            "ocr_used": True
                        }

                    except FutureTimeoutError:
                        logger.warning(f"OCR processing timed out for file: {file.filename} ({file_size_mb:.1f}MB) after {ocr_timeout}s")

                        # Provide specific guidance based on file size and environment
                        is_render = os.getenv("ENVIRONMENT") == "production"
                        if is_render:
                            if file_size_mb > 1.0:
                                error_msg = f"Image too large ({file_size_mb:.1f}MB) for our servers. Please use images smaller than 1MB for reliable processing."
                            else:
                                error_msg = f"OCR processing timed out after {ocr_timeout}s. Try using a clearer, higher-contrast image."
                        else:
                            error_msg = f"OCR processing timed out after {ocr_timeout} seconds. For {file_size_mb:.1f}MB files, try reducing image size or using a clearer image."

                        errors.append(error_msg)
                        return {
                            "message": "Image uploaded but OCR processing timed out",
                            "filename": file.filename,
                            "size": len(content),
                            "contacts_created": 0,
                            "errors": errors,
                            "total_errors": len(errors),
                            "ocr_used": False,
                            "timeout": True,
                            "file_size_mb": file_size_mb,
                            "suggested_max_size": 1.0 if is_render else 1.5
                        }

            except Exception as e:
                logger.error(f"OCR processing failed for file {file.filename}: {str(e)}")
                errors.append(f"OCR processing failed: {str(e)}")
                return {
                    "message": "Image uploaded but OCR processing failed",
                    "filename": file.filename,
                    "size": len(content),
                    "contacts_created": 0,
                    "errors": errors,
                    "total_errors": len(errors),
                    "ocr_used": False
                }

        else:
            # For other file types
            return {
                "message": "File uploaded successfully",
                "filename": file.filename,
                "size": len(content),
                "note": "File type not supported for automatic processing",
                "contacts_created": 0,
                "errors": ["Unsupported file type for contact extraction"]
            }

        return {
            "message": "File processed successfully",
            "filename": file.filename,
            "contacts_created": contacts_created,
            "errors": errors,
            "total_errors": len(errors)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
