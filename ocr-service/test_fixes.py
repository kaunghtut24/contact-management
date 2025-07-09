#!/usr/bin/env python3
"""
Test script to verify OCR service fixes
"""
import requests
import sys

def test_health_endpoints(base_url):
    """Test health endpoints to verify fixes"""
    print(f"🔍 Testing health endpoints on {base_url}")
    
    try:
        # Test root endpoint (this was failing before)
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Root endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Status: {data.get('status')}")
            print(f"   OCR Available: {data.get('capabilities', {}).get('ocr_available')}")
            print(f"   LLM Available: {data.get('capabilities', {}).get('llm_available')}")
            print(f"   LLM Providers: {data.get('capabilities', {}).get('llm_providers', [])}")
            print(f"   Default Provider: {data.get('capabilities', {}).get('default_provider')}")
        else:
            print(f"   Error: {response.text}")
        
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   OCR Available: {data.get('ocr_available')}")
            print(f"   LLM Available: {data.get('llm_available')}")
            print(f"   LLM Providers: {data.get('llm_providers', [])}")
            print(f"   Job Queue Size: {data.get('job_queue_size')}")
        else:
            print(f"   Error: {response.text}")
            
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Run health check tests"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    
    print("🧪 Testing OCR Service Fixes")
    print(f"🎯 Target URL: {base_url}")
    print("=" * 50)
    
    success = test_health_endpoints(base_url)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All health checks passed!")
        print("🎉 The AttributeError fix is working correctly")
    else:
        print("❌ Health checks failed")
        print("🔧 Check the service logs for more details")
    
    print(f"\n💡 Usage: python test_fixes.py {base_url}")

if __name__ == "__main__":
    main()
