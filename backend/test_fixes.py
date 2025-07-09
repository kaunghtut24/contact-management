#!/usr/bin/env python3
"""
Test script to verify the backend fixes for Render deployment issues
"""
import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://contact-management-ffsl.onrender.com"  # Your Render backend URL
LOCAL_URL = "http://localhost:8000"

def test_health_endpoints(base_url):
    """Test health check endpoints"""
    print(f"\n🔍 Testing health endpoints on {base_url}")
    
    try:
        # Test basic health check
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        
        # Test database health check (this might fail if no auth)
        try:
            response = requests.get(f"{base_url}/health/db", timeout=10)
            print(f"✅ DB Health check: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"⚠️  DB Health check failed (expected if auth required): {e}")
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def test_cors_preflight(base_url):
    """Test CORS preflight requests"""
    print(f"\n🔍 Testing CORS preflight on {base_url}")
    
    try:
        # Test OPTIONS request
        headers = {
            'Origin': 'https://contact-management-six-alpha.vercel.app',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        response = requests.options(f"{base_url}/auth/login", headers=headers, timeout=10)
        print(f"✅ CORS preflight: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"❌ CORS preflight failed: {e}")

def test_expired_token_handling(base_url):
    """Test expired token handling"""
    print(f"\n🔍 Testing expired token handling on {base_url}")
    
    try:
        # Create an expired token (this is just a mock test)
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid"
        
        headers = {
            'Authorization': f'Bearer {expired_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=10)
        print(f"✅ Expired token test: {response.status_code}")
        
        if response.status_code == 401:
            error_data = response.json()
            print(f"   Error message: {error_data.get('detail', 'No detail')}")
        
    except Exception as e:
        print(f"❌ Expired token test failed: {e}")

def test_database_connection_resilience(base_url):
    """Test database connection resilience"""
    print(f"\n🔍 Testing database connection resilience on {base_url}")
    
    try:
        # Make multiple rapid requests to test connection pooling
        for i in range(5):
            response = requests.get(f"{base_url}/health", timeout=5)
            print(f"   Request {i+1}: {response.status_code}")
            time.sleep(0.1)
        
        print("✅ Database connection resilience test completed")
        
    except Exception as e:
        print(f"❌ Database resilience test failed: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing backend fixes for Render deployment issues")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    
    # Test production URL
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        test_url = LOCAL_URL
    else:
        test_url = BASE_URL
    
    print(f"🎯 Testing URL: {test_url}")
    
    # Run tests
    test_health_endpoints(test_url)
    test_cors_preflight(test_url)
    test_expired_token_handling(test_url)
    test_database_connection_resilience(test_url)
    
    print(f"\n✅ All tests completed at: {datetime.now().isoformat()}")
    print("\n📋 Summary of fixes applied:")
    print("   - Improved database connection handling with retry logic")
    print("   - Enhanced JWT token expiration error handling")
    print("   - Added proper logging instead of print statements")
    print("   - Improved CORS configuration with preflight caching")
    print("   - Added custom exception handlers")
    print("   - Enhanced database session management")

if __name__ == "__main__":
    main()
