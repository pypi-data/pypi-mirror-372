"""MCP Prompts for Memory Bank - workflow commands."""

from pathlib import Path
from typing import Optional
from fastmcp import FastMCP

from .mcp_utils import (
    get_memory_bank_path,
    get_working_directory,
    safe_load_yaml,
    load_template
)
from .increment_utils import (
    ensure_component_state,
    get_full_increment_name
)


# Create MCP server instance for prompts
mcp = FastMCP("Memory-Bank Prompts")


@mcp.prompt("implement-component")
def implement_component(release: str, component: str) -> str:
    """Initialize component implementation workflow for owner/PM.
    
    This prompt loads the PM role and protocol, establishes focus on the 
    release and component, and starts the implementation workflow.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        
    Returns:
        Formatted prompt to start the implementation workflow
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "Error: Memory-Bank not bound to current project. Run 'claude-helpers memory-bank init' first."
    
    # Load implement-component prompt template
    template = load_template("workflow/pm/implement-component.md", memory_bank_path)
    
    if not template:
        # Fallback prompt if template not found
        template = """
# Implement Component: {component}

You are now acting as the PM (Project Manager) for implementing component **{component}** in release **{release}**.

## Your Role
As PM, you coordinate the implementation workflow between owner, dev, and tech-lead roles.

## Current Context
- **Release**: {release}
- **Component**: {component}
- **Working Directory**: {working_dir}
- **Memory Bank**: {memory_bank_path}

## Available MCP Tools
- `get-pm-focus` - Get your current focus and context
- `journal-note` - Log important decisions and progress
- `next-increment` - Move to the next increment when current is complete

## Available MCP Resources
- `/todo/{release}/{component}/decomposition.md` - Component breakdown
- `/todo/{release}/{component}/increment.md` - Current increment details
- `/progress/{release}/{component}/state.md` - Current state
- `/progress/{release}/{component}/journal.md` - Work journal

## Workflow
1. First, call `get-pm-focus` to understand the current state
2. Make a journal note about starting the implementation
3. Review the decomposition and current increment
4. Coordinate with dev and tech-lead sub-agents as needed

Begin by getting your PM focus for this component.
"""
    
    # Get current state information using ensure_component_state
    try:
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        status = state_data.get("increment_status") or state_data.get("status", "not_started")
        
        # Ensure we have full increment name
        if not current_increment or '-' not in str(current_increment):
            current_increment = get_full_increment_name(memory_bank_path, release, component, str(current_increment))
        
        # Ensure current_increment is a string and not multiline
        current_increment = str(current_increment).strip().replace('\n', ' ')
        status = str(status).strip().replace('\n', ' ')
        
    except Exception as e:
        # Fallback if state loading fails
        current_increment = get_full_increment_name(memory_bank_path, release, component, "01")
        status = "not_started"
    
    # Format the prompt with variables
    prompt = template.format(
        release=release,
        component=component,
        increment=current_increment,  # Add increment for backward compatibility
        current_increment=current_increment,
        status=status,
        working_dir=str(get_working_directory()),
        memory_bank_path=str(memory_bank_path)
    )
    
    return prompt


# Note: The HIL 'ask' prompt will be in the HIL MCP module