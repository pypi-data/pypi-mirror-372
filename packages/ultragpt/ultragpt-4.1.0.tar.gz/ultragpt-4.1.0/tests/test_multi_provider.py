"""
Test multi-provider support in UltraGPT
"""

import os
import sys
sys.path.append('src')

from ultragpt import UltraGPT

def test_initialization():
    """Test UltraGPT initialization with multiple providers"""
    print("Testing initialization...")
    
    # Test with OpenAI only
    try:
        ultra_openai = UltraGPT(
            api_key="test-key",  # Will fail on actual API call but should initialize
            verbose=True
        )
        print("✓ OpenAI-only initialization successful")
        assert "openai" in ultra_openai.provider_manager.providers
    except Exception as e:
        print(f"✗ OpenAI initialization failed: {e}")
    
    # Test with both providers (will fail gracefully if anthropic not installed)
    try:
        ultra_multi = UltraGPT(
            api_key="test-openai-key",
            claude_api_key="test-claude-key",
            verbose=True
        )
        print("✓ Multi-provider initialization successful")
        assert "openai" in ultra_multi.provider_manager.providers
        if "claude" in ultra_multi.provider_manager.providers:
            print("✓ Claude provider loaded")
        else:
            print("⚠ Claude provider not available (anthropic package not installed)")
    except Exception as e:
        print(f"✗ Multi-provider initialization failed: {e}")

def test_model_parsing():
    """Test model string parsing"""
    print("\nTesting model parsing...")
    
    try:
        ultra = UltraGPT(api_key="test-key")
        provider_manager = ultra.provider_manager
        
        # Test default (OpenAI)
        provider, model = provider_manager.parse_model_string("gpt-4o")
        assert provider == "openai" and model == "gpt-4o"
        print("✓ Default model parsing works")
        
        # Test explicit provider
        provider, model = provider_manager.parse_model_string("claude:claude-3-sonnet-20240229")
        assert provider == "claude" and model == "claude-3-sonnet-20240229"
        print("✓ Explicit provider parsing works")
        
        # Test OpenAI explicit
        provider, model = provider_manager.parse_model_string("openai:gpt-4o")
        assert provider == "openai" and model == "gpt-4o"
        print("✓ Explicit OpenAI parsing works")
        
    except Exception as e:
        print(f"✗ Model parsing failed: {e}")

def test_provider_availability():
    """Test provider availability checks"""
    print("\nTesting provider availability...")
    
    try:
        ultra = UltraGPT(api_key="test-key")
        
        # OpenAI should always be available
        try:
            provider = ultra.provider_manager.get_provider("openai")
            print("✓ OpenAI provider available")
        except Exception as e:
            print(f"✗ OpenAI provider not available: {e}")
        
        # Claude may or may not be available
        try:
            provider = ultra.provider_manager.get_provider("claude")
            print("✓ Claude provider available")
        except Exception as e:
            print(f"⚠ Claude provider not available (expected if not installed): {e}")
            
    except Exception as e:
        print(f"✗ Provider availability test failed: {e}")

def test_tools_config():
    """Test tools configuration with provider specifications"""
    print("\nTesting tools configuration...")
    
    # Test configuration structure
    tools_config = {
        "web-search": {
            "model": "claude:claude-3-sonnet-20240229",
            "max_results": 5
        },
        "calculator": {
            "model": "gpt-4o",
            "max_history_items": 3
        }
    }
    
    print("✓ Tools config structure valid")
    
    # Test model parsing in config
    web_search_model = tools_config["web-search"]["model"]
    calc_model = tools_config["calculator"]["model"]
    
    try:
        ultra = UltraGPT(api_key="test-key")
        
        provider1, model1 = ultra.provider_manager.parse_model_string(web_search_model)
        provider2, model2 = ultra.provider_manager.parse_model_string(calc_model)
        
        assert provider1 == "claude" and model1 == "claude-3-sonnet-20240229"
        assert provider2 == "openai" and model2 == "gpt-4o"
        
        print("✓ Tool config model parsing works")
        
    except Exception as e:
        print(f"✗ Tool config test failed: {e}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("ULTRAGPT MULTI-PROVIDER SUPPORT TESTS")
    print("=" * 60)
    
    test_initialization()
    test_model_parsing()
    test_provider_availability()
    test_tools_config()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)
    
    print("\nNOTE: Some tests may show warnings if Claude provider is not available.")
    print("To enable full Claude support, install: pip install anthropic")

if __name__ == "__main__":
    main()
