"""
Simple test for UltraGPT Tool Call functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.ultragpt.schemas import UserTool, ToolCallResponse, SingleToolCallResponse

def test_schemas():
    """Test that the new schemas work correctly"""
    print("Testing schemas...")
    
    # Test UserTool schema
    tool = UserTool(
        name="test_tool",
        description="A test tool",
        parameters_schema={"type": "object", "properties": {"param1": {"type": "string"}}},
        usage_guide="Use when testing",
        when_to_use="Always for testing"
    )
    print(f"UserTool created: {tool.name}")
    
    # Test tool call schemas
    from src.ultragpt.schemas import ToolCall
    
    tool_call = ToolCall(
        tool_name="test_tool",
        parameters={"param1": "value1"},
        reasoning="This is a test"
    )
    print(f"ToolCall created: {tool_call.tool_name}")
    
    # Test response schemas
    single_response = SingleToolCallResponse(tool_call=tool_call)
    print(f"SingleToolCallResponse created")
    
    multiple_response = ToolCallResponse(tool_calls=[tool_call])
    print(f"ToolCallResponse created with {len(multiple_response.tool_calls)} tools")
    
    print("✓ All schemas working correctly!")

def test_prompts():
    """Test that the new prompts work correctly"""
    print("\nTesting prompts...")
    
    from src.ultragpt.prompts import generate_tool_call_prompt, generate_single_tool_call_prompt, generate_multiple_tool_call_prompt
    
    example_tools = [
        {
            "name": "test_tool",
            "description": "A test tool",
            "parameters_schema": {"type": "object"},
            "usage_guide": "Test usage",
            "when_to_use": "For testing"
        }
    ]
    
    # Test prompt generation
    prompt1 = generate_tool_call_prompt(example_tools, allow_multiple=True)
    prompt2 = generate_single_tool_call_prompt(example_tools)
    prompt3 = generate_multiple_tool_call_prompt(example_tools)
    
    print(f"✓ Tool call prompt generated ({len(prompt1)} chars)")
    print(f"✓ Single tool call prompt generated ({len(prompt2)} chars)")
    print(f"✓ Multiple tool call prompt generated ({len(prompt3)} chars)")

if __name__ == "__main__":
    print("="*50)
    print("UltraGPT Tool Call Functionality Test")
    print("="*50)
    
    try:
        test_schemas()
        test_prompts()
        print("\n✓ All tests passed! Tool call functionality is ready.")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
