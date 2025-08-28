"""Main MCP server for Memory Bank - combines tools, resources, and prompts."""

import sys
from pathlib import Path
from fastmcp import FastMCP
from .mcp_utf8_fix import create_utf8_mcp_server, patch_fastmcp_json_encoding

# Import all MCP components
from .mcp_tools import mcp as tools_mcp
from .mcp_resources import mcp as resources_mcp  
from .mcp_prompts import mcp as prompts_mcp
from .mcp_focus import mcp as focus_mcp
from .mcp_resources_list import mcp as resources_list_mcp
from .mcp_resource_tools import mcp as resource_tools_mcp
from .mcp_utils import get_memory_bank_path


def create_combined_mcp_server() -> FastMCP:
    """Create combined MCP server with all Memory Bank capabilities."""
    
    # Apply UTF-8 JSON encoding patch for proper Unicode handling
    patch_fastmcp_json_encoding()
    
    # Create main server
    main_mcp = FastMCP("Memory-Bank")
    
    # Register all tools from mcp_tools
    for tool_name, tool_func in tools_mcp._tool_manager._tools.items():
        main_mcp._tool_manager._tools[tool_name] = tool_func
    
    # Register all tools from mcp_focus
    for tool_name, tool_func in focus_mcp._tool_manager._tools.items():
        main_mcp._tool_manager._tools[tool_name] = tool_func
    
    # Register tools from mcp_resources_list
    for tool_name, tool_func in resources_list_mcp._tool_manager._tools.items():
        main_mcp._tool_manager._tools[tool_name] = tool_func
    
    # Register tools from mcp_resource_tools (workaround for sub-agents)
    for tool_name, tool_func in resource_tools_mcp._tool_manager._tools.items():
        main_mcp._tool_manager._tools[tool_name] = tool_func
    
    # Register all resources from mcp_resources
    if hasattr(resources_mcp, '_resource_manager'):
        # Ensure main_mcp has resource manager
        if not hasattr(main_mcp, '_resource_manager'):
            from fastmcp.resources import ResourceManager
            main_mcp._resource_manager = ResourceManager()
        
        # Copy regular resources
        for resource_uri, resource_func in resources_mcp._resource_manager._resources.items():
            main_mcp._resource_manager._resources[resource_uri] = resource_func
        
        # Copy resource templates (parametrized resources)
        if hasattr(resources_mcp._resource_manager, '_templates'):
            if not hasattr(main_mcp._resource_manager, '_templates'):
                main_mcp._resource_manager._templates = {}
            for template_uri, template_func in resources_mcp._resource_manager._templates.items():
                main_mcp._resource_manager._templates[template_uri] = template_func
    
    # Register resources from mcp_resources_list
    if hasattr(resources_list_mcp, '_resource_manager'):
        if not hasattr(main_mcp, '_resource_manager'):
            from fastmcp.resources import ResourceManager
            main_mcp._resource_manager = ResourceManager()
        
        for resource_uri, resource_func in resources_list_mcp._resource_manager._resources.items():
            main_mcp._resource_manager._resources[resource_uri] = resource_func
    
    # Register all prompts from mcp_prompts
    if hasattr(prompts_mcp, '_prompt_manager'):
        for prompt_name, prompt_func in prompts_mcp._prompt_manager._prompts.items():
            if hasattr(main_mcp, '_prompt_manager'):
                main_mcp._prompt_manager._prompts[prompt_name] = prompt_func
    
    return main_mcp


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
        # Create combined server
        mcp = create_combined_mcp_server()
        
        # List registered components for debugging
        if hasattr(mcp, '_tool_manager'):
            tools = list(mcp._tool_manager._tools.keys())
            print(f"Registered tools: {tools}", file=sys.stderr)
        
        if hasattr(mcp, '_resource_manager'):
            resources = list(getattr(mcp, '_resource_manager')._resources.keys())
            templates = list(getattr(mcp._resource_manager, '_templates', {}).keys())
            print(f"Registered resources: {len(resources)} static, {len(templates)} templates", file=sys.stderr)
            if templates:
                print(f"Resource templates: {templates[:5]}...", file=sys.stderr)
        
        if hasattr(mcp, '_prompt_manager'):
            prompts = list(getattr(mcp, '_prompt_manager')._prompts.keys())
            print(f"Registered prompts: {prompts}", file=sys.stderr)
        
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


# For backward compatibility
run_mcp_server = run_memory_bank_mcp_server