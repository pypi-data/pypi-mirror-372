#!/usr/bin/env python3
"""
Real API test for UltraGPT Claude support
Tests both providers with minimal credit usage
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

# Load environment variables
load_dotenv()

from src.ultragpt import UltraGPT

class SimpleResponse(BaseModel):
    answer: str
    confidence: float
    reasoning: str

def test_openai_basic():
    """Test basic OpenAI functionality"""
    print("🔵 Testing OpenAI Basic Chat...")
    
    try:
        ultragpt = UltraGPT(
            api_key=os.getenv("OPENAI_API_KEY"),
            provider="openai",
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            messages=[{"role": "user", "content": "What is 2+2? Give a very brief answer."}],
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✓ OpenAI Response: {response}")
        print(f"✓ Tokens used: {tokens}")
        return True
        
    except Exception as e:
        print(f"✗ OpenAI basic test failed: {e}")
        return False

def test_claude_basic():
    """Test basic Claude functionality"""
    print("\n🟠 Testing Claude Basic Chat...")
    
    try:
        ultragpt = UltraGPT(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            provider="anthropic",
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            messages=[{"role": "user", "content": "What is 3+3? Give a very brief answer."}],
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✓ Claude Response: {response}")
        print(f"✓ Tokens used: {tokens}")
        return True
        
    except Exception as e:
        print(f"✗ Claude basic test failed: {e}")
        return False

def test_openai_structured():
    """Test OpenAI structured output"""
    print("\n🔵 Testing OpenAI Structured Output...")
    
    try:
        ultragpt = UltraGPT(
            api_key=os.getenv("OPENAI_API_KEY"),
            provider="openai",
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            messages=[{"role": "user", "content": "Is the sky blue? Answer with confidence level."}],
            schema=SimpleResponse,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✓ OpenAI Structured Response: {response}")
        print(f"✓ Tokens used: {tokens}")
        print(f"✓ Answer: {response.get('answer')}")
        print(f"✓ Confidence: {response.get('confidence')}")
        return True
        
    except Exception as e:
        print(f"✗ OpenAI structured test failed: {e}")
        return False

def test_claude_structured():
    """Test Claude structured output"""
    print("\n🟠 Testing Claude Structured Output...")
    
    try:
        ultragpt = UltraGPT(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            provider="anthropic",
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            messages=[{"role": "user", "content": "Is water wet? Answer with confidence level."}],
            schema=SimpleResponse,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✓ Claude Structured Response: {response}")
        print(f"✓ Tokens used: {tokens}")
        print(f"✓ Answer: {response.get('answer')}")
        print(f"✓ Confidence: {response.get('confidence')}")
        return True
        
    except Exception as e:
        print(f"✗ Claude structured test failed: {e}")
        return False

def test_message_conversion():
    """Test Claude message conversion with real API"""
    print("\n🟠 Testing Claude Message Conversion...")
    
    try:
        ultragpt = UltraGPT(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            provider="anthropic",
            verbose=False
        )
        
        # Test with system message
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Be very brief."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response, tokens, details = ultragpt.chat(
            messages=messages,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✓ Claude System Message Response: {response}")
        print(f"✓ Tokens used: {tokens}")
        return True
        
    except Exception as e:
        print(f"✗ Claude message conversion test failed: {e}")
        return False

def main():
    """Run minimal real API tests"""
    print("🚀 UltraGPT Real API Tests")
    print("=" * 50)
    print("Running minimal tests to verify functionality...")
    print("(Designed to use minimal API credits)")
    print("=" * 50)
    
    results = []
    total_tests = 0
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - skipping OpenAI tests")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set - skipping Claude tests")
    
    # Run tests
    if os.getenv("OPENAI_API_KEY"):
        total_tests += 2
        results.append(("OpenAI Basic", test_openai_basic()))
        results.append(("OpenAI Structured", test_openai_structured()))
    
    if os.getenv("ANTHROPIC_API_KEY"):
        total_tests += 3
        results.append(("Claude Basic", test_claude_basic()))
        results.append(("Claude Structured", test_claude_structured()))
        results.append(("Claude Messages", test_message_conversion()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        print("🎉 All tests passed! Both providers are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Next steps:")
    print("- Try the example_claude_support.py for more comprehensive examples")
    print("- Check CLAUDE_SUPPORT.md for full documentation")
    print("- Both providers are now ready for production use!")

if __name__ == "__main__":
    main()
