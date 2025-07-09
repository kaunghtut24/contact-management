#!/usr/bin/env python3
"""
Test script for OCR Microservice
"""
import requests
import time
import io
from PIL import Image, ImageDraw, ImageFont

def create_test_business_card():
    """Create a test business card image"""
    # Create image
    img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw business card content
    draw.text((50, 50), "John Doe", fill='black', font=font_large)
    draw.text((50, 90), "Senior Software Engineer", fill='black', font=font_medium)
    draw.text((50, 130), "Tech Solutions Inc.", fill='black', font=font_medium)
    draw.text((50, 180), "john.doe@techsolutions.com", fill='blue', font=font_small)
    draw.text((50, 210), "+1-555-123-4567", fill='black', font=font_small)
    draw.text((50, 240), "www.techsolutions.com", fill='blue', font=font_small)
    draw.text((50, 280), "123 Tech Street", fill='black', font=font_small)
    draw.text((50, 300), "Silicon Valley, CA 94000", fill='black', font=font_small)
    
    # Add a border
    draw.rectangle([(10, 10), (590, 390)], outline='black', width=2)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_health_check(base_url):
    """Test health check endpoints"""
    print(f"\n🔍 Testing health endpoints on {base_url}")
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   OCR Available: {data.get('capabilities', {}).get('ocr_available')}")
            print(f"   LLM Available: {data.get('capabilities', {}).get('llm_available')}")
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"✅ Health endpoint: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def test_sync_processing(base_url):
    """Test synchronous processing"""
    print(f"\n📄 Testing sync processing on {base_url}")
    
    try:
        # Create test image
        img_data = create_test_business_card()
        files = {'file': ('business_card.png', img_data, 'image/png')}
        
        print(f"   Created test image: {len(img_data)} bytes")
        
        # Send to sync endpoint
        start_time = time.time()
        response = requests.post(f"{base_url}/process-sync", files=files, timeout=35)
        end_time = time.time()
        
        print(f"✅ Sync processing: {response.status_code} (took {end_time - start_time:.1f}s)")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('success'):
                ocr_result = data.get('ocr_result', {})
                contacts = data.get('contacts', [])
                print(f"   OCR Strategy: {ocr_result.get('strategy_used')}")
                print(f"   Text Length: {len(ocr_result.get('text', ''))}")
                print(f"   Contacts Found: {len(contacts)}")
                
                if contacts:
                    contact = contacts[0]
                    print(f"   First Contact: {contact.get('name')} - {contact.get('email')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Sync processing failed: {e}")

def test_async_processing(base_url):
    """Test asynchronous processing"""
    print(f"\n⏳ Testing async processing on {base_url}")
    
    try:
        # Create test image
        img_data = create_test_business_card()
        files = {'file': ('business_card_large.png', img_data, 'image/png')}
        
        # Start async processing
        start_time = time.time()
        response = requests.post(f"{base_url}/process-async", files=files, timeout=15)
        
        if response.status_code == 200:
            job_info = response.json()
            job_id = job_info["job_id"]
            print(f"✅ Async job started: {job_id}")
            
            # Poll for completion
            max_wait = 30
            poll_interval = 2
            waited = 0
            
            while waited < max_wait:
                time.sleep(poll_interval)
                waited += poll_interval
                
                status_response = requests.get(f"{base_url}/status/{job_id}", timeout=5)
                
                if status_response.status_code == 200:
                    job_status = status_response.json()
                    status = job_status["status"]
                    print(f"   Status after {waited}s: {status}")
                    
                    if status == "completed":
                        end_time = time.time()
                        result = job_status["result"]
                        contacts = result.get("contacts", [])
                        
                        print(f"✅ Async processing completed (took {end_time - start_time:.1f}s)")
                        print(f"   Contacts Found: {len(contacts)}")
                        
                        if contacts:
                            contact = contacts[0]
                            print(f"   First Contact: {contact.get('name')} - {contact.get('email')}")
                        break
                        
                    elif status == "failed":
                        print(f"❌ Async processing failed: {job_status.get('error')}")
                        break
            
            if waited >= max_wait:
                print(f"⏰ Async processing timed out after {max_wait}s")
        else:
            print(f"❌ Async job creation failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Async processing failed: {e}")

def main():
    """Run all tests"""
    import sys
    
    # Default to localhost, but allow override
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8002"
    
    print("🧪 Testing OCR Microservice")
    print(f"🎯 Target URL: {base_url}")
    print("=" * 60)
    
    test_health_check(base_url)
    test_sync_processing(base_url)
    test_async_processing(base_url)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n💡 Usage examples:")
    print(f"   python test_service.py {base_url}")
    print("   python test_service.py https://your-ocr-service.onrender.com")
    print("   python test_service.py https://your-ocr-service.vercel.app")

if __name__ == "__main__":
    main()
