#!/usr/bin/env python3
"""
Specific test to debug and fix Groq LLM empty response issue
"""
import asyncio
import os
import sys
import json

# Add the backend directory to the path
sys.path.append('/home/yuthar/contact-management-system/backend')

async def test_groq_directly():
    """Test Groq API directly with the exact same text from OCR"""
    try:
        print("🔍 Testing Groq API directly with OCR text...")
        
        # Check if Groq API key is available
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            print("❌ GROQ_API_KEY not found in environment")
            return False
        
        print(f"✅ GROQ_API_KEY found: {groq_key[:10]}...")
        
        # Use the exact text that OCR extracted (293 characters)
        ocr_text = """
        John Doe
        Senior Software Engineer
        Tech Solutions Inc.
        john.doe@techsolutions.com
        +1-555-123-4567
        www.techsolutions.com
        123 Tech Street
        Silicon Valley, CA 94000
        Additional contact information
        Business card details
        Professional services
        """
        
        print(f"📝 Testing with OCR text ({len(ocr_text)} characters)")
        
        import openai
        
        client = openai.OpenAI(
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Test 1: Simple prompt
        print("\n🧪 Test 1: Simple prompt")
        simple_prompt = f"""Extract contact info as JSON:

{ocr_text}

Return: [{{"name":"","email":"","phone":"","company":"","categories":["Others"]}}]"""
        
        try:
            response1 = await asyncio.to_thread(
                client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": simple_prompt}],
                max_tokens=1000,
                temperature=0.0
            )
            
            result1 = response1.choices[0].message.content
            print(f"📥 Response 1 length: {len(result1) if result1 else 0}")
            print(f"📥 Response 1 content: {repr(result1)}")
            
            if result1 and result1.strip():
                try:
                    contacts1 = json.loads(result1.strip())
                    print(f"✅ Test 1 SUCCESS: {len(contacts1)} contacts parsed")
                except json.JSONDecodeError as e:
                    print(f"❌ Test 1 JSON parsing failed: {e}")
            else:
                print("❌ Test 1 FAILED: Empty response")
                
        except Exception as e:
            print(f"❌ Test 1 API call failed: {e}")
        
        # Test 2: Even simpler prompt
        print("\n🧪 Test 2: Ultra-simple prompt")
        ultra_simple = "Extract name and email from: John Doe john.doe@techsolutions.com"
        
        try:
            response2 = await asyncio.to_thread(
                client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": ultra_simple}],
                max_tokens=500,
                temperature=0.0
            )
            
            result2 = response2.choices[0].message.content
            print(f"📥 Response 2 length: {len(result2) if result2 else 0}")
            print(f"📥 Response 2 content: {repr(result2)}")
            
            if result2 and result2.strip():
                print(f"✅ Test 2 SUCCESS: Got response")
            else:
                print("❌ Test 2 FAILED: Empty response")
                
        except Exception as e:
            print(f"❌ Test 2 API call failed: {e}")
        
        # Test 3: Different model
        print("\n🧪 Test 3: Different Groq model")
        try:
            response3 = await asyncio.to_thread(
                client.chat.completions.create,
                model="llama3-8b-8192",  # Different model
                messages=[{"role": "user", "content": ultra_simple}],
                max_tokens=500,
                temperature=0.0
            )
            
            result3 = response3.choices[0].message.content
            print(f"📥 Response 3 length: {len(result3) if result3 else 0}")
            print(f"📥 Response 3 content: {repr(result3)}")
            
            if result3 and result3.strip():
                print(f"✅ Test 3 SUCCESS: Different model works")
                return True
            else:
                print("❌ Test 3 FAILED: Empty response with different model")
                
        except Exception as e:
            print(f"❌ Test 3 API call failed: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Groq test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_content_intelligence_with_debug():
    """Test Content Intelligence with enhanced debugging"""
    try:
        print("\n🧠 Testing Content Intelligence with Groq debugging...")
        
        from app.services.content_intelligence import content_intelligence
        
        # Enable debug logging
        import logging
        logging.getLogger('app.services.content_intelligence').setLevel(logging.DEBUG)
        
        # Use the same OCR text
        ocr_text = """
        John Doe
        Senior Software Engineer
        Tech Solutions Inc.
        john.doe@techsolutions.com
        +1-555-123-4567
        www.techsolutions.com
        123 Tech Street
        Silicon Valley, CA 94000
        """
        
        print(f"📝 Analyzing with Content Intelligence...")
        result = await content_intelligence.analyze_content(ocr_text, "image")
        
        print(f"📊 Analysis result:")
        print(f"   Success: {result['success']}")
        print(f"   Method: {result['analysis']['processing_method']}")
        print(f"   Contacts: {len(result['contacts'])}")
        
        if result['contacts']:
            contact = result['contacts'][0]
            print(f"👤 Contact: {contact.get('name')} - {contact.get('email')}")
        
        # Check LLM extraction specifically
        llm_result = result['analysis']['llm_extraction']
        print(f"🤖 LLM extraction:")
        print(f"   Method: {llm_result['method']}")
        print(f"   Contacts: {len(llm_result.get('contacts', []))}")
        if 'error' in llm_result:
            print(f"   Error: {llm_result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Content Intelligence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run Groq debugging tests"""
    print("🔍 Groq LLM Debugging Test Suite")
    print("=" * 60)
    
    # Test 1: Direct Groq API
    groq_result = await test_groq_directly()
    
    # Test 2: Content Intelligence with debugging
    ci_result = await test_content_intelligence_with_debug()
    
    print("\n" + "=" * 60)
    print("📋 Debug Results:")
    print(f"   Direct Groq API: {'✅ Working' if groq_result else '❌ Failed'}")
    print(f"   Content Intelligence: {'✅ Working' if ci_result else '❌ Failed'}")
    
    if not groq_result:
        print("\n💡 Groq API Issues Detected:")
        print("   1. API key may be invalid or expired")
        print("   2. Model may be unavailable or rate limited")
        print("   3. Prompt may be triggering content filters")
        print("   4. API response format may have changed")
        print("\n🔧 Recommended Actions:")
        print("   1. Verify API key at console.groq.com")
        print("   2. Try different model (llama3-8b-8192)")
        print("   3. Simplify prompts to avoid filters")
        print("   4. Add retry logic with exponential backoff")

if __name__ == "__main__":
    asyncio.run(main())
