"""Dynamic resource listing for Memory Bank MCP."""

from pathlib import Path
from typing import List, Dict, Any
from fastmcp import FastMCP

from .mcp_utils import get_memory_bank_path
from .increment_utils import ensure_component_state, get_full_increment_name

# Create MCP server instance for resource listing
mcp = FastMCP("Memory-Bank Resource List")


# This entire file is not needed anymore
# MCP has built-in resources/list method that automatically lists all registered resources
# The mcp_server.py already registers all resources properly


# No static resource needed - we have the list-resources tool that does this dynamically