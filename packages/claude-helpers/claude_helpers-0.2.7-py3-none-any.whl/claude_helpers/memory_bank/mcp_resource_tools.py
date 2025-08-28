"""MCP Tools for Memory Bank resource access - workaround for sub-agents.

This module provides MCP tools that emulate resource API functionality,
allowing sub-agents to list and read Memory Bank resources.
"""

import re
from pathlib import Path
from typing import Optional, Dict, Any
from fastmcp import FastMCP

from .mcp_utils import (
    get_memory_bank_path,
    paginate_content,
    safe_load_yaml
)
from .increment_utils import (
    ensure_component_state,
    get_full_increment_name
)


# Create MCP server instance for resource tools
mcp = FastMCP("Memory-Bank Resource Tools")


def generate_resource_guide():
    """Generate a generic resource guide without hardcoded values."""
    return """# Memory Bank Resource Guide 🗂️

## Static Resources (Always Available)
These resources are always accessible and don't require parameters:

### Architecture Context
- `architecture://tech-context/list` - List all tech-context files
- `architecture://tech-context/{filename}` - Read specific tech file
  - Examples: tech-stack.md, code-standards.md, testing-standards.md

## Dynamic Resources (Template-Based)
These resources require parameters in the URI. Replace {parameter} with actual values:

### Component Resources
- `architecture://{release}/{component}/component` - Component specification

### Task Resources  
- `todo://{release}/{component}/increment` - Current increment details
- `todo://{release}/{component}/decomposition` - Task decomposition

### Progress Resources
- `progress://{release}/{component}/journal` - Current increment journal
- `progress://{release}/{component}/state` - Combined progress state  

### Specific Increment Journals
- `progress://{release}/{component}/{increment}/journal` - Specific increment journal

## How to Use

### For Static Resources
Simply use the URI as shown:
```
read-memory-bank-resource(uri="architecture://tech-context/tech-stack.md", page=1)
```

### For Dynamic Resources
Replace {parameter} placeholders with your actual values:
```
read-memory-bank-resource(uri="architecture://your-release/your-component/component", page=1)
read-memory-bank-resource(uri="progress://your-release/your-component/journal", page=1)
```

## Usage Tips
1. **Start with static resources** like `architecture://tech-context/list` to discover content
2. **Replace parameters** in template URIs with your actual release/component/increment values
3. **All resources support UTF-8/Cyrillic** text properly

## Tools Available
Use these MCP tools for additional functionality:
- `journal-note` - Add entries to current increment journal
- `ask-memory-bank` - Query Memory Bank content intelligently  
- `get-pm-focus`, `get-dev-focus`, `get-tech-lead-focus` - Get role-specific focus
- `next-increment` - Move to next increment when current is complete"""


@mcp.tool("list-memory-bank-resources")
def list_memory_bank_resources() -> str:
    """List all available Memory Bank resources (workaround for sub-agents).
    
    This tool provides a complete resource guide for sub-agents
    who cannot use MCP Resources API directly.
    
    Returns:
        Universal resource guide with URIs, patterns and instructions
    """
    # Use the common resource guide function
    guide_content = generate_resource_guide()
    
    output = []
    output.append("# 📚 Available Memory Bank Resources (Sub-Agent Access)\n")
    output.append("**Note**: Since you're a sub-agent, use these MCP tools instead of direct resource access:\n")
    output.append("- `list-memory-bank-resources()` - List available resources")
    output.append("- `read-memory-bank-resource(uri, page)` - Read resources with pagination\n")
    
    # Add the actual resource guide
    output.append("## Complete Resource Guide\n")
    output.append(guide_content)
    
    output.append("\n## 📖 How to Read Resources\n")
    output.append("Use the `read-memory-bank-resource` tool:")
    output.append("```python")
    output.append('read-memory-bank-resource(uri="<resource_uri>", page=1)')
    output.append("```")
    output.append("")
    output.append("⚠️ **IMPORTANT**: Always check for pagination!")
    output.append("- Look for **PAGE X OF Y** markers")
    output.append("- If you see **CONTENT CONTINUES**, read next pages")
    output.append("- You MUST read ALL pages for complete context")
    
    return "\n".join(output)


def parse_resource_uri(uri: str) -> Dict[str, Any]:
    """Parse resource URI into components.
    
    Args:
        uri: Resource URI (e.g. "architecture://tech-context/code-standards.md")
        
    Returns:
        Dict with parsed components
    """
    # Basic URI pattern: scheme://path
    match = re.match(r"^([^:]+)://(.+)$", uri)
    if not match:
        return {"error": f"Invalid URI format: {uri}"}
    
    scheme = match.group(1)
    path = match.group(2)
    
    result = {
        "scheme": scheme,
        "path": path,
        "parts": path.split("/")
    }
    
    # Parse based on scheme
    if scheme == "architecture":
        if path.startswith("tech-context/"):
            result["type"] = "tech-context"
            result["filename"] = path[len("tech-context/"):]
        else:
            # Pattern: release/component/component
            parts = path.split("/")
            if len(parts) >= 3:
                result["type"] = "component"
                result["release"] = parts[0]
                result["component"] = parts[1]
    
    elif scheme == "progress":
        # Pattern: release/component/journal or release/component/increment/journal
        parts = path.split("/")
        if len(parts) >= 3:
            result["type"] = "progress"
            result["release"] = parts[0]
            result["component"] = parts[1]
            if len(parts) == 3:
                result["resource"] = parts[2]  # journal or state
            elif len(parts) == 4:
                result["increment"] = parts[2]
                result["resource"] = parts[3]  # journal
    
    elif scheme == "todo":
        # Pattern: release/component/resource
        parts = path.split("/")
        if len(parts) >= 3:
            result["type"] = "todo"
            result["release"] = parts[0]
            result["component"] = parts[1]
            result["resource"] = parts[2]  # increment or decomposition
    
    elif scheme == "memory-bank":
        result["type"] = "memory-bank"
        result["resource"] = path
    
    return result


@mcp.tool("read-memory-bank-resource")
def read_memory_bank_resource(uri: str, page: int = 1) -> str:
    """Read Memory Bank resource by URI with pagination (workaround for sub-agents).
    
    This tool provides paginated access to Memory Bank resources for sub-agents
    who cannot use MCP Resources API directly.
    
    Args:
        uri: Resource URI (e.g. "architecture://tech-context/code-standards.md")
        page: Page number for paginated content (default: 1)
        
    Returns:
        Resource content with clear pagination markers and instructions
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ Error: Memory-Bank not bound to project. Run 'claude-helpers memory-bank init' first."
    
    # Parse URI
    parsed = parse_resource_uri(uri)
    if "error" in parsed:
        return f"❌ Error: {parsed['error']}"
    
    # Get resource content based on type - DIRECTLY without calling MCP resources
    content = None
    resource_name = uri
    
    try:
        if parsed["scheme"] == "architecture":
            if parsed["type"] == "tech-context":
                if parsed["filename"] == "list":
                    # List tech-context files directly
                    tech_context_dir = memory_bank_path / "architecture" / "tech-context"
                    if tech_context_dir.exists():
                        content_lines = ["# Available Tech Context Files\n"]
                        for file_path in sorted(tech_context_dir.glob("*.md")):
                            try:
                                file_size = file_path.stat().st_size
                                name = file_path.stem.replace("-", " ").title()
                                content_lines.append(f"- `architecture://tech-context/{file_path.name}` - {name} ({file_size // 1024}KB)")
                            except Exception:
                                continue
                        content = "\n".join(content_lines)
                        resource_name = "Tech Context Files List"
                    else:
                        return "❌ Error: No tech-context directory found"
                else:
                    # Read specific tech-context file
                    filename = parsed["filename"]
                    if not filename.endswith('.md'):
                        filename += '.md'
                    file_path = memory_bank_path / "architecture" / "tech-context" / filename
                    if file_path.exists():
                        content = file_path.read_text()
                        resource_name = file_path.stem.replace("-", " ").title()
                    else:
                        return f"❌ Error: Tech context file {filename} not found"
            
            elif parsed["type"] == "component":
                # Read component specification directly
                release = parsed["release"]
                component = parsed["component"]
                spec_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
                if not spec_file.exists():
                    spec_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "component.md"
                if spec_file.exists():
                    content = spec_file.read_text()
                    resource_name = f"{component} Specification"
                else:
                    return f"❌ Error: Component specification not found for {component}"
        
        elif parsed["scheme"] == "progress":
            release = parsed.get("release")
            component = parsed.get("component")
            
            if parsed.get("increment"):
                # Specific increment journal
                increment = parsed["increment"]
                journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment / "journal.md"
                if journal_file.exists():
                    content = journal_file.read_text()
                    resource_name = f"Journal - {component}/{increment}"
                else:
                    content = f"# Journal - {component}/{increment}\n\nNo entries yet."
                    resource_name = f"Journal - {component}/{increment}"
                    
            elif parsed.get("resource") == "state":
                # Combined state
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
                    except Exception:
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
                    except Exception:
                        combined_content += "## Progress State\n\n*Unable to load progress state*\n\n"
                else:
                    combined_content += "## Progress State\n\n*No progress recorded*\n\n"
                    
                content = combined_content
                resource_name = f"{component} Combined State"
                
            else:
                # Current increment journal
                state_data = ensure_component_state(memory_bank_path, release, component)
                current_increment = state_data.get("current_increment", "01")
                increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
                journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
                
                if journal_file.exists():
                    content = journal_file.read_text()
                    resource_name = f"Journal - {component}/{current_increment}"
                else:
                    content = f"# Journal - {component}/{increment_name}\n\nNo entries yet."
                    resource_name = f"Journal - {component}/{increment_name}"
        
        elif parsed["scheme"] == "todo":
            release = parsed.get("release")
            component = parsed.get("component")
            
            if parsed.get("resource") == "increment":
                # Current increment
                state_data = ensure_component_state(memory_bank_path, release, component)
                current_increment = state_data.get("current_increment", "01")
                increment_pattern = f"{current_increment}-*.md"
                increment_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "increments"
                
                if increment_dir.exists():
                    increment_files = list(increment_dir.glob(increment_pattern))
                    if increment_files:
                        content = increment_files[0].read_text()
                        resource_name = f"Current Increment: {increment_files[0].stem}"
                    else:
                        return f"❌ Error: Increment {current_increment} not found"
                else:
                    return f"❌ Error: No increments found for {component}"
                    
            elif parsed.get("resource") == "decomposition":
                # Decomposition
                decomposition_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "decomposition.md"
                if decomposition_file.exists():
                    content = decomposition_file.read_text()
                    resource_name = f"{component} Decomposition"
                else:
                    return f"❌ Error: Decomposition not found for {component}"
            else:
                return f"❌ Error: Unknown todo resource: {parsed.get('resource')}"
        
        elif parsed["scheme"] == "memory-bank":
            if parsed["resource"] == "resource-guide":
                # Use the common resource guide function
                content = generate_resource_guide()
                resource_name = "Memory Bank Resource Guide"
            else:
                return f"❌ Error: Unknown memory-bank resource: {parsed['resource']}"
        
        else:
            return f"❌ Error: Unknown URI scheme: {parsed['scheme']}"
        
    except Exception as e:
        return f"❌ Error reading resource: {str(e)}"
    
    if not content:
        return f"❌ Error: Resource not found or empty: {uri}"
    
    # Apply pagination with clear instructions
    paginated = paginate_content(content, page, page_size_tokens=5000)
    
    # Format output with clear navigation
    output = []
    
    # Add header with page info
    if paginated["pagination"]["total_pages"] > 1:
        output.append(f"📄 **PAGE {paginated['pagination']['current_page']} OF {paginated['pagination']['total_pages']}**")
        output.append(f"📚 **Resource**: {resource_name}")
        output.append(f"🔗 **URI**: `{uri}`")
        output.append("")
        output.append("---")
        output.append("")
    else:
        output.append(f"📚 **Resource**: {resource_name}")
        output.append(f"🔗 **URI**: `{uri}`")
        output.append("")
        output.append("---")
        output.append("")
    
    # Add content
    output.append(paginated["content"])
    
    # Add navigation footer if needed
    if paginated["pagination"]["has_more"]:
        output.append("")
        output.append("---")
        output.append("")
        output.append("⚠️ **CONTENT CONTINUES**")
        output.append(f"📖 To read page {page + 1}, call:")
        output.append(f"```")
        output.append(f'read-memory-bank-resource(uri="{uri}", page={page + 1})')
        output.append(f"```")
        output.append(f"❗ You **MUST** read ALL {paginated['pagination']['total_pages']} pages to get the complete context!")
    elif paginated["pagination"]["total_pages"] > 1:
        output.append("")
        output.append("---")
        output.append("")
        output.append(f"✅ **END OF DOCUMENT** (Page {page} of {paginated['pagination']['total_pages']})")
    
    # Handle error case
    if "error" in paginated["pagination"]:
        output = [f"❌ Error: {paginated['pagination']['error']}"]
        output.append("")
        output.append(f"💡 Try: `read-memory-bank-resource(uri=\"{uri}\", page=1)`")
    
    return "\n".join(output)