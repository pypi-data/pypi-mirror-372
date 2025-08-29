"""
Basic test for UltraGPT multi-provider support
Tests basic chat and structured output functionality
Designed to use minimal tokens for cost-effective testing
"""

import os
import sys
sys.path.append('src')

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded environment variables from .env file")
except ImportError:
    print("⚠ python-dotenv not installed. Install with: pip install python-dotenv")
    print("  Or manually set environment variables")

from ultragpt import UltraGPT
from pydantic import BaseModel, Field
from typing import List, Optional

# Simple schemas for testing structured output
class SimpleResponse(BaseModel):
    answer: str = Field(description="A simple one-word answer")
    confidence: float = Field(description="Confidence level between 0 and 1", ge=0, le=1)

class MathResponse(BaseModel):
    result: int = Field(description="The result of the calculation")
    operation: str = Field(description="The operation performed (add, subtract, multiply, divide)")

def test_basic_initialization():
    """Test UltraGPT initialization with different provider configurations"""
    print("=" * 60)
    print("TESTING INITIALIZATION")
    print("=" * 60)
    
    # Test 1: OpenAI only
    try:
        if os.getenv("OPENAI_API_KEY"):
            ultra_openai = UltraGPT(
                api_key=os.getenv("OPENAI_API_KEY"),
                verbose=False
            )
            print("✓ OpenAI-only initialization successful")
            print(f"  Available providers: {list(ultra_openai.provider_manager.providers.keys())}")
        else:
            print("⚠ Skipping OpenAI test - no API key provided")
    except Exception as e:
        print(f"✗ OpenAI initialization failed: {e}")
    
    # Test 2: Multi-provider
    try:
        providers = {}
        if os.getenv("OPENAI_API_KEY"):
            providers["openai"] = True
        if os.getenv("ANTHROPIC_API_KEY"):
            providers["claude"] = True
            
        if providers:
            ultra_multi = UltraGPT(
                api_key=os.getenv("OPENAI_API_KEY"),
                claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
                verbose=False
            )
            print("✓ Multi-provider initialization successful")
            print(f"  Available providers: {list(ultra_multi.provider_manager.providers.keys())}")
            return ultra_multi
        else:
            print("⚠ Skipping multi-provider test - no API keys provided")
            return None
    except Exception as e:
        print(f"✗ Multi-provider initialization failed: {e}")
        return None

def test_basic_chat(ultra):
    """Test basic chat functionality with different providers"""
    if not ultra:
        print("⚠ Skipping basic chat tests - no UltraGPT instance")
        return
        
    print("\n" + "=" * 60)
    print("TESTING BASIC CHAT")
    print("=" * 60)
    
    # Simple test message to minimize token usage
    test_messages = [{"role": "user", "content": "Say 'hello' in one word"}]
    
    # Test with available providers
    available_providers = list(ultra.provider_manager.providers.keys())
    
    for provider in available_providers:
        try:
            print(f"\nTesting {provider.upper()} provider...")
            
            # Test with explicit provider
            if provider == "openai":
                model = "gpt-4o-mini"  # Use cheaper model
            else:
                model = f"{provider}:claude-3-haiku-20240307"  # Use fastest Claude model
            
            response, tokens, details = ultra.chat(
                messages=test_messages,
                model=model,
                steps_pipeline=False,  # Disable to save tokens
                reasoning_pipeline=False,  # Disable to save tokens
                tools=[]  # Disable tools to save tokens
            )
            
            print(f"✓ {provider.upper()} chat successful")
            print(f"  Model: {model}")
            print(f"  Response: {response[:50]}..." if len(response) > 50 else f"  Response: {response}")
            print(f"  Tokens used: {tokens}")
            
        except Exception as e:
            print(f"✗ {provider.upper()} chat failed: {e}")

def test_structured_output(ultra):
    """Test structured output with different providers"""
    if not ultra:
        print("⚠ Skipping structured output tests - no UltraGPT instance")
        return
        
    print("\n" + "=" * 60)
    print("TESTING STRUCTURED OUTPUT")
    print("=" * 60)
    
    available_providers = list(ultra.provider_manager.providers.keys())
    
    # Test 1: Simple response schema
    test_messages_1 = [{"role": "user", "content": "What is 5+3? Answer with just the number and your confidence."}]
    
    for provider in available_providers:
        try:
            print(f"\nTesting {provider.upper()} structured output...")
            
            if provider == "openai":
                model = "gpt-4o-mini"
            else:
                model = f"{provider}:claude-3-haiku-20240307"
            
            response, tokens, details = ultra.chat(
                messages=test_messages_1,
                schema=MathResponse,
                model=model,
                steps_pipeline=False,
                reasoning_pipeline=False,
                tools=[]
            )
            
            print(f"✓ {provider.upper()} structured output successful")
            print(f"  Model: {model}")
            print(f"  Response: {response}")
            print(f"  Tokens used: {tokens}")
            
        except Exception as e:
            print(f"✗ {provider.upper()} structured output failed: {e}")

def test_model_parsing():
    """Test model string parsing functionality"""
    print("\n" + "=" * 60)
    print("TESTING MODEL PARSING")
    print("=" * 60)
    
    try:
        # Create a minimal instance just for testing parsing
        ultra = UltraGPT(api_key="test-key")  # Won't make actual API calls
        provider_manager = ultra.provider_manager
        
        test_cases = [
            ("gpt-4o", "openai", "gpt-4o"),
            ("openai:gpt-4o-mini", "openai", "gpt-4o-mini"),
            ("claude:claude-3-sonnet-20240229", "claude", "claude-3-sonnet-20240229"),
            ("claude:claude-3-haiku-20240307", "claude", "claude-3-haiku-20240307"),
        ]
        
        for model_string, expected_provider, expected_model in test_cases:
            provider, model = provider_manager.parse_model_string(model_string)
            if provider == expected_provider and model == expected_model:
                print(f"✓ '{model_string}' → Provider: {provider}, Model: {model}")
            else:
                print(f"✗ '{model_string}' → Expected ({expected_provider}, {expected_model}), Got ({provider}, {model})")
                
    except Exception as e:
        print(f"✗ Model parsing test failed: {e}")

def main():
    """Run all tests"""
    print("UltraGPT Multi-Provider Basic Tests")
    print("Designed for minimal token usage")
    print()
    
    # Check for API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("API Key Status:")
    print(f"  OPENAI_API_KEY: {'✓ Found' if openai_key else '✗ Not found'}")
    print(f"  ANTHROPIC_API_KEY: {'✓ Found' if claude_key else '✗ Not found'}")
    print()
    
    if not openai_key and not claude_key:
        print("⚠ No API keys found. Make sure you have a .env file with your keys or set environment variables.")
        print("  Required format in .env file:")
        print("    OPENAI_API_KEY=your-openai-key")
        print("    ANTHROPIC_API_KEY=your-anthropic-key")
        print()
    
    # Test model parsing (no API calls)
    test_model_parsing()
    
    # Test initialization
    ultra = test_basic_initialization()
    
    # Test basic chat functionality
    test_basic_chat(ultra)
    
    # Test structured output
    test_structured_output(ultra)
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
    
    if not openai_key and not claude_key:
        print("\nNOTE: No API keys provided. To run actual API tests:")
        print("  1. Create a .env file with your API keys, OR")
        print("  2. Set environment variables manually:")
        print("     export OPENAI_API_KEY='your-openai-key'")
        print("     export ANTHROPIC_API_KEY='your-anthropic-key'")
    
    print("\nTo enable Claude support, install: pip install anthropic")
    print("To load .env files automatically, install: pip install python-dotenv")

if __name__ == "__main__":
    main()
