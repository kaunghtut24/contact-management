#!/usr/bin/env python3
"""
Migration script to create MySQL schema for PlanetScale
Run this after setting up your PlanetScale database
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.models import Base
from app.config import settings

def create_mysql_schema():
    """Create tables in MySQL database"""
    print("🚀 Creating MySQL schema for PlanetScale...")
    
    # Check if DATABASE_URL is set
    if not settings.DATABASE_URL or settings.DATABASE_URL.startswith("sqlite"):
        print("❌ Please set DATABASE_URL to your PlanetScale connection string")
        print("Example: mysql://username:password@host:port/database_name")
        sys.exit(1)
    
    try:
        # Create engine
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "charset": "utf8mb4",
                "ssl_disabled": False
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Verify tables
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"✅ Created tables: {', '.join(tables)}")
        
        print("\n🎉 MySQL schema setup complete!")
        print("You can now deploy your application to Vercel")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        sys.exit(1)

def migrate_data_from_sqlite():
    """Optional: Migrate existing data from SQLite to MySQL"""
    sqlite_path = "contact_db.sqlite"
    
    if not os.path.exists(sqlite_path):
        print("ℹ️  No SQLite database found, skipping data migration")
        return
    
    print("📦 Migrating data from SQLite to MySQL...")
    
    # This is a basic example - you might need to customize based on your data
    try:
        from sqlalchemy.orm import sessionmaker
        
        # SQLite connection
        sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
        SqliteSession = sessionmaker(bind=sqlite_engine)
        
        # MySQL connection
        mysql_engine = create_engine(settings.DATABASE_URL)
        MysqlSession = sessionmaker(bind=mysql_engine)
        
        # Import your models
        from app.models import Contact
        
        with SqliteSession() as sqlite_session, MysqlSession() as mysql_session:
            # Get all contacts from SQLite
            contacts = sqlite_session.query(Contact).all()
            
            for contact in contacts:
                # Create new contact in MySQL
                new_contact = Contact(
                    name=contact.name,
                    designation=contact.designation,
                    company=contact.company,
                    telephone=contact.telephone,
                    email=contact.email,
                    website=contact.website,
                    category=contact.category,
                    address=contact.address,
                    notes=contact.notes
                )
                mysql_session.add(new_contact)
            
            mysql_session.commit()
            print(f"✅ Migrated {len(contacts)} contacts")
    
    except Exception as e:
        print(f"⚠️  Data migration failed: {e}")
        print("You can manually export/import your data if needed")

if __name__ == "__main__":
    print("🗄️  PlanetScale Migration Tool")
    print("=" * 40)
    
    create_mysql_schema()
    
    # Ask user if they want to migrate data
    if input("\nMigrate existing SQLite data? (y/N): ").lower() == 'y':
        migrate_data_from_sqlite()
    
    print("\n📋 Next Steps:")
    print("1. Deploy backend to Vercel")
    print("2. Deploy frontend to Vercel") 
    print("3. Set environment variables in Vercel dashboard")
    print("4. Test your application!")
