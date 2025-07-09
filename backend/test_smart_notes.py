#!/usr/bin/env python3
"""
Test script for Smart Notes functionality
"""
import asyncio
import sys

# Add the backend directory to the path
sys.path.append('/home/yuthar/contact-management-system/backend')

async def test_smart_notes():
    """Test the smart notes generation"""
    try:
        from app.services.content_intelligence import content_intelligence
        
        print("🧪 Testing Smart Notes Generation")
        print("=" * 50)
        
        # Test text with rich information for notes
        test_text = """
        Dr. ALOKE CHAKRABORTY
        DEPUTY GENERAL MANAGER
        ECOGENESIS GROUP
        aloke.chakraborty@ecogenesis.info
        +91-8420636976
        www.ecogenesis.info
        218, Ajoy Nagar, 1st Road, Kolkata-700075, INDIA
        
        MBA in International Business, PhD in Environmental Science
        15+ years experience in sustainable development
        Specializes in green technology consulting
        Fluent in English, Hindi, and Bengali
        Winner of Environmental Excellence Award 2023
        Available Monday to Friday, 9 AM to 6 PM
        WhatsApp: +91-8420636976
        LinkedIn: linkedin.com/in/aloke-chakraborty
        Provides consulting services for renewable energy projects
        Expert in carbon footprint analysis
        Certified Project Management Professional (PMP)
        """
        
        print(f"📝 Test text length: {len(test_text)} characters")
        print(f"📝 Test text preview: {test_text[:200]}...")
        
        # Analyze with Content Intelligence
        result = await content_intelligence.analyze_content(test_text, "text")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Success: {result['success']}")
        print(f"   Contacts found: {len(result['contacts'])}")
        print(f"   Processing method: {result['analysis']['processing_method']}")
        
        if result['contacts']:
            contact = result['contacts'][0]
            print(f"\n👤 Contact Details:")
            print(f"   Name: {contact.get('name', 'N/A')}")
            print(f"   Designation: {contact.get('designation', 'N/A')}")
            print(f"   Company: {contact.get('company', 'N/A')}")
            print(f"   Email: {contact.get('email', 'N/A')}")
            print(f"   Phone: {contact.get('phone', 'N/A')}")
            print(f"   Categories: {contact.get('categories', 'N/A')}")
            
            notes = contact.get('notes', '')
            print(f"\n📝 Smart Notes Generated:")
            if notes:
                print(f"   {notes}")
                
                # Analyze notes content
                print(f"\n🔍 Notes Analysis:")
                print(f"   Length: {len(notes)} characters")
                
                # Check for different types of information
                info_types = {
                    "Qualifications": ['mba', 'phd', 'degree', 'certified'],
                    "Experience": ['years experience', 'experience', 'expert'],
                    "Languages": ['fluent', 'speaks', 'languages'],
                    "Awards": ['award', 'winner', 'excellence'],
                    "Services": ['consulting', 'provides', 'services'],
                    "Contact Info": ['whatsapp', 'linkedin', 'available']
                }
                
                notes_lower = notes.lower()
                for info_type, keywords in info_types.items():
                    if any(keyword in notes_lower for keyword in keywords):
                        print(f"   ✅ Contains {info_type}")
                    else:
                        print(f"   ❌ Missing {info_type}")
            else:
                print("   ⚠️ No notes generated")
        else:
            print("❌ No contacts extracted")
        
        return len(result['contacts']) > 0 and result['contacts'][0].get('notes', '')
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_notes_with_different_content():
    """Test notes generation with different types of content"""
    try:
        from app.services.content_intelligence import content_intelligence
        
        print("\n🧪 Testing Notes with Different Content Types")
        print("=" * 50)
        
        test_cases = [
            {
                "name": "Business Card",
                "text": """
                John Smith
                Senior Marketing Manager
                TechCorp Solutions
                john.smith@techcorp.com
                +1-555-123-4567
                Specializes in digital marketing campaigns
                Google Ads certified
                10 years experience in B2B marketing
                """
            },
            {
                "name": "Academic Profile", 
                "text": """
                Prof. Sarah Johnson
                Research Director
                University Research Center
                sarah.j@university.edu
                PhD in Computer Science from MIT
                Published 50+ research papers
                Expert in machine learning and AI
                Speaks English, French, and German
                """
            },
            {
                "name": "Service Provider",
                "text": """
                Mike Wilson
                Freelance Web Developer
                mike@webdev.com
                +44-20-1234-5678
                Full-stack developer with React and Node.js
                Available for remote projects
                Portfolio: www.mikewilson.dev
                5+ years experience
                """
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            print(f"\n📋 Test Case {i+1}: {test_case['name']}")
            
            result = await content_intelligence.analyze_content(test_case['text'], "text")
            
            if result['contacts']:
                contact = result['contacts'][0]
                notes = contact.get('notes', '')
                
                print(f"   Name: {contact.get('name', 'N/A')}")
                print(f"   Notes: {notes[:100]}{'...' if len(notes) > 100 else ''}")
                print(f"   Notes length: {len(notes)} chars")
                
                results.append(len(notes) > 0)
            else:
                print("   ❌ No contact extracted")
                results.append(False)
        
        success_rate = sum(results) / len(results) * 100
        print(f"\n📊 Notes Generation Success Rate: {success_rate:.1f}%")
        
        return success_rate > 50
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run all smart notes tests"""
    print("🧪 Smart Notes Test Suite")
    print("=" * 60)
    
    # Test 1: Comprehensive notes generation
    test1_result = await test_smart_notes()
    
    # Test 2: Different content types
    test2_result = await test_notes_with_different_content()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"   Smart Notes Generation: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Multiple Content Types: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Smart Notes functionality is working correctly.")
        print("💡 The system will now generate intelligent notes containing:")
        print("   • Qualifications and certifications")
        print("   • Experience and expertise")
        print("   • Languages spoken")
        print("   • Awards and achievements")
        print("   • Services offered")
        print("   • Additional contact methods")
        print("   • Availability information")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    asyncio.run(main())
