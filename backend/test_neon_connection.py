#!/usr/bin/env python3
"""
Test script to verify Neon PostgreSQL database connection
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.database import engine, SessionLocal
from app.models import Contact
from sqlalchemy import text

def test_connection():
    """Test database connection and basic operations"""
    try:
        print("🔗 Testing Neon PostgreSQL connection...")
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"📊 Database version: {version[:50]}...")
        
        # Test table existence
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'contacts'
            """))
            tables = result.fetchall()
            
            if tables:
                print("✅ 'contacts' table exists")
            else:
                print("❌ 'contacts' table not found")
                return False
        
        # Test basic query
        db = SessionLocal()
        try:
            contact_count = db.query(Contact).count()
            print(f"📊 Total contacts in database: {contact_count}")
            
            # Test a simple query
            recent_contacts = db.query(Contact).limit(3).all()
            if recent_contacts:
                print("📋 Sample contacts:")
                for contact in recent_contacts:
                    print(f"   - {contact.name} ({contact.email})")
            else:
                print("📋 No contacts found in database")
            
        finally:
            db.close()
        
        print("\n🎉 Database connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Neon Database Connection Test")
    print("=" * 35)
    
    db_url = os.getenv("DATABASE_URL", "")
    if "neon.tech" in db_url:
        print("✅ Using Neon PostgreSQL database")
    else:
        print("⚠️  DATABASE_URL doesn't appear to be Neon PostgreSQL")
    
    success = test_connection()
    
    if success:
        print("\n✅ Your database is ready for Vercel deployment!")
        print("\n📝 Next steps:")
        print("1. Update Vercel environment variables (both frontend and backend)")
        print("2. Redeploy both projects")
        print("3. Test your live application")
    else:
        print("\n❌ Please fix database issues before deploying")
