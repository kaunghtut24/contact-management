#!/usr/bin/env python3
"""
Test script to verify large image upload timeout fixes
"""
import requests
import time
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration
BASE_URL = "http://localhost:8001"  # Local test server

def create_test_image(size_mb=2.0, text_content=None):
    """Create a test image of specified size with business card content"""
    if text_content is None:
        text_content = [
            "John Doe",
            "Senior Software Engineer",
            "Tech Solutions Inc.",
            "john.doe@techsolutions.com",
            "+1-555-123-4567",
            "www.techsolutions.com",
            "123 Tech Street, Silicon Valley, CA 94000"
        ]
    
    # Calculate dimensions for target file size
    # Rough estimate: 1MB ≈ 1000x1000 pixels for PNG
    target_pixels = int(size_mb * 1000000)  # Rough approximation
    width = int((target_pixels * 1.5) ** 0.5)  # 3:2 aspect ratio
    height = int(width / 1.5)
    
    print(f"Creating {width}x{height} test image targeting {size_mb}MB...")
    
    # Create image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font_size = max(20, width // 40)  # Scale font with image size
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Draw business card content
    y_offset = height // 10
    line_height = height // 15
    
    for i, line in enumerate(text_content):
        y_pos = y_offset + (i * line_height)
        draw.text((width // 20, y_pos), line, fill='black', font=font)
    
    # Add some visual elements to increase file size
    for i in range(0, width, 50):
        draw.line([(i, height-10), (i+20, height-10)], fill='lightgray', width=2)
    
    # Save to bytes and check size
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', optimize=False)
    actual_size_mb = len(img_bytes.getvalue()) / (1024 * 1024)
    
    print(f"Created image: {width}x{height}, actual size: {actual_size_mb:.1f}MB")
    
    img_bytes.seek(0)
    return img_bytes.getvalue(), actual_size_mb

def test_large_image_upload():
    """Test large image upload with timeout handling"""
    print(f"\n🔍 Testing large image upload on {BASE_URL}")
    
    # First, create admin user and login
    try:
        # Create admin
        response = requests.post(f"{BASE_URL}/auth/create-admin", timeout=10)
        print(f"Admin creation: {response.status_code}")
        
        # Login
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/auth/login/simple", json=login_data, timeout=10)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print("❌ Login failed, testing without authentication")
            headers = {}
    except Exception as e:
        print(f"❌ Login setup failed: {e}")
        headers = {}
    
    # Test different image sizes
    test_sizes = [0.5, 1.0, 1.5, 2.0]  # MB
    
    for size_mb in test_sizes:
        print(f"\n📸 Testing {size_mb}MB image upload...")
        
        try:
            # Create test image
            img_data, actual_size = create_test_image(size_mb)
            
            # Upload image
            files = {'file': (f'test_{size_mb}mb.png', img_data, 'image/png')}
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/upload", 
                files=files, 
                headers=headers, 
                timeout=70  # Give extra time for large files
            )
            end_time = time.time()
            
            duration = end_time - start_time
            
            print(f"✅ {actual_size:.1f}MB image upload: {response.status_code} (took {duration:.1f}s)")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Contacts created: {data.get('contacts_created', 0)}")
                print(f"   OCR used: {data.get('ocr_used', False)}")
                if data.get('errors'):
                    print(f"   Errors: {len(data['errors'])}")
                    for error in data['errors'][:2]:  # Show first 2 errors
                        print(f"     - {error}")
            else:
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"❌ {size_mb}MB image upload timed out")
        except Exception as e:
            print(f"❌ {size_mb}MB image upload failed: {e}")

def test_timeout_behavior():
    """Test timeout behavior with different scenarios"""
    print(f"\n⏱️  Testing timeout behavior...")
    
    # Test with a very large image that should timeout
    try:
        print("Creating 3MB image (should be rejected by frontend validation)...")
        img_data, actual_size = create_test_image(3.0)
        print(f"Created {actual_size:.1f}MB image for timeout test")
        
        # This should be rejected by our validation
        files = {'file': ('large_test.png', img_data, 'image/png')}
        
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/upload", files=files, timeout=10)
        end_time = time.time()
        
        print(f"Large image response: {response.status_code} (took {end_time - start_time:.1f}s)")
        if response.status_code != 200:
            print(f"   Error (expected): {response.text[:200]}...")
        
    except Exception as e:
        print(f"Large image test result: {e}")

def main():
    """Run large image upload tests"""
    print("🧪 Testing large image upload timeout fixes")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print(f"🎯 Testing URL: {BASE_URL}")
    
    test_large_image_upload()
    test_timeout_behavior()
    
    print(f"\n✅ All tests completed at: {datetime.now().isoformat()}")
    print("\n📋 Summary of large image fixes applied:")
    print("   - Dynamic timeout scaling based on file size:")
    print("     * < 1MB: 20s OCR timeout, 30s overall")
    print("     * 1-1.5MB: 25s OCR timeout, 35s overall")
    print("     * > 1.5MB: 35s OCR timeout, 45s overall")
    print("   - Optimized image preprocessing for large files")
    print("   - Frontend validation rejects images > 2MB")
    print("   - Better user feedback with file size information")
    print("   - Frontend timeout increased to 60s")

if __name__ == "__main__":
    main()
