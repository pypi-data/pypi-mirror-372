"""
Type definitions for the tools package.
"""

from typing import Any, Callable
from pydantic import BaseModel, Field
import logging
import json

logger = logging.getLogger(__name__)

def _resolve_ref(schema: dict[str, Any], ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve a $ref to its actual schema definition.
    
    Args:
        schema: The current schema object
        ref: The reference string (e.g., "#/$defs/MyType")
        root_schema: The root schema containing $defs
        
    Returns:
        The resolved schema definition with all nested $refs also resolved
    """
    if ref.startswith("#/"):
        # Remove the "#/" prefix and split the path
        path_parts = ref[2:].split("/")
        current = root_schema
        
        # Navigate through the path
        for part in path_parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                logger.warning(f"Could not resolve $ref: {ref}")
                return {"type": "object", "additionalProperties": False}
        
        if isinstance(current, dict):
            # Recursively process the resolved schema to handle nested $refs
            return _convert_property_to_strict(current, root_schema)
        else:
            return {"type": "object", "additionalProperties": False}
    else:
        logger.warning(f"Unsupported $ref format: {ref}")
        return {"type": "object", "additionalProperties": False}

def _convert_property_to_strict(prop: dict[str, Any], root_schema: dict[str, Any]) -> dict[str, Any]:
    """Convert a single property to strict format, recursively handling nested objects and arrays.
    
    Args:
        prop: The property definition to convert
        root_schema: The root schema containing $defs
        
    Returns:
        A strict format property definition with all $refs resolved
    """
    # Handle $ref resolution first - this may return a completely different schema
    if "$ref" in prop:
        # Get the referenced schema path
        ref = prop["$ref"]
        if ref.startswith("#/"):
            path_parts = ref[2:].split("/")
            current = root_schema
            
            # Navigate through the path to get the referenced schema
            for part in path_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    logger.warning(f"Could not resolve $ref: {ref}")
                    return {"type": "object", "additionalProperties": False}
            
            if isinstance(current, dict):
                # Recursively process the resolved schema
                return _convert_property_to_strict(current, root_schema)
            else:
                return {"type": "object", "additionalProperties": False}
        else:
            logger.warning(f"Unsupported $ref format: {ref}")
            return {"type": "object", "additionalProperties": False}
    
    # Get the property type, defaulting to string
    prop_type = prop.get("type", "string")
    
    # Start with basic property structure
    new_prop = {
        "type": prop_type,
        "description": prop.get("description", f"A {prop_type} parameter")
    }
    
    # Handle specific types
    if prop_type == "object":
        # Objects need additionalProperties: false and properties
        new_prop["additionalProperties"] = False
        new_prop["properties"] = {}
        new_prop["required"] = []
        
        # Process nested properties recursively
        if "properties" in prop:
            for nested_name, nested_prop in prop["properties"].items():
                new_prop["properties"][nested_name] = _convert_property_to_strict(nested_prop, root_schema)
        
        # Copy required fields
        if "required" in prop:
            new_prop["required"] = prop["required"]
            
    elif prop_type == "array":
        # Arrays must have items definition
        if "items" in prop:
            # Recursively process items schema (this could also have $refs)
            new_prop["items"] = _convert_property_to_strict(prop["items"], root_schema)
        else:
            # Default items schema if missing
            new_prop["items"] = {
                "type": "string",
                "description": "Array item"
            }
            
    elif prop_type in ["string", "number", "integer", "boolean"]:
        # For primitive types, copy additional constraints
        if "enum" in prop:
            new_prop["enum"] = prop["enum"]
        if "minimum" in prop:
            new_prop["minimum"] = prop["minimum"]
        if "maximum" in prop:
            new_prop["maximum"] = prop["maximum"]
        if "pattern" in prop:
            new_prop["pattern"] = prop["pattern"]
        if "format" in prop:
            new_prop["format"] = prop["format"]
    
    return new_prop

def convert_to_strict_schema(schema: dict[str, Any], strict: bool = True, keep_input_wrapper: bool = False) -> dict[str, Any]:
    """Convert a schema to strict format required by OpenAI.
    
    This function handles:
    - Resolving all $ref and $defs to inline definitions
    - Adding required 'items' property for arrays
    - Ensuring all objects have 'additionalProperties: false'
    - Recursively processing nested schemas
    
    Args:
        schema: The input schema to validate and convert
        strict: Whether to enforce strict validation with additionalProperties: false
        keep_input_wrapper: Whether to keep the input wrapper (for MCP tools)
        
    Returns:
        A schema in strict format with all references resolved
    """
    if not schema:
        return {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

    # Create a new schema object to ensure we have all required fields
    strict_schema = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False  # Always enforce additionalProperties: false for OpenRouter
    }

    # Store the root schema for $ref resolution
    root_schema = schema

    # Handle input wrapper
    if "properties" in schema and "input" in schema["properties"]:
        inputSchema = schema["properties"]["input"]
        
        # If input has a $ref, resolve it
        if "$ref" in inputSchema:
            inputSchema = _resolve_ref(inputSchema, inputSchema["$ref"], root_schema)
        
        if keep_input_wrapper:
            # Create the input property schema
            input_prop_schema = {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False  # Always enforce additionalProperties: false for OpenRouter
            }
            
            # Process input properties
            if "properties" in inputSchema:
                for prop_name, prop in inputSchema["properties"].items():
                    input_prop_schema["properties"][prop_name] = _convert_property_to_strict(prop, root_schema)
            
            # Copy over required fields for input schema
            if "required" in inputSchema:
                input_prop_schema["required"] = inputSchema["required"]
            
            # Add the input property to the main schema
            strict_schema["properties"]["input"] = input_prop_schema
            
            # Copy over required fields for main schema
            if "required" in schema:
                strict_schema["required"] = schema["required"]
        else:
            # If not keeping input wrapper, use input schema directly
            if "properties" in inputSchema:
                for prop_name, prop in inputSchema["properties"].items():
                    strict_schema["properties"][prop_name] = _convert_property_to_strict(prop, root_schema)
            
            # Copy over required fields
            if "required" in inputSchema:
                strict_schema["required"] = inputSchema["required"]
    else:
        # If no input wrapper, use the schema as is
        if "properties" in schema:
            for prop_name, prop in schema["properties"].items():
                strict_schema["properties"][prop_name] = _convert_property_to_strict(prop, root_schema)
        
        # Copy over required fields
        if "required" in schema:
            strict_schema["required"] = schema["required"]

    return strict_schema

class ToolCall(BaseModel):
    """A tool call from the model."""
    id: str
    name: str
    arguments: dict[str, Any]

class Tool(BaseModel):
    """A tool that can be used by the model."""
    name: str
    description: str
    function: Callable[..., Any] | None = None  # Make function optional
    schema: dict[str, Any]

    def to_openai_function(self) -> dict[str, Any]:
        """Convert the tool to an OpenAI function definition."""
        # Ensure schema is in strict format
        strict_schema = convert_to_strict_schema(self.schema)
        
        function_def = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": strict_schema,
                "strict": True
            }
        }
        
        logger.debug(f"(types) Created function definition for {self.name}: {json.dumps(function_def, indent=2)}")
        return function_def 