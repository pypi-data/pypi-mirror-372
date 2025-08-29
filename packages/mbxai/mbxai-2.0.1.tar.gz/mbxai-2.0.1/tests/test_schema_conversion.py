"""
Test for schema conversion with Pydantic models containing arrays.

This test demonstrates the fix for the "array schema missing items" error
when converting Pydantic models to OpenAI function schemas.
"""

import json
import os
from typing import Any
from pydantic import BaseModel, Field

# Add the src directory to the path so we can import from mbxai
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mbxai.tools.types import convert_to_strict_schema


class MetadataFilter(BaseModel):
    """Model for a single metadata filter key-value pair.
    
    Each filter represents one condition to apply to the search.
    Common filter keys include:
    - category: Content category (e.g., 'api', 'plugins', 'themes')
    - version: Shopware version (e.g., '6.5', '6.6') 
    - title: Document title (partial match)
    - optimized: Whether content was AI-optimized (true/false)
    - source_url: Source URL (partial match)
    - optimization_strategy: Strategy used ('enhance_readability', etc.)
    - ai_generated_metadata: Whether metadata was AI-generated (true/false)
    """
    
    key: str = Field(description="The metadata field name to filter by")
    value: Any = Field(description="The value to filter for")


class ShopwareKnowledgeSearchInput(BaseModel):
    """Input model for Shopware knowledge search."""
    
    query: str = Field(
        description="The search query to find relevant Shopware knowledge and documentation"
    )
    max_results: int = Field(
        description="Maximum number of search results to return (1-20)",
        ge=1,
        le=20
    )
    include_metadata: bool = Field(
        description="Whether to include metadata in the search results"
    )
    metadata_filter: list[MetadataFilter] = Field(
        description="List of metadata filters to apply to the search. Use empty list [] for no filtering, or specify key-value pairs like [{'key': 'category', 'value': 'api'}, {'key': 'version', 'value': '6.5'}]"
    )


def test_shopware_schema_conversion():
    """Test that Shopware knowledge search Pydantic models are properly converted to OpenAI-compatible schemas."""
    
    print("🧪 Testing Schema Conversion for Shopware Knowledge Search")
    print("=" * 60)
    
    # Generate the JSON schema from the Pydantic model
    print("\n1. Generating Pydantic JSON Schema...")
    pydantic_schema = ShopwareKnowledgeSearchInput.model_json_schema()
    
    # Convert to OpenAI strict schema
    print("2. Converting to OpenAI strict schema...")
    strict_schema = convert_to_strict_schema(
        pydantic_schema, 
        strict=True, 
        keep_input_wrapper=False
    )
    
    # Create OpenAI function definition
    print("3. Creating OpenAI Function Definition...")
    function_def = {
        "type": "function",
        "function": {
            "name": "search_shopware_knowledge",
            "description": "Search Shopware knowledge base for relevant documentation and information",
            "parameters": strict_schema,
            "strict": True
        }
    }
    
    # Create local tmp directory for output files
    tmp_dir = Path(__file__).parent.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    
    # Create output files in local tmp directory
    original_schema_file = tmp_dir / "shopware_original_schema.json"
    strict_schema_file = tmp_dir / "shopware_strict_schema.json"
    function_def_file = tmp_dir / "shopware_openai_function.json"
    
    with open(original_schema_file, 'w') as f:
        json.dump(pydantic_schema, f, indent=2)
    
    with open(strict_schema_file, 'w') as f:
        json.dump(strict_schema, f, indent=2)
    
    with open(function_def_file, 'w') as f:
        json.dump(function_def, f, indent=2)
    
    print(f"\n📄 Generated files:")
    print(f"   Original Pydantic Schema: {original_schema_file}")
    print(f"   OpenAI Strict Schema: {strict_schema_file}")
    print(f"   OpenAI Function Definition: {function_def_file}")
    
    # Validation checks
    print("\n4. Validation Checks...")
    
    # Check that all arrays have 'items' property
    def check_arrays_have_items(schema, path=""):
        """Recursively check that all arrays have items property."""
        issues = []
        
        if isinstance(schema, dict):
            if schema.get("type") == "array":
                if "items" not in schema:
                    issues.append(f"Array at {path} missing 'items' property")
                else:
                    print(f"   ✓ Array at {path} has items: {schema['items'].get('type', 'unknown')}")
                    # Recursively check items
                    issues.extend(check_arrays_have_items(schema["items"], f"{path}.items"))
            
            # Check properties
            if "properties" in schema:
                for prop_name, prop_schema in schema["properties"].items():
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    issues.extend(check_arrays_have_items(prop_schema, prop_path))
        
        return issues
    
    print("✅ Checking that all arrays have 'items' property...")
    issues = check_arrays_have_items(strict_schema)
    assert not issues, f"Schema validation failed: {issues}"
    print("   ✓ All arrays have proper 'items' definitions")
    
    # Check that no $ref or $defs exist
    print("\n✅ Checking that no $ref or $defs exist...")
    schema_str = json.dumps(strict_schema)
    assert "$ref" not in schema_str and "$defs" not in schema_str, "Schema still contains $ref or $defs"
    print("   ✓ No $ref or $defs found - schema is fully inlined")
    
    # Check that all objects have additionalProperties: false
    def check_additional_properties(schema, path=""):
        """Recursively check that all objects have additionalProperties: false."""
        issues = []
        
        if isinstance(schema, dict):
            if schema.get("type") == "object":
                if schema.get("additionalProperties") is not False:
                    issues.append(f"Object at {path} missing 'additionalProperties: false'")
                else:
                    print(f"   ✓ Object at {path} has additionalProperties: false")
            
            # Check nested schemas
            for key, value in schema.items():
                if key in ["properties", "items"] and isinstance(value, dict):
                    if key == "properties":
                        for prop_name, prop_schema in value.items():
                            prop_path = f"{path}.{prop_name}" if path else prop_name
                            issues.extend(check_additional_properties(prop_schema, prop_path))
                    else:  # items
                        issues.extend(check_additional_properties(value, f"{path}.items"))
        
        return issues
    
    print("\n✅ Checking that all objects have additionalProperties: false...")
    issues = check_additional_properties(strict_schema)
    assert not issues, f"additionalProperties validation failed: {issues}"
    print("   ✓ All objects have additionalProperties: false")
    
    # Check that constraints are preserved
    print("\n✅ Checking that constraints are preserved...")
    max_results_prop = strict_schema["properties"]["max_results"]
    assert max_results_prop["minimum"] == 1, "minimum constraint not preserved"
    assert max_results_prop["maximum"] == 20, "maximum constraint not preserved"
    print("   ✓ Constraints preserved (ge=1, le=20 for max_results)")
    
    # Check that metadata_filter array has proper MetadataFilter items
    print("\n✅ Checking metadata_filter array structure...")
    metadata_filter_prop = strict_schema["properties"]["metadata_filter"]
    assert metadata_filter_prop["type"] == "array", "metadata_filter should be array"
    assert "items" in metadata_filter_prop, "metadata_filter array missing items"
    
    items_schema = metadata_filter_prop["items"]
    assert items_schema["type"] == "object", "metadata_filter items should be object"
    assert "key" in items_schema["properties"], "metadata_filter items missing 'key' property"
    assert "value" in items_schema["properties"], "metadata_filter items missing 'value' property"
    assert items_schema["required"] == ["key", "value"], "metadata_filter items missing required fields"
    print("   ✓ metadata_filter array has proper MetadataFilter object items")
    
    print("\n🎉 All tests passed! Schema is OpenAI/OpenRouter compatible!")
    print("\nKey improvements:")
    print("- ✅ Arrays have proper 'items' definitions")
    print("- ✅ No $ref or $defs (fully inlined)")
    print("- ✅ All objects have additionalProperties: false")
    print("- ✅ Constraints preserved (ge=1, le=20 for max_results)")
    print("- ✅ Complex nested structures handled correctly")
    print("- ✅ metadata_filter array properly defines MetadataFilter items")
    
    # Return file paths for further inspection
    return {
        "original_schema_file": str(original_schema_file),
        "strict_schema_file": str(strict_schema_file),
        "function_def_file": str(function_def_file),
        "function_definition": function_def
    }


def test_mcp_style_schema_conversion():
    """Test schema conversion with MCP-style input wrapper."""
    
    print("\n🧪 Testing MCP-Style Schema Conversion")
    print("=" * 50)
    
    # Generate the JSON schema from the Pydantic model
    pydantic_schema = ShopwareKnowledgeSearchInput.model_json_schema()
    
    # Create MCP-style schema with input wrapper
    mcp_style_schema = {
        "type": "object",
        "properties": {
            "input": pydantic_schema
        },
        "required": ["input"],
        "additionalProperties": False
    }
    
    # Convert with input wrapper
    strict_schema_with_wrapper = convert_to_strict_schema(
        mcp_style_schema,
        strict=True,
        keep_input_wrapper=True
    )
    
    # Create output file in local tmp directory
    tmp_dir = Path(__file__).parent.parent / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    
    mcp_schema_file = tmp_dir / "shopware_mcp_style_schema.json"
    with open(mcp_schema_file, 'w') as f:
        json.dump(strict_schema_with_wrapper, f, indent=2)
    
    print(f"📄 MCP-Style Schema: {mcp_schema_file}")
    
    # Validate MCP-style structure
    assert "input" in strict_schema_with_wrapper["properties"], "MCP wrapper missing input property"
    input_schema = strict_schema_with_wrapper["properties"]["input"]
    assert "metadata_filter" in input_schema["properties"], "Input schema missing metadata_filter"
    
    print("✅ MCP-style schema conversion successful!")
    
    return str(mcp_schema_file)


if __name__ == "__main__":
    try:
        # Run the main test
        result = test_shopware_schema_conversion()
        
        # Run the MCP-style test
        mcp_file = test_mcp_style_schema_conversion()
        
        print(f"\n✅ All tests completed successfully!")
        print(f"\n📁 Check these files to inspect the generated schemas:")
        print(f"   - Original: {result['original_schema_file']}")
        print(f"   - Strict: {result['strict_schema_file']}")
        print(f"   - Function: {result['function_def_file']}")
        print(f"   - MCP Style: {mcp_file}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise 