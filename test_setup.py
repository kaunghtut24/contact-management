#!/usr/bin/env python3
"""
Simple test script to verify the Contact Management System setup
"""

import requests
import json
import sys
import time

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_database_connection():
    """Test database connection by trying to fetch contacts"""
    try:
        response = requests.get("http://localhost:8000/contacts", timeout=5)
        if response.status_code == 200:
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Database not accessible: {e}")
        return False

def test_create_contact():
    """Test creating a contact"""
    test_contact = {
        "name": "Test User",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "address": "123 Test St",
        "category": "Personal",
        "notes": "Test contact"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/contacts",
            json=test_contact,
            timeout=5
        )
        if response.status_code == 200:
            contact_data = response.json()
            print("✅ Contact creation successful")
            return contact_data.get("id")
        else:
            print(f"❌ Contact creation failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Contact creation error: {e}")
        return None

def test_delete_contact(contact_id):
    """Test deleting a contact"""
    try:
        response = requests.delete(
            f"http://localhost:8000/contacts/{contact_id}",
            timeout=5
        )
        if response.status_code == 200:
            print("✅ Contact deletion successful")
            return True
        else:
            print(f"❌ Contact deletion failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Contact deletion error: {e}")
        return False

def test_frontend():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Contact Management System Setup...\n")
    
    tests_passed = 0
    total_tests = 5
    
    # Test backend health
    if test_backend_health():
        tests_passed += 1
    
    # Test database connection
    if test_database_connection():
        tests_passed += 1
    
    # Test CRUD operations
    contact_id = test_create_contact()
    if contact_id:
        tests_passed += 1
        
        # Test deletion
        if test_delete_contact(contact_id):
            tests_passed += 1
    else:
        print("❌ Skipping contact deletion test")
    
    # Test frontend
    if test_frontend():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your Contact Management System is ready to use.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check your setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
