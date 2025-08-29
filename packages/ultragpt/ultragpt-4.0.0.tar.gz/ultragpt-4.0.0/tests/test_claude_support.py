#!/usr/bin/env python3
"""
Test script for UltraGPT Claude support
"""

import os
import sys

# Global variable to store UltraGPT class after import
UltraGPT = None

def test_imports():
    """Test that all required imports work"""
    global UltraGPT
    print("Testing imports...")
    try:
        from src.ultragpt import UltraGPT as _UltraGPT
        UltraGPT = _UltraGPT
        print("✓ UltraGPT import successful")
        
        # Test that anthropic import works if available
        try:
            import anthropic
            print("✓ Anthropic SDK available")
        except ImportError:
            print("⚠ Anthropic SDK not installed")
            
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_initialization():
    """Test that both providers can be initialized"""
    print("\nTesting initialization...")
    
    # Test OpenAI provider
    try:
        ultragpt_openai = UltraGPT(
            api_key="dummy-key",
            provider="openai"
        )
        print("✓ OpenAI provider initialization successful")
    except Exception as e:
        print(f"✗ OpenAI provider initialization failed: {e}")
    
    # Test Claude provider (only if anthropic is available)
    try:
        import anthropic
        ultragpt_claude = UltraGPT(
            api_key="dummy-key",
            provider="anthropic"
        )
        print("✓ Claude provider initialization successful")
    except ImportError:
        print("⚠ Claude provider test skipped - Anthropic SDK not available")
    except Exception as e:
        print(f"✗ Claude provider initialization failed: {e}")

def test_default_models():
    """Test that default models are set correctly"""
    print("\nTesting default models...")
    
    try:
        # OpenAI
        ultragpt_openai = UltraGPT(
            api_key="dummy-key",
            provider="openai"
        )
        openai_default = ultragpt_openai._get_default_model()
        print(f"✓ OpenAI default model: {openai_default}")
        
        # Claude (if available)
        try:
            import anthropic
            ultragpt_claude = UltraGPT(
                api_key="dummy-key",
                provider="anthropic"
            )
            claude_default = ultragpt_claude._get_default_model()
            print(f"✓ Claude default model: {claude_default}")
        except ImportError:
            print("⚠ Claude default model test skipped")
            
    except Exception as e:
        print(f"✗ Default model test failed: {e}")

def test_message_conversion():
    """Test Claude message conversion"""
    print("\nTesting Claude message conversion...")
    
    try:
        import anthropic
        ultragpt = UltraGPT(
            api_key="dummy-key",
            provider="anthropic"
        )
        
        # Test message conversion
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        
        claude_messages, system_prompt = ultragpt._convert_messages_for_claude(messages)
        
        print(f"✓ System prompt: {system_prompt}")
        print(f"✓ Claude messages: {len(claude_messages)} messages")
        print(f"✓ First message role: {claude_messages[0]['role']}")
        
    except ImportError:
        print("⚠ Claude message conversion test skipped")
    except Exception as e:
        print(f"✗ Message conversion test failed: {e}")

def test_error_handling():
    """Test error handling for invalid configurations"""
    print("\nTesting error handling...")
    
    # Test invalid provider
    try:
        UltraGPT(provider="invalid")
        print("✗ Should have failed with invalid provider")
    except ValueError as e:
        print(f"✓ Invalid provider error: {e}")
    
    # Test missing OpenAI key
    try:
        UltraGPT(provider="openai")
        print("✗ Should have failed with missing OpenAI key")
    except ValueError as e:
        print(f"✓ Missing OpenAI key error: {e}")
    
    # Test missing Claude key (if anthropic available)
    try:
        import anthropic
        UltraGPT(provider="anthropic")
        print("✗ Should have failed with missing Claude key")
    except ImportError:
        print("⚠ Claude key test skipped")
    except ValueError as e:
        print(f"✓ Missing Claude key error: {e}")

def test_tools_config():
    """Test that tools config is set correctly for each provider"""
    print("\nTesting tools configuration...")
    
    try:
        # OpenAI
        ultragpt_openai = UltraGPT(
            api_key="dummy-key",
            provider="openai"
        )
        openai_config = ultragpt_openai._get_default_tools_config()
        print(f"✓ OpenAI tools config model: {openai_config['web-search']['model']}")
        
        # Claude (if available)
        try:
            import anthropic
            ultragpt_claude = UltraGPT(
                api_key="dummy-key",
                provider="anthropic"
            )
            claude_config = ultragpt_claude._get_default_tools_config()
            print(f"✓ Claude tools config model: {claude_config['web-search']['model']}")
        except ImportError:
            print("⚠ Claude tools config test skipped")
            
    except Exception as e:
        print(f"✗ Tools config test failed: {e}")

def main():
    """Run all tests"""
    print("UltraGPT Claude Support - Test Suite")
    print("=" * 50)
    
    if not test_imports():
        print("\nFATAL: Import test failed. Cannot continue.")
        sys.exit(1)
    
    test_initialization()
    test_default_models()
    test_message_conversion()
    test_error_handling()
    test_tools_config()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("\nTo test with real API calls, set your API keys:")
    print("- OPENAI_API_KEY")
    print("- ANTHROPIC_API_KEY")
    print("Then run example_claude_support.py")

if __name__ == "__main__":
    main()
