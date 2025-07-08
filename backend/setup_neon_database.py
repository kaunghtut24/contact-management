#!/usr/bin/env python3
"""
Setup script for Neon PostgreSQL database
This script will create the necessary tables in your Neon database
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.database import engine, SessionLocal
from app.models import Base, Contact
from sqlalchemy import text

def setup_database():
    """Create all tables and verify connection"""
    try:
        print("🔗 Connecting to Neon PostgreSQL database...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"📊 Database version: {version}")
        
        print("\n🏗️  Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables created successfully!")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Created tables: {', '.join(tables)}")
        
        # Test inserting a sample contact
        print("\n🧪 Testing database operations...")
        
        db = SessionLocal()
        try:
            # Check if any contacts exist
            contact_count = db.query(Contact).count()
            print(f"📊 Current contacts in database: {contact_count}")
            
            # If no contacts, create a test contact
            if contact_count == 0:
                test_contact = Contact(
                    name="Test Contact",
                    email="test@example.com",
                    phone="123-456-7890",
                    company="Test Company",
                    designation="Test Position",
                    category="Others",
                    notes="Test contact created during database setup"
                )
                db.add(test_contact)
                db.commit()
                print("✅ Test contact created successfully!")
            
        finally:
            db.close()
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Update your Vercel backend environment variables with:")
        print(f"   DATABASE_URL=postgresql://neondb_owner:npg_oCyiNY6RD4gF@ep-white-river-a8irxian-pooler.eastus2.azure.neon.tech/neondb?sslmode=require")
        print("2. Redeploy your backend on Vercel")
        print("3. Test your application")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\n🔍 Troubleshooting:")
        print("1. Check your DATABASE_URL is correct")
        print("2. Ensure your Neon database is active")
        print("3. Verify network connectivity")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Neon PostgreSQL Database Setup")
    print("=" * 40)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not found, using system environment variables")
    
    # Check if DATABASE_URL is set
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "sqlite" in db_url:
        print("❌ DATABASE_URL not set or still using SQLite")
        print("Please update your .env file with the Neon PostgreSQL URL")
        sys.exit(1)
    
    print(f"🔗 Using database: {db_url.split('@')[1].split('/')[0]}...")
    
    success = setup_database()
    sys.exit(0 if success else 1)
