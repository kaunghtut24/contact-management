#!/usr/bin/env python3
"""
Debug script for LLM issues
"""
import asyncio
import os
import sys
import json

# Add the backend directory to the path
sys.path.append('/home/yuthar/contact-management-system/backend')

async def test_llm_directly():
    """Test LLM directly to debug the empty response issue"""
    try:
        print("🔍 Testing LLM directly...")
        
        # Check environment variables
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        print(f"🔑 GROQ_API_KEY present: {bool(groq_key)}")
        print(f"🔑 OPENAI_API_KEY present: {bool(openai_key)}")
        
        if not groq_key and not openai_key:
            print("❌ No API keys found in environment")
            return False
        
        # Test with simple prompt
        simple_text = """
        John Doe
        Senior Software Engineer
        Tech Solutions Inc.
        john.doe@techsolutions.com
        +1-555-123-4567
        """
        
        # Try Groq if available
        if groq_key:
            print("\n🤖 Testing Groq API...")
            try:
                import openai
                
                client = openai.OpenAI(
                    api_key=groq_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                
                prompt = f"""Extract contact information and return ONLY valid JSON array.

TEXT:
{simple_text}

Return JSON like: [{{"name":"John Doe","designation":"Engineer","company":"ABC","email":"john@abc.com","phone":"+123","website":"","address":"","categories":["Others"]}}]

JSON:"""
                
                print(f"📝 Sending prompt (length: {len(prompt)})")
                
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model="mixtral-8x7b-32768",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                
                result = response.choices[0].message.content
                print(f"📥 Response length: {len(result) if result else 0}")
                print(f"📥 Response content: {repr(result)}")
                
                if result and result.strip():
                    try:
                        contacts = json.loads(result.strip())
                        print(f"✅ JSON parsing successful: {len(contacts)} contacts")
                        print(f"📊 First contact: {contacts[0] if contacts else 'None'}")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing failed: {e}")
                        print(f"🔍 Trying to extract JSON from: {result}")
                        return False
                else:
                    print("❌ Empty response from Groq")
                    return False
                    
            except Exception as e:
                print(f"❌ Groq test failed: {e}")
                return False
        
        # Try OpenAI if available
        if openai_key:
            print("\n🤖 Testing OpenAI API...")
            try:
                import openai
                
                client = openai.OpenAI(api_key=openai_key)
                
                prompt = f"""Extract contact information and return ONLY valid JSON array.

TEXT:
{simple_text}

Return JSON like: [{{"name":"John Doe","designation":"Engineer","company":"ABC","email":"john@abc.com","phone":"+123","website":"","address":"","categories":["Others"]}}]

JSON:"""
                
                response = await asyncio.to_thread(
                    client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                
                result = response.choices[0].message.content
                print(f"📥 Response length: {len(result) if result else 0}")
                print(f"📥 Response content: {repr(result)}")
                
                if result and result.strip():
                    try:
                        contacts = json.loads(result.strip())
                        print(f"✅ JSON parsing successful: {len(contacts)} contacts")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing failed: {e}")
                        return False
                else:
                    print("❌ Empty response from OpenAI")
                    return False
                    
            except Exception as e:
                print(f"❌ OpenAI test failed: {e}")
                return False
        
        return False
        
    except Exception as e:
        print(f"❌ LLM test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_content_intelligence_with_llm():
    """Test Content Intelligence with LLM debugging"""
    try:
        from app.services.content_intelligence import content_intelligence
        
        print("\n🧠 Testing Content Intelligence with LLM debugging...")
        
        # Enable debug logging
        import logging
        logging.getLogger('app.services.content_intelligence').setLevel(logging.DEBUG)
        
        test_text = """
        John Doe
        Senior Software Engineer  
        Tech Solutions Inc.
        john.doe@techsolutions.com
        +1-555-123-4567
        www.techsolutions.com
        """
        
        result = await content_intelligence.analyze_content(test_text, "text")
        
        print(f"✅ Analysis completed!")
        print(f"📊 Success: {result['success']}")
        print(f"🎯 Method: {result['analysis']['processing_method']}")
        print(f"📧 Contacts: {len(result['contacts'])}")
        
        if result['contacts']:
            contact = result['contacts'][0]
            print(f"👤 Contact: {contact.get('name')} - {contact.get('email')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Content Intelligence test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run LLM debugging tests"""
    print("🔍 LLM Debugging Test Suite")
    print("=" * 50)
    
    # Test 1: Direct LLM API calls
    llm_result = await test_llm_directly()
    
    # Test 2: Content Intelligence with debugging
    ci_result = await test_content_intelligence_with_llm()
    
    print("\n" + "=" * 50)
    print("📋 Debug Results:")
    print(f"   Direct LLM API: {'✅ Working' if llm_result else '❌ Failed'}")
    print(f"   Content Intelligence: {'✅ Working' if ci_result else '❌ Failed'}")
    
    if not llm_result:
        print("\n💡 Recommendations:")
        print("   1. Check API key configuration in Render environment")
        print("   2. Verify API key has sufficient credits/quota")
        print("   3. Test API key directly with curl")
        print("   4. Check for rate limiting or API restrictions")

if __name__ == "__main__":
    asyncio.run(main())
