"""Unified Memory Bank MCP Server - single FastMCP instance."""

import sys
from pathlib import Path
from typing import Dict, Any, List
from fastmcp import FastMCP

from .mcp_utils import (
    get_memory_bank_path,
    get_working_directory,
    create_yaml_header,
    safe_load_yaml,
    format_error_response,
    format_success_response,
    load_template
)
from .increment_utils import (
    ensure_component_state,
    get_increment_list,
    get_increment_details,
    update_component_progress,
    create_increment_structure,
    get_full_increment_name
)

# Create single MCP server instance
mcp = FastMCP("Memory-Bank")

# ============================================================================
# TOOLS - Active operations
# ============================================================================

# Import raw functions (not decorated) from mcp_tools
from .mcp_tools import journal_note, next_increment, ask_memory_bank

# Import raw functions from mcp_focus  
from .mcp_focus import get_pm_focus, get_dev_focus, get_tech_lead_focus

# Register tools with our single MCP instance
# These are now raw functions, not decorated
mcp.tool(name="journal-note")(journal_note)
mcp.tool(name="next-increment")(next_increment)
mcp.tool(name="ask-memory-bank")(ask_memory_bank)
mcp.tool(name="get-pm-focus")(get_pm_focus)
mcp.tool(name="get-dev-focus")(get_dev_focus)
mcp.tool(name="get-tech-lead-focus")(get_tech_lead_focus)


# Add a helper resource that explains available patterns
@mcp.resource("memory-bank://help")
def get_help_resource() -> Dict[str, Any]:
    """Help resource explaining available Memory Bank resources."""
    return {
        "uri": "memory-bank://help",
        "name": "Memory Bank Help",
        "content": """# Memory Bank Resources

## Available Resource Templates

### Architecture Resources
- `architecture://tech-context/list` - List all tech context files
- `architecture://tech-context/{filename}` - Get specific tech context file (e.g. code-standards.md)
- `architecture://{release}/{component}/component` - Component specification

### Todo Resources  
- `todo://{release}/{component}/increment` - Current increment details
- `todo://{release}/{component}/decomposition` - Task decomposition

### Progress Resources
- `progress://{release}/{component}/journal` - Current increment journal
- `progress://{release}/{component}/{increment}/journal` - Specific increment journal
- `progress://{release}/{component}/state` - Combined initial + progress state

## Parameters
- `{release}` - Release name (e.g. "02-alpha")
- `{component}` - Component name (e.g. "01-modus-id")  
- `{increment}` - Increment name (e.g. "01-models-and-protocols")
- `{filename}` - File name with .md extension

## Example Usage
```
ReadMcpResourceTool(
    server="memory-bank-kenoma",
    uri="progress://02-alpha/01-modus-id/journal"
)
```
""",
        "mime_type": "text/markdown"
    }


# ============================================================================
# RESOURCES - Static data access
# ============================================================================

# Import resource functions from mcp_resources
from .mcp_resources import (
    get_tech_context_resources,
    get_component_spec,
    get_current_increment,
    get_decomposition,
    get_journal,
    get_increment_journal,
    get_combined_state,
    get_specific_tech_context
)

# Register resources with proper decorators
# These are now raw functions, not decorated
mcp.resource("architecture://tech-context/list")(get_tech_context_resources)
mcp.resource("architecture://{release}/{component}/component")(get_component_spec)
mcp.resource("todo://{release}/{component}/increment")(get_current_increment)
mcp.resource("todo://{release}/{component}/decomposition")(get_decomposition)
mcp.resource("progress://{release}/{component}/journal")(get_journal)
mcp.resource("progress://{release}/{component}/{increment}/journal")(get_increment_journal)
mcp.resource("progress://{release}/{component}/state")(get_combined_state)
mcp.resource("architecture://tech-context/{filename}")(get_specific_tech_context)


# Resource guide is not needed - we have the list-resources tool
# which provides dynamic, context-aware listing


# ============================================================================
# PROMPTS - Guided workflows  
# ============================================================================

# Import prompt functions from mcp_prompts if needed
# Currently we don't have prompts implemented, but structure is ready

# ============================================================================
# SERVER RUNNER
# ============================================================================

def run_memory_bank_mcp_server():
    """Run Memory-Bank MCP server with stdio transport."""
    
    # Debug output to stderr
    print(f"Memory-Bank MCP starting from: {Path.cwd()}", file=sys.stderr)
    
    memory_bank_path = get_memory_bank_path()
    if memory_bank_path:
        print(f"Found Memory-Bank at: {memory_bank_path}", file=sys.stderr)
    else:
        print("No Memory-Bank binding found in current directory", file=sys.stderr)
        print("Some features will be limited. Run 'claude-helpers memory-bank init' to bind.", file=sys.stderr)
    
    try:
        # List registered components for debugging
        if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
            tools = list(mcp._tool_manager._tools.keys())
            print(f"Registered tools: {len(tools)} tools - {tools}", file=sys.stderr)
        else:
            print("No tool manager found", file=sys.stderr)
        
        if hasattr(mcp, '_resource_manager'):
            if hasattr(mcp._resource_manager, '_resources'):
                resources = list(mcp._resource_manager._resources.keys())
                print(f"Registered static resources: {len(resources)}", file=sys.stderr)
            if hasattr(mcp._resource_manager, '_templates'):
                templates = list(mcp._resource_manager._templates.keys())
                print(f"Registered resource templates: {len(templates)}", file=sys.stderr)
        else:
            print("No resource manager found", file=sys.stderr)
        
        sys.stderr.flush()
        
        # Run the server
        mcp.run()  # Default transport is stdio
        
    except KeyboardInterrupt:
        print("MCP server interrupted", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"MCP server error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_memory_bank_mcp_server()