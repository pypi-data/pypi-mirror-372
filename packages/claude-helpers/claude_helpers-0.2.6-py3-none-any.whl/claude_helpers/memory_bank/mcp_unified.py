"""Unified Memory Bank MCP Server - all in one file with single FastMCP instance."""

import json
import yaml
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# Import utilities and helpers
from .mcp_utils import (
    get_memory_bank_path,
    get_working_directory,
    create_yaml_header,
    safe_load_yaml,
    format_error_response,
    format_success_response,
    load_template,
    paginate_content
)
from .increment_utils import (
    ensure_component_state,
    get_increment_list,
    get_increment_details,
    update_component_progress,
    create_increment_structure,
    get_full_increment_name,
    _update_state_file_header
)
from .increment_models import IncrementJournalEntry

# Create THE SINGLE MCP server instance
mcp = FastMCP("Memory-Bank")

# ============================================================================
# TOOLS - Active operations
# ============================================================================

@mcp.tool(name="journal-note")
def journal_note(release: str, component: str, role: str, message: str) -> str:
    """Add journal entry for current increment."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return format_error_response("Memory-Bank not bound to current project")
    
    try:
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        
        create_increment_structure(memory_bank_path, release, component, current_increment)
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
        journal_file.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc)
        datetime_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = f"\n## {datetime_str} - {role}\n\n{message}\n"
        
        if not journal_file.exists():
            header = create_yaml_header(
                datetime=datetime_str,
                release=release,
                component=component,
                increment=current_increment
            )
            content = header + f"# Journal - {component}/{increment_name}\n" + entry
            journal_file.write_text(content)
        else:
            existing = journal_file.read_text()
            journal_file.write_text(existing + entry)
        
        return format_success_response({
            "status": "success",
            "journal_file": str(journal_file.relative_to(memory_bank_path)),
            "timestamp": datetime_str,
            "increment": current_increment,
            "role": role
        })
        
    except Exception as e:
        return format_error_response(f"Failed to create journal entry: {e}")


@mcp.tool(name="next-increment")
async def next_increment(release: str, component: str) -> str:
    """Move to next increment within component."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return format_error_response("Memory-Bank not bound to current project")
    
    try:
        state_data = ensure_component_state(memory_bank_path, release, component)
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "progress-state.md"
        
        current_increment = state_data.get("current_increment", "01")
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        # Generate progress-state section using Claude Code SDK or fallback
        try:
            from .mcp_tools import _generate_progress_state_with_sdk
            overview = await _generate_progress_state_with_sdk(memory_bank_path, release, component, current_increment)
        except:
            from .mcp_tools import _get_journal_content_as_overview
            overview = _get_journal_content_as_overview(memory_bank_path, release, component, increment_name)
        
        # Update progress-state with overview
        if state_file.exists():
            content = state_file.read_text()
            content = content.rstrip() + "\n\n" + overview + "\n"
            state_file.write_text(content)
            
            # Update state for next increment
            current_num = current_increment.split('-')[0] if '-' in current_increment else current_increment
            next_increment_num = int(current_num) + 1
            next_increment_str = str(next_increment_num).zfill(2)
            next_increment_full = get_full_increment_name(memory_bank_path, release, component, next_increment_str)
            
            state_data["current_increment"] = next_increment_full
            _update_state_file_header(state_file, state_data)
        
        # Get all increments and check if next exists
        all_increments = get_increment_list(memory_bank_path, release, component)
        
        if next_increment_str not in all_increments:
            # Component completed
            progress = update_component_progress(memory_bank_path, release, component, current_increment)
            
            return format_success_response({
                "status": "completed",
                "message": f"Component {component} completed! All {len(all_increments)} increments finished.",
                "completed_increment": current_increment,
                "total_increments": len(all_increments),
                "completion_percentage": 100.0,
                "overview_generated": True
            })
        
        # Get next increment details
        next_details = get_increment_details(memory_bank_path, release, component, next_increment_str)
        progress = update_component_progress(memory_bank_path, release, component, current_increment)
        create_increment_structure(memory_bank_path, release, component, next_increment_full)
        
        return format_success_response({
            "status": "success",
            "previous_increment": increment_name,
            "current_increment": next_increment_full,
            "increment_title": next_details.get("title", f"Increment {next_increment_full}") if next_details else f"Increment {next_increment_full}",
            "increment_description": next_details.get("description", "") if next_details else "",
            "progress": {
                "completed": len(progress.completed_increments),
                "total": progress.total_increments,
                "percentage": progress.completion_percentage
            },
            "overview_generated": True,
            "ready": True
        })
        
    except Exception as e:
        return format_error_response(f"Failed to move to next increment: {e}")


@mcp.tool(name="list-memory-bank-resources")
def list_available_resources(release: str = "02-alpha", component: str = "01-modus-id") -> str:
    """List all available Memory Bank resources for current context."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "Memory-Bank not bound to current project"
    
    resources = []
    
    # Tech context resources
    tech_context_dir = memory_bank_path / "architecture" / "tech-context"
    if tech_context_dir.exists():
        resources.append("📚 **Tech Context Resources**:")
        for file_path in tech_context_dir.glob("*.md"):
            resources.append(f"  - `architecture://tech-context/{file_path.name}` - {file_path.stem.replace('-', ' ').title()}")
    
    # Component-specific resources
    resources.append(f"\n📦 **Component Resources** (Release: {release}, Component: {component}):")
    
    spec_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
    if not spec_file.exists():
        spec_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "component.md"
    if spec_file.exists():
        resources.append(f"  - `architecture://{release}/{component}/component` - Component specification")
    
    decomp_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "decomposition.md"
    if decomp_file.exists():
        resources.append(f"  - `todo://{release}/{component}/decomposition` - Task decomposition")
    
    try:
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        resources.append(f"  - `todo://{release}/{component}/increment` - Current increment: {increment_name}")
    except:
        pass
    
    # Progress resources
    resources.append(f"\n📝 **Progress Resources**:")
    resources.append(f"  - `progress://{release}/{component}/state` - Combined initial + progress state")
    resources.append(f"  - `progress://{release}/{component}/journal` - Current increment journal")
    
    increments_dir = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments"
    if increments_dir.exists():
        resources.append(f"\n  **Available Increment Journals**:")
        for inc_dir in sorted(increments_dir.iterdir()):
            if inc_dir.is_dir():
                journal_file = inc_dir / "journal.md"
                if journal_file.exists():
                    resources.append(f"  - `progress://{release}/{component}/{inc_dir.name}/journal` - {inc_dir.name} journal")
    
    resources.append("\n📖 **How to Read Resources**:")
    resources.append("Use ReadMcpResourceTool with:")
    resources.append('  - server: "memory-bank-kenoma"')
    resources.append('  - uri: one of the URIs listed above')
    
    return "\n".join(resources)


# Focus tools from mcp_focus
@mcp.tool(name="get-pm-focus")
def get_pm_focus(release: str, component: str, page: int = 1) -> str:
    """Get PM focus for component level."""
    from .mcp_focus import _generate_pm_focus, _pure_markdown_paginate
    
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ **Error**: Memory-Bank not bound to current project"
    
    try:
        state = ensure_component_state(memory_bank_path, release, component)
        current_increment = state.get("current_increment", "01")
        
        focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / current_increment / "pm-focus.md"
        
        if focus_file.exists():
            focus_content = focus_file.read_text()
        else:
            focus_content = _generate_pm_focus(memory_bank_path, release, component, current_increment)
            
            if focus_content:
                focus_file.parent.mkdir(parents=True, exist_ok=True)
                header = create_yaml_header(
                    datetime=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    increment=current_increment,
                    component=component,
                    release=release
                )
                focus_file.write_text(header + focus_content)
        
        if not focus_content:
            return "❌ **Error**: Failed to generate PM focus"
        
        return _pure_markdown_paginate(focus_content, page)
        
    except Exception as e:
        return f"❌ **Error**: Failed to get PM focus: {e}"


@mcp.tool(name="get-dev-focus")
def get_dev_focus(release: str, component: str, page: int = 1) -> str:
    """Get dev focus for current increment."""
    from .mcp_focus import _generate_dev_focus, _pure_markdown_paginate
    
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ **Error**: Memory-Bank not bound to current project"
    
    try:
        state = ensure_component_state(memory_bank_path, release, component)
        current_increment = state.get("current_increment", "01")
        
        focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / current_increment / "dev-focus.md"
        
        if focus_file.exists():
            focus_content = focus_file.read_text()
        else:
            focus_content = _generate_dev_focus(memory_bank_path, release, component, current_increment)
            
            if focus_content:
                focus_file.parent.mkdir(parents=True, exist_ok=True)
                header = create_yaml_header(
                    datetime=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    increment=current_increment,
                    component=component,
                    release=release
                )
                focus_file.write_text(header + focus_content)
        
        if not focus_content:
            return "❌ **Error**: Failed to generate dev focus"
        
        return _pure_markdown_paginate(focus_content, page)
        
    except Exception as e:
        return f"❌ **Error**: Failed to get dev focus: {e}"


@mcp.tool(name="get-tech-lead-focus")
def get_tech_lead_focus(release: str, component: str, page: int = 1) -> str:
    """Get tech-lead focus for current increment."""
    from .mcp_focus import _generate_tech_lead_focus, _pure_markdown_paginate
    
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ **Error**: Memory-Bank not bound to current project"
    
    try:
        state = ensure_component_state(memory_bank_path, release, component)
        current_increment = state.get("current_increment", "01")
        
        focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / current_increment / "tech-lead-focus.md"
        
        if focus_file.exists():
            focus_content = focus_file.read_text()
        else:
            focus_content = _generate_tech_lead_focus(memory_bank_path, release, component, current_increment)
            
            if focus_content:
                focus_file.parent.mkdir(parents=True, exist_ok=True)
                header = create_yaml_header(
                    datetime=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    increment=current_increment,
                    component=component,
                    release=release
                )
                focus_file.write_text(header + focus_content)
        
        if not focus_content:
            return "❌ **Error**: Failed to generate tech-lead focus"
        
        return _pure_markdown_paginate(focus_content, page)
        
    except Exception as e:
        return f"❌ **Error**: Failed to get tech-lead focus: {e}"


# ============================================================================
# RESOURCES - Static data access
# ============================================================================

@mcp.resource("progress://{release}/{component}/journal")
def get_journal(release: str, component: str) -> Dict[str, Any]:
    """Get journal for current increment."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    state_data = ensure_component_state(memory_bank_path, release, component)
    current_increment = state_data.get("current_increment", "01")
    increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
    
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
    
    if not journal_file.exists():
        return {
            "uri": f"progress://{release}/{component}/journal",
            "name": f"Journal - {component}/{increment_name}",
            "content": f"# Journal - {component}/{increment_name}\n\nNo entries yet.",
            "mime_type": "text/markdown"
        }
    
    try:
        content = journal_file.read_text()
        return {
            "uri": f"progress://{release}/{component}/journal",
            "name": f"Journal - {component}/{increment_name}",
            "content": content,
            "mime_type": "text/markdown"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("progress://{release}/{component}/{increment}/journal")
def get_increment_journal(release: str, component: str, increment: str) -> Dict[str, Any]:
    """Get journal for specific increment."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment / "journal.md"
    
    if not journal_file.exists():
        return {
            "uri": f"progress://{release}/{component}/{increment}/journal",
            "name": f"Journal - {component}/{increment}",
            "content": f"# Journal - {component}/{increment}\n\nNo entries yet.",
            "mime_type": "text/markdown"
        }
    
    try:
        content = journal_file.read_text()
        return {
            "uri": f"progress://{release}/{component}/{increment}/journal",
            "name": f"Journal - {component}/{increment}",
            "content": content,
            "mime_type": "text/markdown"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("architecture://{release}/{component}/component")
def get_component_spec(release: str, component: str) -> Dict[str, Any]:
    """Get component specification from architecture."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    spec_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
    
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
    """Get current increment details from implementation."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    state_data = ensure_component_state(memory_bank_path, release, component)
    current_increment = state_data.get("current_increment", "01")
    
    increment_pattern = f"{current_increment}*.md"
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
            "mime_type": "text/markdown"
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("progress://{release}/{component}/state")
def get_combined_state(release: str, component: str) -> Dict[str, Any]:
    """Get combined initial + progress state."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
    combined_content = f"# Combined State - {component}\n\n"
    
    # Load initial state
    initial_state_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "initial-state.md"
    if initial_state_file.exists():
        try:
            initial_content = initial_state_file.read_text()
            if initial_content.startswith('---\n'):
                yaml_end = initial_content.find('\n---\n', 4)
                if yaml_end != -1:
                    initial_content = initial_content[yaml_end + 5:]
            combined_content += "## Initial State\n\n" + initial_content + "\n\n"
        except:
            combined_content += "## Initial State\n\n*Unable to load initial state*\n\n"
    else:
        combined_content += "## Initial State\n\n*No initial state defined*\n\n"
    
    # Load progress state
    progress_state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "progress-state.md"
    if progress_state_file.exists():
        try:
            progress_content = progress_state_file.read_text()
            state_data = safe_load_yaml(progress_state_file)
            
            if progress_content.startswith('---\n'):
                yaml_end = progress_content.find('\n---\n', 4)
                if yaml_end != -1:
                    progress_content = progress_content[yaml_end + 5:]
            
            combined_content += "## Progress State\n\n"
            combined_content += f"**Current Increment**: {state_data.get('current_increment', 'unknown')}\n"
            combined_content += f"**Status**: {state_data.get('status', 'unknown')}\n"
            combined_content += f"**Last Updated**: {state_data.get('datetime', 'unknown')}\n\n"
            combined_content += progress_content
        except:
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
def get_tech_context_file(filename: str) -> Dict[str, Any]:
    """Get specific tech-context file."""
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return {"error": "Memory-Bank not bound"}
    
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


@mcp.resource("memory-bank://resource-guide")
def get_resource_guide() -> Dict[str, Any]:
    """Static resource guide for Memory Bank."""
    return {
        "uri": "memory-bank://resource-guide",
        "name": "Memory Bank Resource Guide",
        "content": """# Memory Bank Resource Guide

## Available Resources

### Progress Resources
- `progress://{release}/{component}/journal` - Current increment journal
- `progress://{release}/{component}/{increment}/journal` - Specific increment journal
- `progress://{release}/{component}/state` - Combined state

### Architecture Resources
- `architecture://{release}/{component}/component` - Component specification
- `architecture://tech-context/{filename}` - Tech context files

### Todo Resources
- `todo://{release}/{component}/increment` - Current increment details

## Usage
Use ReadMcpResourceTool with server="memory-bank-kenoma" and the URI.
""",
        "mime_type": "text/markdown"
    }


# ============================================================================
# SERVER RUNNER
# ============================================================================

def run_memory_bank_mcp_server():
    """Run Memory-Bank MCP server with stdio transport."""
    print(f"Memory-Bank MCP starting from: {Path.cwd()}", file=sys.stderr)
    
    memory_bank_path = get_memory_bank_path()
    if memory_bank_path:
        print(f"Found Memory-Bank at: {memory_bank_path}", file=sys.stderr)
    else:
        print("No Memory-Bank binding found", file=sys.stderr)
    
    try:
        mcp.run()
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