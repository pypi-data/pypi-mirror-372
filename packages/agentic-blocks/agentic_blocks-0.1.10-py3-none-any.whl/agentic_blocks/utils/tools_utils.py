"""
Utilities for working with tools across different formats.
"""

from typing import Dict, Any, List


def langchain_tool_to_openai_format(tool) -> Dict[str, Any]:
    """
    Convert a LangChain StructuredTool to OpenAI function calling format.
    
    Args:
        tool: A langchain_core.tools.structured.StructuredTool instance
        
    Returns:
        Dictionary in OpenAI function calling format, compatible with 
        MCPClient.list_tools() output and call_llm() tools parameter
    """
    schema = tool.args_schema.model_json_schema()
    
    return {
        "type": "function",
        "function": {
            "name": schema.get("title", tool.name),
            "description": schema.get("description", ""),
            "parameters": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        }
    }


def langchain_tools_to_openai_format(tools: List) -> List[Dict[str, Any]]:
    """
    Convert a list of LangChain StructuredTools to OpenAI function calling format.
    
    Args:
        tools: List of langchain_core.tools.structured.StructuredTool instances
        
    Returns:
        List of dictionaries in OpenAI function calling format, compatible with 
        MCPClient.list_tools() output and call_llm() tools parameter
    """
    return [langchain_tool_to_openai_format(tool) for tool in tools]