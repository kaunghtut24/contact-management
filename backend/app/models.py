from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime
import enum
from sqlalchemy import Boolean, Enum

from .database import Base

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    designation = Column(String, nullable=True)
    company = Column(String, nullable=True, index=True)
    telephone = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    website = Column(String, nullable=True)
    category = Column(String, nullable=True, default="Others")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Legacy fields for backward compatibility (will be migrated)
    phone = Column(String, nullable=True)  # Maps to telephone
    address = Column(Text, nullable=True)  # Maps to company address or notes

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)    

from .database import engine

Base.metadata.create_all(bind=engine)