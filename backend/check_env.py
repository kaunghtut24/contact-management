#!/usr/bin/env python3
"""
Check environment variables for LLM configuration
"""
import os

def check_environment():
    """Check all relevant environment variables"""
    print("🔍 Environment Variable Check")
    print("=" * 40)
    
    # LLM API Keys
    env_vars = [
        ("OPENAI_API_KEY", "OpenAI API Key"),
        ("GROQ_API_KEY", "Groq API Key"),
        ("ANTHROPIC_API_KEY", "Anthropic API Key"),
        ("OPENAI_MODEL", "OpenAI Model"),
        ("GROQ_MODEL", "Groq Model"),
        ("OPENAI_BASE_URL", "OpenAI Base URL"),
        ("DATABASE_URL", "Database URL"),
        ("ENVIRONMENT", "Environment"),
    ]
    
    found_keys = 0
    
    for var_name, description in env_vars:
        value = os.getenv(var_name)
        if value:
            if "API_KEY" in var_name:
                # Mask API keys for security
                masked_value = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
                print(f"✅ {description}: {masked_value}")
                found_keys += 1
            else:
                print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: Not set")
    
    print(f"\n📊 Summary: {found_keys} API keys found")
    
    # Check if any LLM provider is available
    if found_keys > 0:
        print("✅ LLM providers available")
    else:
        print("⚠️ No LLM providers configured - using SpaCy fallback only")
    
    # Check specific Groq configuration
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"\n🤖 Groq Configuration:")
        print(f"   Key format: {'✅ Valid' if groq_key.startswith('gsk_') else '❌ Invalid'}")
        print(f"   Key length: {len(groq_key)} characters")
        print(f"   Model: {os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')}")
    
    return found_keys > 0

if __name__ == "__main__":
    check_environment()
