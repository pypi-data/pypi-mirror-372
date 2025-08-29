#!/usr/bin/env python3
"""
Test script for UltraGPT with new mathematical operations tool and model control
"""

import os
import sys
import dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ultragpt import UltraGPT

# Load environment variables
dotenv.load_dotenv()

def test_math_operations():
    """Test the new math operations tool"""
    print("Testing Math Operations Tool...")
    
    # You'll need to set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Initialize UltraGPT
    ultragpt = UltraGPT(
        api_key=api_key,
        verbose=True
    )
    
    # Test range checking
    messages = [
        {"role": "user", "content": "Check if the numbers [1, 5, 8, 12, 15] lie between 0 and 10"}
    ]
    
    response, tokens, details = ultragpt.chat(
        messages=messages,
        tools=["math-operations"],
        steps_pipeline=False,
        reasoning_pipeline=False
    )
    
    print(f"Response: {response}")
    print(f"Tokens used: {tokens}")

def test_model_control():
    """Test the new model control for pipelines"""
    print("\nTesting Model Control...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    ultragpt = UltraGPT(
        api_key=api_key,
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "What is 2 + 2?"}
    ]
    
    response, tokens, details = ultragpt.chat(
        messages=messages,
        model="gpt-4o",  # Main model
        steps_model="gpt-4o-mini",  # Cheaper model for steps
        reasoning_model="gpt-4o-mini",  # Cheaper model for reasoning
        reasoning_iterations=2,
        tools=[]  # No tools for this simple test
    )
    
    print(f"Response: {response}")
    print(f"Tokens used: {tokens}")
    print(f"Details: {details}")

if __name__ == "__main__":
    test_math_operations()
    test_model_control()
