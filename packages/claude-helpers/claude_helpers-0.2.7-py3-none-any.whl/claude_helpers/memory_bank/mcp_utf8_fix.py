"""UTF-8 fix for FastMCP to properly handle Cyrillic and other Unicode characters."""

import json
import sys
from typing import Any, Dict
from fastmcp import FastMCP


class UTF8FastMCP(FastMCP):
    """FastMCP subclass that properly handles UTF-8 encoding in JSON responses.
    
    This fixes the issue where Cyrillic text appears as Unicode escape sequences
    (\u041f\u0440\u0438\u043d\u044f\u0442\u0438\u0435) instead of proper UTF-8 text.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def _serialize_response(self, response: Dict[str, Any]) -> str:
        """Override JSON serialization to use ensure_ascii=False for proper UTF-8."""
        try:
            return json.dumps(response, ensure_ascii=False, separators=(',', ':'))
        except Exception:
            # Fallback to default behavior if custom serialization fails
            return json.dumps(response, separators=(',', ':'))


def patch_fastmcp_json_encoding():
    """Monkey patch FastMCP to use proper UTF-8 encoding.
    
    This patches the JSON serialization used by FastMCP to properly handle
    Unicode characters without escaping them to \\uXXXX sequences.
    """
    
    # Store original json.dumps
    original_dumps = json.dumps
    
    def utf8_dumps(*args, **kwargs):
        """JSON dumps wrapper that sets ensure_ascii=False by default."""
        # Set ensure_ascii=False unless explicitly overridden
        if 'ensure_ascii' not in kwargs:
            kwargs['ensure_ascii'] = False
        return original_dumps(*args, **kwargs)
    
    # Patch json.dumps globally for this module
    json.dumps = utf8_dumps
    
    print("UTF-8 JSON encoding patch applied", file=sys.stderr)


def create_utf8_mcp_server(name: str, **kwargs) -> FastMCP:
    """Create FastMCP server instance with UTF-8 support.
    
    Args:
        name: Server name
        **kwargs: Additional FastMCP configuration
        
    Returns:
        FastMCP instance with UTF-8 JSON encoding
    """
    # Apply the patch before creating the server
    patch_fastmcp_json_encoding()
    
    # Create normal FastMCP instance
    # The patched json.dumps will be used for all JSON serialization
    mcp = FastMCP(name, **kwargs)
    
    return mcp