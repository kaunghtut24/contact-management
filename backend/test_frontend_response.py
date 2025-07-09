#!/usr/bin/env python3
"""
Test frontend response format compatibility
"""
import json

def test_response_format():
    """Test the response format that frontend expects"""
    
    # Simulate successful response
    success_response = {
        "message": "File uploaded and processed successfully!",
        "filename": "test.jpg",
        "contacts_created": 1,
        "errors": [],
        "total_errors": 0,
        "success": True,
        "processing_method": "ocr_microservice_direct"
    }
    
    # Simulate error response
    error_response = {
        "message": "File uploaded but database save failed",
        "filename": "test.jpg", 
        "contacts_created": 0,
        "errors": ["Database commit failed: connection error"],
        "total_errors": 1,
        "success": False
    }
    
    print("✅ Success Response Format:")
    print(json.dumps(success_response, indent=2))
    
    print("\n❌ Error Response Format:")
    print(json.dumps(error_response, indent=2))
    
    print("\n🔍 Frontend Compatibility Check:")
    print(f"   Has 'message': {'✅' if 'message' in success_response else '❌'}")
    print(f"   Has 'contacts_created': {'✅' if 'contacts_created' in success_response else '❌'}")
    print(f"   Has 'errors': {'✅' if 'errors' in success_response else '❌'}")
    print(f"   Has 'total_errors': {'✅' if 'total_errors' in success_response else '❌'}")
    print(f"   Has 'success' flag: {'✅' if 'success' in success_response else '❌'}")
    
    # Check if frontend can handle the response
    if success_response.get('total_errors', 0) == 0:
        print("✅ Frontend should show: Success message")
    else:
        print("⚠️ Frontend should show: Error message")
    
    return True

if __name__ == "__main__":
    test_response_format()
