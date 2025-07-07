from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

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