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


@mcp.resource("architecture://tech-context/list")
def get_tech_context_resources() -> List[Dict[str, str]]:
    """Get all tech-context files from Memory Bank.
    
    Returns all files from architecture/tech-context/ directory as resources.
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return []
    
    tech_context_dir = memory_bank_path / "architecture" / "tech-context"
    if not tech_context_dir.exists():
        return []
    
    resources = []
    for file_path in tech_context_dir.glob("*.md"):
        try:
            # For large files, just return metadata, actual content via specific resource
            file_size = file_path.stat().st_size
            if file_size > 50000:  # If larger than 50KB
                resources.append({
                    "uri": f"/architecture/tech-context/{file_path.name}",
                    "name": file_path.stem.replace("-", " ").title(),
                    "description": f"Tech context document ({file_size // 1024}KB)",
                    "mime_type": "text/markdown"
                })
            else:
                content = file_path.read_text()
                resources.append({
                    "uri": f"/architecture/tech-context/{file_path.name}",
                    "name": file_path.stem.replace("-", " ").title(),
                    "content": content,
                    "mime_type": "text/markdown"
                })
        except Exception:
            continue
    
    return resources


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
        result = paginate_content(content, 1)
        result["uri"] = f"/architecture/{release}/{component}/component.md"
        result["name"] = f"{component} Specification"
        result["mime_type"] = "text/markdown"
        return result
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
        result = paginate_content(content, 1)
        result["uri"] = f"/todo/{release}/{component}/increment.md"
        result["name"] = f"Current Increment: {increment_files[0].stem}"
        result["mime_type"] = "text/markdown"
        result["increment"] = current_increment
        return result
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
        result = paginate_content(content, 1)
        result["uri"] = f"/todo/{release}/{component}/decomposition.md"
        result["name"] = f"{component} Decomposition"
        result["mime_type"] = "text/markdown"
        return result
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
            "uri": f"/progress/{release}/{component}/journal.md",
            "name": f"Journal - {component}/{increment_name}",
            "content": f"# Journal - {component}/{increment_name}\n\nNo entries yet.",
            "mime_type": "text/markdown",
            "increment": current_increment
        }
    
    try:
        content = journal_file.read_text()
        result = paginate_content(content, 1)
        result["uri"] = f"/progress/{release}/{component}/journal.md"
        result["name"] = f"Journal - {component}/{current_increment}"
        result["mime_type"] = "text/markdown"
        result["increment"] = current_increment
        return result
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
            "uri": f"/progress/{release}/{component}/{increment}/journal.md",
            "name": f"Journal - {component}/{increment}",
            "content": f"# Journal - {component}/{increment}\n\nNo entries yet.",
            "mime_type": "text/markdown",
            "increment": increment
        }
    
    try:
        content = journal_file.read_text()
        result = paginate_content(content, 1)
        result["uri"] = f"/progress/{release}/{component}/{increment}/journal.md"
        result["name"] = f"Journal - {component}/{increment}"
        result["mime_type"] = "text/markdown"
        result["increment"] = increment
        return result
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
    
    # Apply pagination
    result = paginate_content(combined_content, 1)
    result["uri"] = f"/progress/{release}/{component}/state.md"
    result["name"] = f"{component} Combined State"
    result["mime_type"] = "text/markdown"
    return result


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
        result = paginate_content(content, 1)
        result["uri"] = f"/architecture/tech-context/{filename}"
        result["name"] = file_path.stem.replace("-", " ").title()
        result["mime_type"] = "text/markdown"
        return result
    except Exception as e:
        return {"error": str(e)}