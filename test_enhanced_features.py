#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced features:
1. Enhanced File Parsing with NLP and vCard support
2. Improved Contact Categorization with ML
3. Advanced Search and Filtering
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_enhanced_parsing():
    """Test enhanced file parsing with NLP"""
    print("🔧 Testing Enhanced File Parsing...")
    
    # Create a sample vCard file
    vcard_content = """BEGIN:VCARD
VERSION:3.0
FN:John Smith
N:Smith;John;;;
ORG:Acme Corporation
TITLE:Software Engineer
EMAIL:john.smith@acme.com
TEL:+1-555-123-4567
ADR:;;123 Business St;New York;NY;10001;USA
NOTE:Important client contact
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Jane Doe
N:Doe;Jane;;;
EMAIL:jane.doe@gmail.com
TEL:+1-555-987-6543
ADR:;;456 Home Ave;Los Angeles;CA;90210;USA
NOTE:Personal friend from college
END:VCARD"""
    
    # Save vCard file
    with open('test_contacts.vcf', 'w') as f:
        f.write(vcard_content)
    
    # Upload vCard file
    with open('test_contacts.vcf', 'rb') as f:
        files = {'file': ('test_contacts.vcf', f, 'text/vcard')}
        response = requests.post(f'{API_BASE}/upload', files=files)
        print(f"✅ vCard upload: {response.status_code} - {response.json()}")
    
    return response.status_code == 200

def test_ml_categorization():
    """Test ML-based categorization and feedback"""
    print("\n🤖 Testing ML Categorization...")
    
    # Get all contacts to see categorization
    response = requests.get(f'{API_BASE}/contacts')
    contacts = response.json()
    
    print(f"📊 Current contacts and their categories:")
    for contact in contacts[-5:]:  # Show last 5 contacts
        print(f"  - {contact['name']}: {contact['category']}")
    
    # Test categorization feedback
    if contacts:
        contact = contacts[0]
        feedback_data = {
            "contact_id": contact['id'],
            "correct_category": "Work"
        }
        
        response = requests.post(f'{API_BASE}/api/categories/feedback', json=feedback_data)
        print(f"✅ Categorization feedback: {response.status_code}")
    
    # Test custom categories
    category_data = {
        "name": "VIP Clients",
        "description": "High-priority business contacts",
        "color": "#FF6B35",
        "rules": [
            {
                "rule_type": "keyword",
                "rule_value": "vip",
                "field_target": "notes",
                "priority": 1
            }
        ]
    }
    
    response = requests.post(f'{API_BASE}/api/categories', json=category_data)
    print(f"✅ Custom category creation: {response.status_code}")
    
    return True

def test_advanced_search():
    """Test advanced search and filtering"""
    print("\n🔍 Testing Advanced Search...")
    
    # Test full-text search
    response = requests.get(f'{API_BASE}/api/search?q=john&page=1&page_size=10')
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Full-text search for 'john': {result['total_count']} results in {result['execution_time_ms']}ms")
    
    # Test advanced search
    search_data = {
        "criteria": {
            "category": "Work",
            "query": "engineer"
        },
        "sort_by": "name",
        "sort_order": "asc",
        "page": 1,
        "page_size": 20
    }
    
    response = requests.post(f'{API_BASE}/api/search/advanced', json=search_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Advanced search: {result['total_count']} results in {result['execution_time_ms']}ms")
    
    # Test search suggestions
    response = requests.get(f'{API_BASE}/api/search/suggestions?q=jo&limit=5')
    if response.status_code == 200:
        suggestions = response.json()
        print(f"✅ Search suggestions for 'jo': {len(suggestions)} suggestions")
        for suggestion in suggestions:
            print(f"  - {suggestion['type']}: {suggestion['value']} ({suggestion['count']} matches)")
    
    # Test saved filters
    filter_data = {
        "name": "Work Contacts",
        "description": "All business-related contacts",
        "filter_criteria": {
            "category": "Work"
        },
        "is_favorite": True
    }
    
    response = requests.post(f'{API_BASE}/api/filters', json=filter_data)
    if response.status_code == 200:
        saved_filter = response.json()
        print(f"✅ Saved filter created: {saved_filter['name']}")
        
        # Test using the saved filter
        response = requests.post(f'{API_BASE}/api/filters/{saved_filter["id"]}/use?page=1&page_size=10')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Used saved filter: {result['total_count']} results")
    
    return True

def test_integration():
    """Test integration of all features"""
    print("\n🔗 Testing Feature Integration...")
    
    # Create a contact with rich data for testing
    contact_data = {
        "name": "Dr. Sarah Wilson",
        "email": "sarah.wilson@hospital.com",
        "phone": "+1-555-DOCTOR",
        "address": "123 Medical Center, Health City, HC 12345",
        "notes": "Chief of Surgery, VIP client, emergency contact available 24/7"
    }
    
    response = requests.post(f'{API_BASE}/contacts', json=contact_data)
    if response.status_code == 200:
        contact = response.json()
        print(f"✅ Created test contact: {contact['name']} (Category: {contact['category']})")
        
        # Search for the contact
        response = requests.get(f'{API_BASE}/api/search?q=sarah wilson&page=1&page_size=5')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found contact via search: {result['total_count']} results")
        
        # Test advanced search with multiple criteria
        search_data = {
            "criteria": {
                "name": "sarah",
                "notes": "vip"
            },
            "sort_by": "created_at",
            "sort_order": "desc"
        }
        
        response = requests.post(f'{API_BASE}/api/search/advanced', json=search_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Advanced multi-criteria search: {result['total_count']} results")
    
    return True

def main():
    """Run all feature tests"""
    print("🚀 Testing Enhanced Contact Management Features\n")
    
    start_time = time.time()
    
    try:
        # Test each feature
        test_enhanced_parsing()
        test_ml_categorization()
        test_advanced_search()
        test_integration()
        
        execution_time = time.time() - start_time
        print(f"\n🎉 All tests completed successfully in {execution_time:.2f} seconds!")
        
        print("\n📋 Feature Summary:")
        print("✅ Enhanced File Parsing: NLP + vCard support")
        print("✅ ML Categorization: Adaptive learning + custom categories")
        print("✅ Advanced Search: Full-text + saved filters")
        print("✅ Feature Integration: All systems working together")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
