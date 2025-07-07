#!/usr/bin/env python3
"""
Database migration script to add new columns to existing contacts table
"""
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add new columns to the contacts table"""
    db_path = Path("contacts.db")
    
    if not db_path.exists():
        logger.info("Database doesn't exist yet, will be created with new schema")
        return
    
    logger.info("Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            ('designation', 'TEXT'),
            ('company', 'TEXT'),
            ('telephone', 'TEXT'),
            ('website', 'TEXT')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                logger.info(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column_name} {column_type}")
            else:
                logger.info(f"Column {column_name} already exists")
        
        # Migrate data from old columns to new columns where appropriate
        logger.info("Migrating data from legacy fields...")
        
        # Copy phone to telephone if telephone is empty
        cursor.execute("""
            UPDATE contacts 
            SET telephone = phone 
            WHERE telephone IS NULL AND phone IS NOT NULL AND phone != ''
        """)
        
        # Try to extract company information from address field
        cursor.execute("""
            UPDATE contacts 
            SET company = address 
            WHERE company IS NULL 
            AND address IS NOT NULL 
            AND address != ''
            AND (
                LOWER(address) LIKE '%office%' OR
                LOWER(address) LIKE '%building%' OR
                LOWER(address) LIKE '%tower%' OR
                LOWER(address) LIKE '%complex%' OR
                LOWER(address) LIKE '%center%' OR
                LOWER(address) LIKE '%plaza%' OR
                LOWER(address) LIKE '%ltd%' OR
                LOWER(address) LIKE '%inc%' OR
                LOWER(address) LIKE '%corp%'
            )
        """)
        
        conn.commit()
        logger.info("Database migration completed successfully!")
        
        # Show migration statistics
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE telephone IS NOT NULL AND telephone != ''")
        telephone_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE company IS NOT NULL AND company != ''")
        company_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contacts")
        total_count = cursor.fetchone()[0]
        
        logger.info(f"Migration Statistics:")
        logger.info(f"  Total contacts: {total_count}")
        logger.info(f"  Contacts with telephone: {telephone_count}")
        logger.info(f"  Contacts with company: {company_count}")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
