#!/usr/bin/env python3
"""
Initialize the database with the correct schema
"""
import sys
import os
sys.path.append('.')

from sqlalchemy import create_engine
from app.models import Base
from app.config import settings

def init_database():
    """Initialize the database with the correct schema"""
    print("Initializing database with new schema...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")
    print(f"   Database URL: {settings.DATABASE_URL}")
    print("   Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")

if __name__ == "__main__":
    init_database()
