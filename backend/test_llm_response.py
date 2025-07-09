#!/usr/bin/env python3
"""
Test to reproduce the exact LLM response issue
"""
import asyncio
import os
import sys
import json

# Add the backend directory to the path
sys.path.append('/home/yuthar/contact-management-system/backend')

async def test_llm_with_exact_ocr_text():
    """Test LLM with the exact text that's causing issues"""
    try:
        print("🔍 Testing LLM with exact OCR text that's failing...")
        
        # This is the exact text from your OCR (293 characters)
        ocr_text = """John Doe
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
Contact for business inquiries"""
        
        print(f"📝 OCR text length: {len(ocr_text)} characters")
        print(f"📝 OCR text preview: {repr(ocr_text[:100])}...")
        
        # Test with OpenAI if key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print(f"\n🤖 Testing OpenAI API...")
            await test_openai_api(openai_key, ocr_text)
        else:
            print("❌ No OPENAI_API_KEY found")
        
        # Test with Groq if key is available
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            print(f"\n🤖 Testing Groq API...")
            await test_groq_api(groq_key, ocr_text)
        else:
            print("❌ No GROQ_API_KEY found")
        
        if not openai_key and not groq_key:
            print("\n💡 No API keys found. To test:")
            print("   export OPENAI_API_KEY=sk-your-key")
            print("   export GROQ_API_KEY=gsk-your-key")
            print("   python test_llm_response.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_openai_api(api_key, text):
    """Test OpenAI API specifically"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        
        # Use the exact same prompt as Content Intelligence
        prompt = f"""You are a contact extraction expert. Extract contact information from the text and return a valid JSON array.

REQUIREMENTS:
- Return ONLY a JSON array, nothing else
- Each contact must have: name, designation, company, email, phone, website, address, categories
- Use empty string "" for missing fields
- Categories must be from: ["Government", "Embassy", "Consulate", "High Commissioner", "Deputy High Commissioner", "Associations", "Exporter", "Importer", "Logistics", "Event management", "Consultancy", "Manufacturer", "Distributors", "Producers", "Others"]
- Categories field must be an array like ["Others"]

EXAMPLE:
[{{"name":"John Doe","designation":"Manager","company":"ABC Corp","email":"john@abc.com","phone":"+1234567890","website":"","address":"123 Main St","categories":["Others"]}}]

If no contacts found, return: []

TEXT TO ANALYZE:
{text}

RESPOND WITH JSON ARRAY:"""
        
        print(f"📤 Sending request to OpenAI...")
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        
        print(f"✅ OpenAI API call successful")
        print(f"🔍 Response object type: {type(response)}")
        print(f"🔍 Response choices: {len(response.choices) if response.choices else 0}")
        
        if response.choices:
            choice = response.choices[0]
            print(f"🔍 Choice finish_reason: {getattr(choice, 'finish_reason', 'unknown')}")
            print(f"🔍 Message role: {getattr(choice.message, 'role', 'unknown')}")
            
            content = choice.message.content
            print(f"🔍 Content type: {type(content)}")
            print(f"🔍 Content length: {len(content) if content else 0}")
            print(f"🔍 Content repr: {repr(content)}")
            
            if content:
                print(f"📝 Content preview: {content[:200]}...")
                
                # Try to parse as JSON
                try:
                    parsed = json.loads(content.strip())
                    print(f"✅ JSON parsing successful: {len(parsed)} contacts")
                    if parsed:
                        print(f"👤 First contact: {parsed[0]}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    print(f"🔍 Trying to find JSON in response...")
                    
                    # Try to extract JSON
                    import re
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        try:
                            extracted = json.loads(json_match.group())
                            print(f"✅ Extracted JSON successful: {len(extracted)} contacts")
                        except:
                            print(f"❌ Extracted JSON also failed")
            else:
                print(f"❌ OpenAI returned empty content")
        else:
            print(f"❌ OpenAI returned no choices")
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_groq_api(api_key, text):
    """Test Groq API specifically"""
    try:
        import openai
        
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Simple prompt for Groq
        prompt = f"""Extract contact info as JSON array:

{text}

Return: [{{"name":"","email":"","phone":"","company":"","categories":["Others"]}}]"""
        
        print(f"📤 Sending request to Groq...")
        print(f"📝 Prompt length: {len(prompt)} characters")
        
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.0
        )
        
        print(f"✅ Groq API call successful")
        print(f"🔍 Response object type: {type(response)}")
        print(f"🔍 Response choices: {len(response.choices) if response.choices else 0}")
        
        if response.choices:
            choice = response.choices[0]
            print(f"🔍 Choice finish_reason: {getattr(choice, 'finish_reason', 'unknown')}")
            
            content = choice.message.content
            print(f"🔍 Content type: {type(content)}")
            print(f"🔍 Content length: {len(content) if content else 0}")
            print(f"🔍 Content repr: {repr(content)}")
            
            if content:
                print(f"📝 Content preview: {content[:200]}...")
                
                # Try to parse as JSON
                try:
                    parsed = json.loads(content.strip())
                    print(f"✅ JSON parsing successful: {len(parsed)} contacts")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
            else:
                print(f"❌ Groq returned empty content")
        else:
            print(f"❌ Groq returned no choices")
            
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_with_exact_ocr_text())
