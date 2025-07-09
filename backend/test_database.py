#!/usr/bin/env python3
"""
Test script to verify database operations
"""
import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append('/home/yuthar/contact-management-system/backend')

def test_database_connection():
    """Test database connection and basic operations"""
    try:
        print("🔍 Testing Database Connection...")
        
        from app.database import SessionLocal, engine
        # Import Contact from api.py where it's actually defined
        import sys
        sys.path.append('.')
        from api import Contact, Base
        
        # Test database connection
        print("📊 Testing database connection...")
        db = SessionLocal()
        
        # Check if tables exist
        print("📋 Checking database tables...")
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Available tables: {tables}")
        
        if 'contacts' not in tables:
            print("⚠️ Contacts table not found, creating tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created")
        
        # Count existing contacts
        contact_count = db.query(Contact).count()
        print(f"📊 Current contacts in database: {contact_count}")
        
        # List recent contacts
        recent_contacts = db.query(Contact).order_by(Contact.id.desc()).limit(5).all()
        if recent_contacts:
            print("📋 Recent contacts:")
            for contact in recent_contacts:
                print(f"   ID: {contact.id} | {contact.name} | {contact.email} | {contact.phone}")
        else:
            print("📋 No contacts found in database")
        
        # Test creating a contact
        print("\n🧪 Testing contact creation...")
        test_contact = Contact(
            name="Test Contact",
            designation="Test Engineer",
            company="Test Company",
            email="test@example.com",
            phone="+1-555-TEST",
            website="",
            address="Test Address",
            category="Others",  # Fixed: use 'category' not 'categories'
            notes=""
        )
        
        db.add(test_contact)
        db.commit()
        print("✅ Test contact created successfully")
        
        # Verify the contact was saved
        saved_contact = db.query(Contact).filter(Contact.email == "test@example.com").first()
        if saved_contact:
            print(f"✅ Test contact verified: {saved_contact.name} - {saved_contact.email}")
            
            # Clean up test contact
            db.delete(saved_contact)
            db.commit()
            print("🧹 Test contact cleaned up")
        else:
            print("❌ Test contact not found after creation")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upload_simulation():
    """Simulate the upload process to see where it fails"""
    try:
        print("\n🧪 Testing Upload Simulation...")
        
        from app.database import SessionLocal
        # Import Contact from api.py where it's actually defined
        from api import Contact
        from app.services.content_intelligence import content_intelligence
        import asyncio
        
        # Simulate extracted text from OCR
        test_text = """
        John Doe
        Senior Software Engineer
        Tech Solutions Inc.
        john.doe@techsolutions.com
        +1-555-123-4567
        www.techsolutions.com
        123 Tech Street
        Silicon Valley, CA 94000
        """
        
        print(f"📝 Simulating Content Intelligence analysis...")
        
        # Run Content Intelligence analysis
        async def run_analysis():
            return await content_intelligence.analyze_content(test_text, "text")
        
        analysis_result = asyncio.run(run_analysis())
        
        print(f"📊 Analysis success: {analysis_result['success']}")
        print(f"📊 Contacts found: {len(analysis_result['contacts'])}")
        
        if analysis_result['contacts']:
            contact_data = analysis_result['contacts'][0]
            print(f"👤 First contact: {contact_data}")
            
            # Test database insertion
            print("\n💾 Testing database insertion...")
            db = SessionLocal()
            
            # Fix categories field mapping
            categories = contact_data.get("categories", ["Others"])
            if isinstance(categories, list):
                category_str = categories[0] if categories else "Others"
            else:
                category_str = str(categories) if categories else "Others"
            
            # Create contact with correct field mapping
            db_contact_data = {
                "name": contact_data.get("name", ""),
                "designation": contact_data.get("designation", ""),
                "company": contact_data.get("company", ""),
                "email": contact_data.get("email", ""),
                "phone": contact_data.get("phone", ""),
                "website": contact_data.get("website", ""),
                "address": contact_data.get("address", ""),
                "category": category_str,  # Fixed: use 'category' not 'categories'
                "notes": f"Test upload - {datetime.now().isoformat()}"
            }
            
            print(f"💾 Creating contact with data: {db_contact_data}")
            
            db_contact = Contact(**db_contact_data)
            db.add(db_contact)
            db.commit()
            
            print(f"✅ Contact created with ID: {db_contact.id}")
            
            # Verify it's in the database
            saved_contact = db.query(Contact).filter(Contact.id == db_contact.id).first()
            if saved_contact:
                print(f"✅ Contact verified in database: {saved_contact.name}")
                print(f"📊 Total contacts now: {db.query(Contact).count()}")
            else:
                print("❌ Contact not found after creation")
            
            db.close()
            return True
        else:
            print("❌ No contacts extracted from Content Intelligence")
            return False
            
    except Exception as e:
        print(f"❌ Upload simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all database tests"""
    print("🧪 Database Test Suite")
    print("=" * 50)
    
    # Test 1: Database connection
    db_result = test_database_connection()
    
    # Test 2: Upload simulation
    upload_result = test_upload_simulation()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Database Connection: {'✅ Working' if db_result else '❌ Failed'}")
    print(f"   Upload Simulation: {'✅ Working' if upload_result else '❌ Failed'}")
    
    if db_result and upload_result:
        print("\n🎉 All tests passed! Database operations are working correctly.")
        print("💡 If contacts aren't showing in the frontend, the issue is likely:")
        print("   1. Frontend not refreshing after upload")
        print("   2. API endpoint for fetching contacts has issues")
        print("   3. CORS or network issues between frontend and backend")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
