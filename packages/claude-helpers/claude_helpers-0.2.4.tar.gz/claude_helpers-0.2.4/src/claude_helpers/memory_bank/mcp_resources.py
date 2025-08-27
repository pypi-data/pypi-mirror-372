"""MCP Resources for Memory Bank - static data access."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

from .mcp_utils import (
    get_memory_bank_path,
    safe_load_yaml,
    paginate_content,
    format_error_response
)
from .increment_utils import (
    ensure_component_state,
    get_increment_details,
    get_full_increment_name
)


# Create MCP server instance for resources
mcp = FastMCP("Memory-Bank Resources")


@mcp.resource("memory-bank://resource-guide")
def get_resource_guide() -> Dict[str, Any]:
    """Comprehensive guide to all available Memory Bank resources.
    
    This resource explains how to access all available resources including
    dynamic/template resources that require parameters.
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {
            "uri": "memory-bank://resource-guide",
            "name": "Memory Bank Resource Guide", 
            "content": "No Memory Bank bound to project",
            "mime_type": "text/plain"
        }
    
    # Get current component state for examples
    state_data = ensure_component_state(memory_bank_path, "02-alpha", "01-modus-id")
    current_increment = state_data.get("current_increment", "01")
    
    guide_content = """# Memory Bank Resource Guide 🗂️

## Static Resources (Always Available)
These resources are always accessible and don't require parameters:

### Architecture Context
- `architecture://tech-context/list` - List all tech-context files
- `architecture://tech-context/{{filename}}` - Read specific tech file
  - Example: `architecture://tech-context/tech-stack.md`
  - Example: `architecture://tech-context/code-standards.md`

## Dynamic Resources (Template-Based)
These resources require parameters in the URI. Replace {{parameter}} with actual values:

### Component Resources
- `architecture://{{release}}/{{component}}/component` - Component specification
  - Example: `architecture://02-alpha/01-modus-id/component`

### Task Resources  
- `todo://{{release}}/{{component}}/increment` - Current increment details
  - Example: `todo://02-alpha/01-modus-id/increment`
- `todo://{{release}}/{{component}}/decomposition` - Task decomposition
  - Example: `todo://02-alpha/01-modus-id/decomposition`

### Progress Resources
- `progress://{{release}}/{{component}}/journal` - Current increment journal
  - Example: `progress://02-alpha/01-modus-id/journal`
- `progress://{{release}}/{{component}}/state` - Combined progress state  
  - Example: `progress://02-alpha/01-modus-id/state`

### Specific Increment Journals
- `progress://{{release}}/{{component}}/{{increment}}/journal` - Specific increment journal
  - Example: `progress://02-alpha/01-modus-id/01-models-and-protocols/journal`
  - Example: `progress://02-alpha/01-modus-id/02-configuration-and-exceptions/journal`

## Current Context Examples
Based on current Memory Bank state:

### Ready-to-Use URIs
- `architecture://02-alpha/01-modus-id/component` ← Component spec
- `progress://02-alpha/01-modus-id/journal` ← Current journal (increment {})
- `progress://02-alpha/01-modus-id/state` ← Progress state
- `todo://02-alpha/01-modus-id/increment` ← Current increment
- `todo://02-alpha/01-modus-id/decomposition` ← Task breakdown

### Available Tech Context Files
To see all available tech files, first read: `architecture://tech-context/list`

## Usage Tips
1. **Start with static resources** like `architecture://tech-context/list` to discover content
2. **Use current context URIs** shown above for immediate access
3. **Replace parameters** in template URIs with actual values
4. **All resources support UTF-8/Cyrillic** text properly

## Tools Available
Use these MCP tools for additional functionality:
- `journal-note` - Add entries to current increment journal
- `ask-memory-bank` - Query Memory Bank content intelligently  
- `get-pm-focus`, `get-dev-focus`, `get-tech-lead-focus` - Get role-specific focus
- `next-increment` - Move to next increment when current is complete
""".format(current_increment)

    return {
        "uri": "memory-bank://resource-guide",
        "name": "Memory Bank Resource Guide",
        "content": guide_content,
        "mime_type": "text/markdown"
    }


@mcp.resource("architecture://tech-context/list")
def get_tech_context_resources() -> Dict[str, Any]:
    """List all tech-context files from Memory Bank.
    
    Returns a list of available tech-context files without their content.
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {
            "uri": "architecture://tech-context/list",
            "name": "Tech Context Files",
            "content": "No Memory Bank bound to project",
            "mime_type": "text/plain"
        }
    
    tech_context_dir = memory_bank_path / "architecture" / "tech-context"
    if not tech_context_dir.exists():
        return {
            "uri": "architecture://tech-context/list",
            "name": "Tech Context Files",
            "content": "No tech-context directory found",
            "mime_type": "text/plain"
        }
    
    # Build a markdown list of available files
    content_lines = ["# Available Tech Context Files\n"]
    for file_path in sorted(tech_context_dir.glob("*.md")):
        try:
            file_size = file_path.stat().st_size
            name = file_path.stem.replace("-", " ").title()
            content_lines.append(f"- `architecture://tech-context/{file_path.name}` - {name} ({file_size // 1024}KB)")
        except Exception:
            continue
    
    return {
        "uri": "architecture://tech-context/list",
        "name": "Tech Context Files",
        "content": "\n".join(content_lines),
        "mime_type": "text/markdown"
    }


@mcp.resource("architecture://{release}/{component}/component")
def get_component_spec(release: str, component: str) -> Dict[str, Any]:
    """Get component specification from architecture.
    
    Args:
        release: Release name
        component: Component name
        
    Returns:
        Component specification with pagination support
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    # First try architecture path
    spec_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
    
    # Fallback to implementation path
    if not spec_file.exists():
        spec_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "component.md"
    
    if not spec_file.exists():
        return {"error": f"Component specification not found for {component}"}
    
    try:
        content = spec_file.read_text()
        return {
            "uri": f"architecture://{release}/{component}/component",
            "name": f"{component} Specification",
            "content": content,
            "mime_type": "text/markdown"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("todo://{release}/{component}/increment")
def get_current_increment(release: str, component: str) -> Dict[str, Any]:
    """Get current increment details from implementation.
    
    Args:
        release: Release name
        component: Component name
        
    Returns:
        Current increment content with pagination
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    # Ensure component state and get current increment
    state_data = ensure_component_state(memory_bank_path, release, component)
    current_increment = state_data.get("current_increment", "01")
    
    # Find increment file
    increment_pattern = f"{current_increment}-*.md"
    increment_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "increments"
    
    if not increment_dir.exists():
        return {"error": f"No increments found for {component}"}
    
    increment_files = list(increment_dir.glob(increment_pattern))
    
    if not increment_files:
        return {"error": f"Increment {current_increment} not found"}
    
    try:
        content = increment_files[0].read_text()
        return {
            "uri": f"todo://{release}/{component}/increment",
            "name": f"Current Increment: {increment_files[0].stem}",
            "content": content,
            "mime_type": "text/markdown",
            "increment": current_increment
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("todo://{release}/{component}/decomposition") 
def get_decomposition(release: str, component: str) -> Dict[str, Any]:
    """Get component decomposition overview.
    
    Args:
        release: Release name
        component: Component name
        
    Returns:
        Decomposition content with pagination
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    decomposition_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "decomposition.md"
    
    if not decomposition_file.exists():
        return {"error": f"Decomposition not found for {component}"}
    
    try:
        content = decomposition_file.read_text()
        return {
            "uri": f"todo://{release}/{component}/decomposition",
            "name": f"{component} Decomposition",
            "content": content,
            "mime_type": "text/markdown"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("progress://{release}/{component}/journal")
def get_journal(release: str, component: str) -> Dict[str, Any]:
    """Get journal for current increment.
    
    Args:
        release: Release name
        component: Component name
        
    Returns:
        Journal content with pagination
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    # Ensure component state and get current increment
    state_data = ensure_component_state(memory_bank_path, release, component)
    current_increment = state_data.get("current_increment", "01")
    
    # Get full increment name for path
    increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
    
    # Get journal file
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
    
    if not journal_file.exists():
        # Return empty journal structure
        return {
            "uri": f"progress://{release}/{component}/journal",
            "name": f"Journal - {component}/{increment_name}",
            "content": f"# Journal - {component}/{increment_name}\n\nNo entries yet.",
            "mime_type": "text/markdown",
            "increment": current_increment
        }
    
    try:
        content = journal_file.read_text()
        return {
            "uri": f"progress://{release}/{component}/journal",
            "name": f"Journal - {component}/{current_increment}",
            "content": content,
            "mime_type": "text/markdown",
            "increment": current_increment
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("progress://{release}/{component}/{increment}/journal")
def get_increment_journal(release: str, component: str, increment: str) -> Dict[str, Any]:
    """Get journal for specific increment.
    
    Args:
        release: Release name
        component: Component name
        increment: Increment name (e.g., "01-models-and-protocols")
        
    Returns:
        Journal content for the specific increment
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    # Get journal file for specific increment
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment / "journal.md"
    
    if not journal_file.exists():
        # Return empty journal structure
        return {
            "uri": f"progress://{release}/{component}/{increment}/journal",
            "name": f"Journal - {component}/{increment}",
            "content": f"# Journal - {component}/{increment}\n\nNo entries yet.",
            "mime_type": "text/markdown",
            "increment": increment
        }
    
    try:
        content = journal_file.read_text()
        return {
            "uri": f"progress://{release}/{component}/{increment}/journal",
            "name": f"Journal - {component}/{increment}",
            "content": content,
            "mime_type": "text/markdown",
            "increment": increment
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("progress://{release}/{component}/state")
def get_combined_state(release: str, component: str) -> Dict[str, Any]:
    """Get combined initial + progress state.
    
    Combines initial-state.md from implementation with progress-state.md from progress.
    
    Args:
        release: Release name
        component: Component name
        
    Returns:
        Combined state information with pagination support
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    combined_content = f"# Combined State - {component}\n\n"
    
    # Load initial state
    initial_state_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "initial-state.md"
    if initial_state_file.exists():
        try:
            initial_content = initial_state_file.read_text()
            # Remove YAML header if present
            if initial_content.startswith('---\n'):
                yaml_end = initial_content.find('\n---\n', 4)
                if yaml_end != -1:
                    initial_content = initial_content[yaml_end + 5:]
            combined_content += "## Initial State\n\n" + initial_content + "\n\n"
        except Exception:
            combined_content += "## Initial State\n\n*Unable to load initial state*\n\n"
    else:
        combined_content += "## Initial State\n\n*No initial state defined*\n\n"
    
    # Load progress state
    progress_state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "progress-state.md"
    if progress_state_file.exists():
        try:
            progress_content = progress_state_file.read_text()
            # Extract YAML header for metadata
            state_data = safe_load_yaml(progress_state_file)
            
            # Remove YAML header from content
            if progress_content.startswith('---\n'):
                yaml_end = progress_content.find('\n---\n', 4)
                if yaml_end != -1:
                    progress_content = progress_content[yaml_end + 5:]
            
            combined_content += "## Progress State\n\n"
            combined_content += f"**Current Increment**: {state_data.get('current_increment', 'unknown')}\n"
            combined_content += f"**Status**: {state_data.get('status', 'unknown')}\n"
            combined_content += f"**Last Updated**: {state_data.get('datetime', 'unknown')}\n\n"
            combined_content += progress_content
        except Exception:
            combined_content += "## Progress State\n\n*Unable to load progress state*\n\n"
    else:
        combined_content += "## Progress State\n\n*No progress recorded*\n\n"
    
    return {
        "uri": f"progress://{release}/{component}/state",
        "name": f"{component} Combined State",
        "content": combined_content,
        "mime_type": "text/markdown"
    }


@mcp.resource("architecture://tech-context/{filename}")
def get_specific_tech_context(filename: str) -> Dict[str, Any]:
    """Get specific tech-context file.
    
    Args:
        filename: Name of the tech-context file
        
    Returns:
        File content with pagination
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'
    
    file_path = memory_bank_path / "architecture" / "tech-context" / filename
    
    if not file_path.exists():
        return {"error": f"Tech context file {filename} not found"}
    
    try:
        content = file_path.read_text()
        return {
            "uri": f"architecture://tech-context/{filename}",
            "name": file_path.stem.replace("-", " ").title(),
            "content": content,
            "mime_type": "text/markdown"
        }
    except Exception as e:
        return {"error": str(e)}