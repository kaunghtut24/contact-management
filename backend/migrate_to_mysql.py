#!/usr/bin/env python3
"""
Migration script to create PostgreSQL schema for Neon
Run this after setting up your Neon database
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.models import Base
from app.config import settings

def create_postgresql_schema():
    """Create tables in PostgreSQL database"""
    print("🚀 Creating PostgreSQL schema for Neon...")

    # Check if DATABASE_URL is set
    if not settings.DATABASE_URL or settings.DATABASE_URL.startswith("sqlite"):
        print("❌ Please set DATABASE_URL to your Neon connection string")
        print("Example: postgresql://username:password@host:port/database_name")
        sys.exit(1)
    
    try:
        # Create engine
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "sslmode": "require"
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
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            print(f"✅ Created tables: {', '.join(tables)}")

        print("\n🎉 PostgreSQL schema setup complete!")
        print("You can now deploy your application to Vercel")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        sys.exit(1)

def migrate_data_from_sqlite():
    """Optional: Migrate existing data from SQLite to PostgreSQL"""
    sqlite_path = "contact_db.sqlite"
    
    if not os.path.exists(sqlite_path):
        print("ℹ️  No SQLite database found, skipping data migration")
        return
    
    print("📦 Migrating data from SQLite to PostgreSQL...")

    # This is a basic example - you might need to customize based on your data
    try:
        from sqlalchemy.orm import sessionmaker

        # SQLite connection
        sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
        SqliteSession = sessionmaker(bind=sqlite_engine)

        # PostgreSQL connection
        postgresql_engine = create_engine(settings.DATABASE_URL)
        PostgresqlSession = sessionmaker(bind=postgresql_engine)
        
        # Import your models
        from app.models import Contact
        
        with SqliteSession() as sqlite_session, PostgresqlSession() as postgresql_session:
            # Get all contacts from SQLite
            contacts = sqlite_session.query(Contact).all()
            
            for contact in contacts:
                # Create new contact in PostgreSQL
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
                postgresql_session.add(new_contact)

            postgresql_session.commit()
            print(f"✅ Migrated {len(contacts)} contacts")
    
    except Exception as e:
        print(f"⚠️  Data migration failed: {e}")
        print("You can manually export/import your data if needed")

if __name__ == "__main__":
    print("🗄️  Neon PostgreSQL Migration Tool")
    print("=" * 40)

    create_postgresql_schema()
    
    # Ask user if they want to migrate data
    if input("\nMigrate existing SQLite data? (y/N): ").lower() == 'y':
        migrate_data_from_sqlite()
    
    print("\n📋 Next Steps:")
    print("1. Deploy backend to Vercel")
    print("2. Deploy frontend to Vercel") 
    print("3. Set environment variables in Vercel dashboard")
    print("4. Test your application!")
