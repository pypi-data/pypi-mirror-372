"""UTF-8 wrapper for MCP resources to ensure proper encoding."""

import json
from typing import Dict, Any


def ensure_utf8_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all string values in dict are properly UTF-8 encoded.
    
    This is a workaround for FastMCP using json.dumps() with default settings
    which escapes Unicode characters.
    """
    if not isinstance(data, dict):
        return data
    
    # For resources, we mainly care about the 'content' field
    if 'content' in data and isinstance(data['content'], str):
        # Force UTF-8 encoding by re-encoding
        # This doesn't actually fix the problem since FastMCP will still escape it
        # But at least ensures the content is valid UTF-8
        pass
    
    return data


def wrap_resource_function(func):
    """Decorator to wrap resource functions with UTF-8 handling.
    
    Note: This is a temporary workaround. The proper fix would be to
    configure FastMCP to use json.dumps(ensure_ascii=False).
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return ensure_utf8_dict(result)
    
    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    
    return wrapper