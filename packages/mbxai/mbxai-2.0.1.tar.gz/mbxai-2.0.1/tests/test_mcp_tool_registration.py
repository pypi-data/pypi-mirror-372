"""
Test MCP tool registration flow to identify where $ref schemas are still used.

This test simulates the server-client registration process to find the bug.
"""

import json
import os
from typing import Any
from pydantic import BaseModel, Field

# Add the src directory to the path so we can import from mbxai
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mbxai.mcp.client import MCPTool
from mbxai.tools.types import convert_to_strict_schema


class MetadataFilter(BaseModel):
    """Model for a single metadata filter key-value pair."""
    key: str = Field(description="The metadata field name to filter by")
    value: Any = Field(description="The value to filter for")


class ShopwareKnowledgeSearchInput(BaseModel):
    """Input model for Shopware knowledge search."""
    
    query: str = Field(description="The search query")
    max_results: int = Field(description="Maximum results (1-20)", ge=1, le=20)
    include_metadata: bool = Field(description="Whether to include metadata")
    metadata_filter: list[MetadataFilter] = Field(description="List of metadata filters")


def test_mcp_tool_registration_flow():
    """Test the exact MCP tool registration flow to identify $ref issues."""
    
    print("🔍 Testing MCP Tool Registration Flow")
    print("=" * 50)
    
    # Step 1: Simulate what FastMCP generates (like what MCP server gets)
    print("\n1. Simulating FastMCP schema generation...")
    fastmcp_schema = ShopwareKnowledgeSearchInput.model_json_schema()
    
    print("FastMCP Raw Schema:")
    print(json.dumps(fastmcp_schema, indent=2))
    
    # Create output directory
    tmp_dir = Path(__file__).parent.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    
    # Save FastMCP schema
    with open(tmp_dir / "fastmcp_raw_schema.json", 'w') as f:
        json.dump(fastmcp_schema, f, indent=2)
    
    # Step 2: Simulate what MCP server stores (what goes in Tool.inputSchema)
    print("\n2. What MCP server stores in Tool.inputSchema...")
    mcp_server_stored_schema = fastmcp_schema  # Server just stores the raw schema
    
    with open(tmp_dir / "mcp_server_stored_schema.json", 'w') as f:
        json.dump(mcp_server_stored_schema, f, indent=2)
    
    # Step 3: Simulate what /tools endpoint returns
    print("\n3. What /tools endpoint returns...")
    tools_endpoint_response = {
        "name": "search_shopware_knowledge",
        "description": "Search Shopware knowledge base",
        "inputSchema": mcp_server_stored_schema,  # This has $ref!
        "internal_url": "http://localhost:8000/tools/search_shopware_knowledge/invoke",
        "service": "shopware-search",
        "strict": True
    }
    
    print("Tools endpoint response:")
    print(json.dumps(tools_endpoint_response, indent=2))
    
    with open(tmp_dir / "tools_endpoint_response.json", 'w') as f:
        json.dump(tools_endpoint_response, f, indent=2)
    
    # Step 4: Simulate MCPClient creating MCPTool
    print("\n4. MCPClient creating MCPTool...")
    try:
        # This is what MCPClient.register_mcp_server() does
        mcp_tool = MCPTool(**tools_endpoint_response)
        
        print("✅ MCPTool created successfully")
        print(f"MCPTool.inputSchema: {type(mcp_tool.inputSchema)}")
        
        # Check if inputSchema still has $ref
        schema_str = json.dumps(mcp_tool.inputSchema)
        has_ref = "$ref" in schema_str or "$defs" in schema_str
        print(f"❌ MCPTool.inputSchema still has $ref/$defs: {has_ref}")
        
        if has_ref:
            print("   🚨 PROBLEM: Raw schema with $ref is stored in MCPTool!")
        
        with open(tmp_dir / "mcp_tool_input_schema.json", 'w') as f:
            json.dump(mcp_tool.inputSchema, f, indent=2)
        
    except Exception as e:
        print(f"❌ Failed to create MCPTool: {e}")
        return
    
    # Step 5: Test MCPTool.to_openai_function()
    print("\n5. Testing MCPTool.to_openai_function()...")
    try:
        openai_function = mcp_tool.to_openai_function()
        
        print("✅ OpenAI function created")
        
        # Check if the converted schema still has $ref
        function_schema_str = json.dumps(openai_function["function"]["parameters"])
        has_ref_after = "$ref" in function_schema_str or "$defs" in function_schema_str
        
        print(f"❌ Final OpenAI schema still has $ref/$defs: {has_ref_after}")
        
        if has_ref_after:
            print("   🚨 CRITICAL PROBLEM: convert_to_strict_schema didn't resolve $ref!")
        else:
            print("   ✅ convert_to_strict_schema successfully resolved $ref")
        
        # Check if arrays have items
        def check_arrays_in_schema(schema, path=""):
            issues = []
            if isinstance(schema, dict):
                if schema.get("type") == "array":
                    if "items" not in schema:
                        issues.append(f"Array at {path} missing items")
                    else:
                        print(f"   ✅ Array at {path} has items")
                
                for key, value in schema.items():
                    if key == "properties" and isinstance(value, dict):
                        for prop_name, prop_schema in value.items():
                            issues.extend(check_arrays_in_schema(prop_schema, f"{path}.{prop_name}" if path else prop_name))
                    elif key == "items" and isinstance(value, dict):
                        issues.extend(check_arrays_in_schema(value, f"{path}.items"))
            return issues
        
        array_issues = check_arrays_in_schema(openai_function["function"]["parameters"])
        if array_issues:
            for issue in array_issues:
                print(f"   ❌ {issue}")
        
        with open(tmp_dir / "final_openai_function.json", 'w') as f:
            json.dump(openai_function, f, indent=2)
        
        print(f"\n📁 Files created in {tmp_dir}:")
        print("   - fastmcp_raw_schema.json")
        print("   - mcp_server_stored_schema.json")
        print("   - tools_endpoint_response.json")
        print("   - mcp_tool_input_schema.json")
        print("   - final_openai_function.json")
        
        return openai_function
        
    except Exception as e:
        print(f"❌ Failed to create OpenAI function: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_direct_schema_conversion():
    """Test direct schema conversion to compare with MCP flow."""
    
    print("\n\n🔧 Testing Direct Schema Conversion (for comparison)")
    print("=" * 55)
    
    # Generate the schema
    schema = ShopwareKnowledgeSearchInput.model_json_schema()
    
    print("\n1. Direct conversion without input wrapper...")
    strict_schema = convert_to_strict_schema(schema, strict=True, keep_input_wrapper=False)
    
    schema_str = json.dumps(strict_schema)
    has_ref = "$ref" in schema_str or "$defs" in schema_str
    print(f"   Direct conversion has $ref/$defs: {has_ref}")
    
    print("\n2. Direct conversion with input wrapper...")
    # Simulate MCP-style wrapper
    wrapped_schema = {
        "type": "object",
        "properties": {
            "input": schema
        },
        "required": ["input"]
    }
    
    strict_wrapped = convert_to_strict_schema(wrapped_schema, strict=True, keep_input_wrapper=True)
    
    wrapped_str = json.dumps(strict_wrapped)
    has_ref_wrapped = "$ref" in wrapped_str or "$defs" in wrapped_str
    print(f"   Wrapped conversion has $ref/$defs: {has_ref_wrapped}")
    
    # Save for comparison
    tmp_dir = Path(__file__).parent.parent / "tmp"
    with open(tmp_dir / "direct_conversion_no_wrapper.json", 'w') as f:
        json.dump(strict_schema, f, indent=2)
    
    with open(tmp_dir / "direct_conversion_with_wrapper.json", 'w') as f:
        json.dump(strict_wrapped, f, indent=2)


if __name__ == "__main__":
    try:
        # Test the MCP registration flow
        result = test_mcp_tool_registration_flow()
        
        # Test direct conversion for comparison
        test_direct_schema_conversion()
        
        if result:
            print("\n✅ MCP flow test completed - check the JSON files for details")
        else:
            print("\n❌ MCP flow test failed")
            
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc() 