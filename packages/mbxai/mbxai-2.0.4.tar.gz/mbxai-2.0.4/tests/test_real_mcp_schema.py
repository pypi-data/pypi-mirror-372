"""
Test with the real MCP schema structure from production logs.

This test uses the exact schema structure that was causing the error
to verify the nested $ref resolution fix works correctly.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mbxai.mcp.client import MCPTool
from mbxai.tools.types import convert_to_strict_schema


def test_real_production_schema():
    """Test with the exact schema structure from production logs."""
    
    print("🔍 Testing Real Production MCP Schema")
    print("=" * 45)
    
    # This is the exact schema structure from your production logs
    real_mcp_tool_data = {
        "description": "Search the Shopware knowledge base for relevant information.\n    \n    This tool performs semantic search through the Shopware knowledge collection\n    to find documentation, guides, and other relevant information based on the query.\n    \n    Args:\n        input: ShopwareKnowledgeSearchInput containing search parameters\n        \n    Returns:\n        ShopwareKnowledgeSearchResponse with search results and metadata\n        \n    Raises:\n        RuntimeError: If the search operation fails\n    ",
        "inputSchema": {
            "$defs": {
                "MetadataFilter": {
                    "description": "Model for a single metadata filter key-value pair.\n\nEach filter represents one condition to apply to the search.\nCommon filter keys include:\n- category: Content category (e.g., 'api', 'plugins', 'themes')\n- version: Shopware version (e.g., '6.5', '6.6') \n- title: Document title (partial match)\n- optimized: Whether content was AI-optimized (true/false)\n- source_url: Source URL (partial match)\n- optimization_strategy: Strategy used ('enhance_readability', etc.)\n- ai_generated_metadata: Whether metadata was AI-generated (true/false)",
                    "properties": {
                        "key": {
                            "description": "The metadata field name to filter by",
                            "title": "Key",
                            "type": "string"
                        },
                        "value": {
                            "description": "The value to filter for",
                            "title": "Value"
                        }
                    },
                    "required": [
                        "key",
                        "value"
                    ],
                    "title": "MetadataFilter",
                    "type": "object"
                },
                "ShopwareKnowledgeSearchInput": {
                    "description": "Input model for Shopware knowledge search.",
                    "properties": {
                        "include_metadata": {
                            "description": "Whether to include metadata in the search results",
                            "title": "Include Metadata",
                            "type": "boolean"
                        },
                        "max_results": {
                            "description": "Maximum number of search results to return (1-20)",
                            "maximum": 20,
                            "minimum": 1,
                            "title": "Max Results",
                            "type": "integer"
                        },
                        "metadata_filter": {
                            "description": "List of metadata filters to apply to the search. Use empty list [] for no filtering, or specify key-value pairs like [{'key': 'category', 'value': 'api'}, {'key': 'version', 'value': '6.5'}]",
                            "items": {
                                "$ref": "#/$defs/MetadataFilter"  # This is the problematic nested $ref
                            },
                            "title": "Metadata Filter",
                            "type": "array"
                        },
                        "query": {
                            "description": "The search query to find relevant Shopware knowledge and documentation",
                            "title": "Query",
                            "type": "string"
                        }
                    },
                    "required": [
                        "query",
                        "max_results",
                        "include_metadata",
                        "metadata_filter"
                    ],
                    "title": "ShopwareKnowledgeSearchInput",
                    "type": "object"
                }
            },
            "properties": {
                "input": {
                    "$ref": "#/$defs/ShopwareKnowledgeSearchInput"  # This references the above
                }
            },
            "required": [
                "input"
            ],
            "title": "search_shopware_knowledgeArguments",
            "type": "object"
        },
        "internal_url": "http://shopware-knowledge.mbxai-mcp.svc.cluster.local:5000/tools/search_shopware_knowledge/invoke",
        "name": "search_shopware_knowledge",
        "service": "shopware-knowledge",
        "strict": True
    }
    
    print("\n1. Creating MCPTool with real production schema...")
    
    try:
        # Create MCPTool (this should work)
        mcp_tool = MCPTool(**real_mcp_tool_data)
        print("✅ MCPTool created successfully")
        
        # Verify the raw schema still has $refs
        schema_str = json.dumps(mcp_tool.inputSchema)
        has_refs = "$ref" in schema_str and "$defs" in schema_str
        print(f"   Raw inputSchema has $ref/$defs: {has_refs}")
        
        if not has_refs:
            print("   ⚠️  Warning: Expected raw schema to have $refs")
        
    except Exception as e:
        print(f"❌ Failed to create MCPTool: {e}")
        return False
    
    print("\n2. Converting to OpenAI function with nested $ref resolution...")
    
    try:
        # This is where the magic happens - convert to OpenAI function
        openai_function = mcp_tool.to_openai_function()
        print("✅ OpenAI function created successfully")
        
        # Check if all $refs are resolved
        function_params = openai_function["function"]["parameters"]
        params_str = json.dumps(function_params)
        
        has_refs_after = "$ref" in params_str or "$defs" in params_str
        print(f"   Final schema has $ref/$defs: {has_refs_after}")
        
        if has_refs_after:
            print("   ❌ FAIL: Schema conversion didn't resolve all $refs!")
            return False
        else:
            print("   ✅ SUCCESS: All $refs resolved!")
        
        # Check the specific structure we care about
        print("\n3. Validating specific schema structure...")
        
        # Should have input property
        if "input" not in function_params["properties"]:
            print("   ❌ Missing 'input' property")
            return False
        
        input_schema = function_params["properties"]["input"]
        print("   ✅ Found 'input' property")
        
        # Should have metadata_filter array
        if "metadata_filter" not in input_schema["properties"]:
            print("   ❌ Missing 'metadata_filter' in input schema")
            return False
        
        metadata_filter = input_schema["properties"]["metadata_filter"]
        print("   ✅ Found 'metadata_filter' property")
        
        # Should be array type
        if metadata_filter["type"] != "array":
            print(f"   ❌ metadata_filter type is {metadata_filter['type']}, expected 'array'")
            return False
        print("   ✅ metadata_filter is array type")
        
        # Should have items property
        if "items" not in metadata_filter:
            print("   ❌ metadata_filter missing 'items' property")
            return False
        print("   ✅ metadata_filter has 'items' property")
        
        # Items should be object with key/value properties (no $ref)
        items_schema = metadata_filter["items"]
        if items_schema["type"] != "object":
            print(f"   ❌ metadata_filter items type is {items_schema['type']}, expected 'object'")
            return False
        print("   ✅ metadata_filter items is object type")
        
        if "key" not in items_schema["properties"] or "value" not in items_schema["properties"]:
            print("   ❌ metadata_filter items missing 'key' or 'value' properties")
            return False
        print("   ✅ metadata_filter items has 'key' and 'value' properties")
        
        # Check that items schema has no $ref
        items_str = json.dumps(items_schema)
        if "$ref" in items_str:
            print("   ❌ metadata_filter items still contains $ref")
            return False
        print("   ✅ metadata_filter items has no $ref")
        
        # Save the results
        tmp_dir = Path(__file__).parent.parent / "tmp"
        tmp_dir.mkdir(exist_ok=True)
        
        with open(tmp_dir / "real_production_schema_raw.json", 'w') as f:
            json.dump(mcp_tool.inputSchema, f, indent=2)
        
        with open(tmp_dir / "real_production_schema_converted.json", 'w') as f:
            json.dump(openai_function, f, indent=2)
        
        print(f"\n📁 Files saved to {tmp_dir}:")
        print("   - real_production_schema_raw.json")
        print("   - real_production_schema_converted.json")
        
        print("\n🎉 ALL TESTS PASSED! Nested $ref resolution works correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to convert to OpenAI function: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_conversion_with_nested_refs():
    """Test direct schema conversion with the nested refs structure."""
    
    print("\n\n🔧 Testing Direct Conversion with Nested $refs")
    print("=" * 50)
    
    # The problematic schema structure
    nested_ref_schema = {
        "$defs": {
            "MetadataFilter": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Filter key"},
                    "value": {"type": "string", "description": "Filter value"}
                },
                "required": ["key", "value"]
            },
            "ShopwareInput": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "metadata_filter": {
                        "type": "array",
                        "description": "Metadata filters",
                        "items": {
                            "$ref": "#/$defs/MetadataFilter"  # Nested $ref
                        }
                    }
                },
                "required": ["query", "metadata_filter"]
            }
        },
        "type": "object",
        "properties": {
            "input": {
                "$ref": "#/$defs/ShopwareInput"  # Top-level $ref
            }
        },
        "required": ["input"]
    }
    
    print("Testing direct conversion with keep_input_wrapper=True...")
    
    try:
        result = convert_to_strict_schema(nested_ref_schema, strict=True, keep_input_wrapper=True)
        
        # Check no $refs remain
        result_str = json.dumps(result)
        has_refs = "$ref" in result_str or "$defs" in result_str
        
        print(f"   Result has $ref/$defs: {has_refs}")
        
        if has_refs:
            print("   ❌ Direct conversion still has $refs")
            return False
        else:
            print("   ✅ Direct conversion resolved all $refs")
        
        # Save result
        tmp_dir = Path(__file__).parent.parent / "tmp"
        with open(tmp_dir / "direct_nested_ref_conversion.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Direct conversion failed: {e}")
        return False


if __name__ == "__main__":
    try:
        print("🧪 Testing Nested $ref Resolution Fix")
        print("=" * 40)
        
        # Test with real production schema
        test1_passed = test_real_production_schema()
        
        # Test direct conversion
        test2_passed = test_direct_conversion_with_nested_refs()
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("The nested $ref resolution fix is working correctly!")
        else:
            print("\n❌ SOME TESTS FAILED")
            print("The fix needs more work.")
            
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc() 