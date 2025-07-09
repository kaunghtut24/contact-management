#!/usr/bin/env python3
"""
Test script for Content Intelligence Service
"""
import asyncio
import os
import sys
import json

# Add the backend directory to the path
sys.path.append('/home/yuthar/contact-management-system/backend')

async def test_content_intelligence():
    """Test the Content Intelligence Service"""
    try:
        from app.services.content_intelligence import content_intelligence
        
        print("🧪 Testing Content Intelligence Service")
        print("=" * 50)
        
        # Test text with business card information
        test_text = """
        John Doe
        Senior Software Engineer
        Tech Solutions Inc.
        john.doe@techsolutions.com
        +1-555-123-4567
        www.techsolutions.com
        123 Tech Street
        Silicon Valley, CA 94000
        """
        
        print(f"📝 Test text: {test_text.strip()}")
        print("\n🔍 Analyzing content...")
        
        # Analyze the content
        result = await content_intelligence.analyze_content(test_text, "text")
        
        print(f"✅ Analysis completed!")
        print(f"📊 Success: {result['success']}")
        print(f"🎯 Confidence: {result['analysis']['confidence_score']:.2f}")
        print(f"🔧 Method: {result['analysis']['processing_method']}")
        print(f"📧 Contacts found: {len(result['contacts'])}")
        
        if result['contacts']:
            contact = result['contacts'][0]
            print(f"\n👤 First contact:")
            print(f"   Name: {contact.get('name', 'N/A')}")
            print(f"   Email: {contact.get('email', 'N/A')}")
            print(f"   Company: {contact.get('company', 'N/A')}")
            print(f"   Phone: {contact.get('phone', 'N/A')}")
            print(f"   Categories: {contact.get('categories', 'N/A')}")
        
        print(f"\n📋 Full result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_llm_providers():
    """Test available LLM providers"""
    try:
        from app.services.content_intelligence import content_intelligence
        
        print("\n🤖 Testing LLM Providers")
        print("=" * 30)
        
        providers = content_intelligence.llm_clients
        print(f"📊 Available providers: {list(providers.keys())}")
        print(f"🎯 Default provider: {content_intelligence.default_provider}")
        
        for name, config in providers.items():
            print(f"   {name}: {config['model']} ({config['type']})")
        
        return len(providers) > 0
        
    except Exception as e:
        print(f"❌ LLM provider test failed: {e}")
        return False

def test_spacy():
    """Test SpaCy model"""
    try:
        from app.services.content_intelligence import content_intelligence
        
        print("\n🧠 Testing SpaCy Model")
        print("=" * 25)
        
        if content_intelligence.spacy_model:
            print(f"✅ SpaCy model loaded: {content_intelligence.spacy_model.meta.get('name', 'unknown')}")
            
            # Test entity extraction
            test_text = "John Doe works at Microsoft in Seattle. Email: john@microsoft.com"
            spacy_result = content_intelligence._extract_with_spacy(test_text)
            
            print(f"📊 Entities found: {len(spacy_result.get('entities', {}))}")
            for entity_type, entities in spacy_result.get('entities', {}).items():
                if entities:
                    print(f"   {entity_type}: {[e['text'] for e in entities]}")
            
            return True
        else:
            print("⚠️ SpaCy model not loaded")
            return False
            
    except Exception as e:
        print(f"❌ SpaCy test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Content Intelligence Service Test Suite")
    print("=" * 60)
    
    # Check environment
    print("🔍 Environment Check:")
    print(f"   OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"   GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Not set'}")
    print(f"   SPACY_MODEL: {os.getenv('SPACY_MODEL', 'en_core_web_sm')}")
    
    # Run tests
    tests = [
        ("SpaCy Model", test_spacy),
        ("LLM Providers", test_llm_providers),
        ("Content Intelligence", test_content_intelligence),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Content Intelligence Service is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the configuration and try again.")

if __name__ == "__main__":
    asyncio.run(main())
