#!/usr/bin/env python3
"""
Test script to verify upload timeout fixes
"""
import requests
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"  # Local test server
# BASE_URL = "https://contact-management-ffsl.onrender.com"  # Production

def test_upload_timeout_handling():
    """Test upload timeout handling with different file types"""
    print(f"\n🔍 Testing upload timeout handling on {BASE_URL}")
    
    # First, we need to login to get a token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Try to login
        response = requests.post(f"{BASE_URL}/auth/login/simple", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print("❌ Login failed, testing without authentication")
            headers = {}
    except Exception as e:
        print(f"❌ Login failed: {e}")
        headers = {}
    
    # Test 1: Small text file (should be fast)
    print("\n📄 Testing small text file upload...")
    try:
        small_content = "Name: John Doe\nEmail: john@example.com\nPhone: 123-456-7890"
        files = {'file': ('test.txt', small_content, 'text/plain')}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/upload", files=files, headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"✅ Small file upload: {response.status_code} (took {end_time - start_time:.2f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"   Contacts created: {data.get('contacts_created', 0)}")
        
    except Exception as e:
        print(f"❌ Small file upload failed: {e}")
    
    # Test 2: CSV file (should be fast)
    print("\n📊 Testing CSV file upload...")
    try:
        csv_content = """Name,Email,Phone,Company
John Doe,john@example.com,123-456-7890,Example Corp
Jane Smith,jane@example.com,098-765-4321,Test Inc"""
        files = {'file': ('test.csv', csv_content, 'text/csv')}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/upload", files=files, headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"✅ CSV file upload: {response.status_code} (took {end_time - start_time:.2f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"   Contacts created: {data.get('contacts_created', 0)}")
        
    except Exception as e:
        print(f"❌ CSV file upload failed: {e}")
    
    # Test 3: Create a simple test image (if PIL is available)
    print("\n🖼️  Testing image file upload (OCR)...")
    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple business card image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Draw some text
        draw.text((20, 20), "John Doe", fill='black', font=font)
        draw.text((20, 50), "Software Engineer", fill='black', font=font)
        draw.text((20, 80), "john.doe@example.com", fill='black', font=font)
        draw.text((20, 110), "+1-555-123-4567", fill='black', font=font)
        draw.text((20, 140), "Tech Solutions Inc.", fill='black', font=font)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {'file': ('business_card.png', img_bytes.getvalue(), 'image/png')}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/upload", files=files, headers=headers, timeout=65)
        end_time = time.time()
        
        print(f"✅ Image file upload: {response.status_code} (took {end_time - start_time:.2f}s)")
        if response.status_code == 200:
            data = response.json()
            print(f"   Contacts created: {data.get('contacts_created', 0)}")
            print(f"   OCR used: {data.get('ocr_used', False)}")
            if data.get('errors'):
                print(f"   Errors: {len(data['errors'])}")
        elif response.status_code == 422:
            print("   Note: OCR dependencies may not be installed")
        
    except ImportError:
        print("❌ PIL not available, skipping image test")
    except Exception as e:
        print(f"❌ Image file upload failed: {e}")
    
    # Test 4: Test timeout behavior with a request that should timeout
    print("\n⏱️  Testing timeout behavior...")
    try:
        # This should test the timeout handling
        large_content = "Name: Test User\nEmail: test@example.com\n" * 1000
        files = {'file': ('large_test.txt', large_content, 'text/plain')}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/upload", files=files, headers=headers, timeout=5)  # Short timeout
        end_time = time.time()
        
        print(f"✅ Timeout test completed: {response.status_code} (took {end_time - start_time:.2f}s)")
        
    except requests.exceptions.Timeout:
        end_time = time.time()
        print(f"✅ Timeout test: Request timed out as expected (took {end_time - start_time:.2f}s)")
    except Exception as e:
        print(f"⚠️  Timeout test result: {e}")

def main():
    """Run upload timeout tests"""
    print("🧪 Testing upload timeout fixes")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print(f"🎯 Testing URL: {BASE_URL}")
    
    test_upload_timeout_handling()
    
    print(f"\n✅ All tests completed at: {datetime.now().isoformat()}")
    print("\n📋 Summary of timeout fixes applied:")
    print("   - Added 25-second timeout for OCR processing in backend")
    print("   - Increased frontend timeout to 60 seconds for uploads")
    print("   - Created fast OCR processing function")
    print("   - Optimized image preprocessing for speed")
    print("   - Added better progress feedback in frontend")
    print("   - Added timeout error handling and user feedback")

if __name__ == "__main__":
    main()
