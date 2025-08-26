"""MCP Tools for generating role-based focus documents."""

import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
from fastmcp import FastMCP

from .mcp_utils import (
    get_memory_bank_path,
    get_working_directory,
    load_template
)
from .increment_utils import (
    ensure_component_state,
    get_increment_details,
    get_full_increment_name
)


# Create MCP server instance for focus tools
mcp = FastMCP("Memory-Bank Focus")


@mcp.tool(name="get-pm-focus")
def get_pm_focus(release: str, component: str, page: int = 1) -> str:
    """Get PM focus for component level.
    
    Args:
        release: Release name
        component: Component name
        page: Page number for pagination
        
    Returns:
        Pure markdown string with pagination markers
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ **Error**: Memory-Bank not bound to current project"
    
    try:
        # Ensure component state exists
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        
        # Get full increment name for path
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        # Check if focus file exists
        # PM focus is in increment folder alongside journal
        focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "pm-focus.md"
        
        if focus_file.exists():
            # Return existing focus with pure markdown pagination
            content = focus_file.read_text()
            return _pure_markdown_paginate(content, page)
        
        # Generate new focus
        focus_content = _generate_pm_focus(memory_bank_path, release, component, current_increment)
        
        if focus_content:
            # Save generated focus
            focus_file.parent.mkdir(parents=True, exist_ok=True)
            focus_file.write_text(focus_content)
            
            # Return with pure markdown pagination
            return _pure_markdown_paginate(focus_content, page)
        
        return "❌ **Error**: Failed to generate PM focus"
        
    except Exception as e:
        return f"❌ **Error**: Error getting PM focus: {e}"


@mcp.tool(name="get-dev-focus")
def get_dev_focus(release: str, component: str, page: int = 1) -> str:
    """Get dev focus for current increment.
    
    Args:
        release: Release name
        component: Component name
        page: Page number for pagination
        
    Returns:
        Pure markdown string with pagination markers
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ **Error**: Memory-Bank not bound to current project"
    
    try:
        # Ensure component state exists
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        
        # Get full increment name for path
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        # Check if focus file exists
        # Dev focus is in increment folder alongside journal
        focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "dev-focus.md"
        
        if focus_file.exists():
            # Return existing focus with pure markdown pagination
            content = focus_file.read_text()
            return _pure_markdown_paginate(content, page)
        
        # Generate new focus
        focus_content = _generate_dev_focus(memory_bank_path, release, component, current_increment)
        
        if focus_content:
            # Save generated focus
            focus_file.parent.mkdir(parents=True, exist_ok=True)
            focus_file.write_text(focus_content)
            
            # Return with pure markdown pagination
            return _pure_markdown_paginate(focus_content, page)
        
        return "❌ **Error**: Failed to generate dev focus"
        
    except Exception as e:
        return f"❌ **Error**: Error getting dev focus: {e}"


@mcp.tool(name="get-tech-lead-focus")
def get_tech_lead_focus(release: str, component: str, page: int = 1) -> str:
    """Get tech-lead focus for current increment.
    
    Args:
        release: Release name
        component: Component name
        page: Page number for pagination
        
    Returns:
        Pure markdown string with pagination markers
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return "❌ **Error**: Memory-Bank not bound to current project"
    
    try:
        # Ensure component state exists
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        
        # Get full increment name for path
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        # Check if focus file exists
        # Tech-lead focus is in increment folder alongside journal
        focus_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "tech-lead-focus.md"
        
        if focus_file.exists():
            # Return existing focus with pure markdown pagination
            content = focus_file.read_text()
            return _pure_markdown_paginate(content, page)
        
        # Generate new focus
        focus_content = _generate_tech_lead_focus(memory_bank_path, release, component, current_increment)
        
        if focus_content:
            # Save generated focus
            focus_file.parent.mkdir(parents=True, exist_ok=True)
            focus_file.write_text(focus_content)
            
            # Return with pure markdown pagination
            return _pure_markdown_paginate(focus_content, page)
        
        return "❌ **Error**: Failed to generate tech-lead focus"
        
    except Exception as e:
        return f"❌ **Error**: Error getting tech-lead focus: {e}"


def _generate_pm_focus(memory_bank_path: Path, release: str, component: str, increment: str) -> Optional[str]:
    """Generate PM focus using formula and template.
    
    Formula: distilled_product + component + decomposition + state
    """
    try:
        # Get product context (vision + release)
        product_context = _get_product_context(memory_bank_path, release)
        
        # Load component content (from architecture, not implementation)
        component_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
        component_content = component_file.read_text() if component_file.exists() else "Component specification not found"
        
        # Load decomposition
        decomposition_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "decomposition.md"
        decomposition_content = decomposition_file.read_text() if decomposition_file.exists() else "Decomposition not found"
        
        # Load combined state
        state_content = _get_combined_state(memory_bank_path, release, component)
        
        # Load PM focus template
        template = load_template("progress/pm-focus.md", memory_bank_path)
        if not template:
            # Fallback template
            template = """---
datetime: "{datetime}"
increment: "{increment}"
component: "{component}"
release: "{release}"
---

## Product/Release Context

{product_context}

---

## Current Component

```md
{current_component_content}
```

## Decomposition

```md
{decomposition_content}
```

## State

```md
{current_component_state_content}
```

## Your Role

You are the Product Manager (PM) orchestrating the implementation of this component.
Your responsibilities:
- Coordinate between owner and development team
- Ensure increment objectives are met
- Manage workflow transitions between roles
- Track progress and report to owner
"""
        
        # Format template
        datetime_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Replace both old and new placeholder names
        focus_content = template.format(
            datetime=datetime_str,
            increment=increment,
            component=component,
            release=release,
            product_context=product_context,  # New name
            destill_overview_of_product_and_current_release=product_context,  # Keep old name for compatibility
            current_component_content=component_content,
            decomposition_content=decomposition_content,
            current_component_state_content=state_content
        )
        
        return focus_content
        
    except Exception as e:
        print(f"Error generating PM focus: {e}")
        return None


def _generate_dev_focus(memory_bank_path: Path, release: str, component: str, increment: str) -> Optional[str]:
    """Generate dev focus using formula and template.
    
    Formula: distilled_product + component + increment + state
    """
    try:
        # Get product context (vision + release)
        product_context = _get_product_context(memory_bank_path, release)
        
        # Load component content (from architecture, not implementation)
        component_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
        component_content = component_file.read_text() if component_file.exists() else "Component specification not found"
        
        # Load current increment content
        # Extract increment number if it's a full name (e.g., "02-configuration-and-exceptions" -> "02")
        increment_id = increment.split('-')[0] if '-' in increment else increment
        increment_details = get_increment_details(memory_bank_path, release, component, increment_id)
        if increment_details and "filename" in increment_details:
            # Load actual increment file content
            increment_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "increments" / increment_details["filename"]
            try:
                increment_content = increment_file.read_text()
            except Exception:
                increment_content = "Increment file not found"
        else:
            increment_content = "Increment not found"
        
        # Load combined state
        state_content = _get_combined_state(memory_bank_path, release, component)
        
        # Load dev focus template
        template = load_template("progress/dev-focus.md", memory_bank_path)
        if not template:
            # Fallback template
            template = """---
datetime: "{datetime}"
increment: "{increment}"
component: "{component}"
release: "{release}"
---

## Your Role

You are the Developer implementing this increment.
Your responsibilities:
- Implement the increment requirements
- Write clean, maintainable code
- Follow project standards and conventions
- Document your implementation decisions in journal

## Product/Release Context

{destill_overview_of_product_and_release_by_increment_context}

---

## Component

```md
{component_content}
```

## Increment (Your current task)

```md
{increment_content}
```

## State

```md
{combined_initial_state_plus_progress_state}
```
"""
        
        # Format template
        datetime_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        focus_content = template.format(
            datetime=datetime_str,
            increment=increment,
            component=component,
            release=release,
            destill_overview_of_product_and_release_by_increment_context=product_context,  # Keep old name for compatibility
            component_content=component_content,
            increment_content=increment_content,
            combined_initial_state_plus_progress_state=state_content
        )
        
        return focus_content
        
    except Exception as e:
        print(f"Error generating dev focus: {e}")
        return None


def _generate_tech_lead_focus(memory_bank_path: Path, release: str, component: str, increment: str) -> Optional[str]:
    """Generate tech-lead focus using formula and template.
    
    Formula: distilled_product + component + increment + state
    """
    try:
        # Get product context (vision + release)
        product_context = _get_product_context(memory_bank_path, release)
        
        # Load component content (from architecture, not implementation)
        component_file = memory_bank_path / "architecture" / "releases" / release / "components" / f"{component}.md"
        component_content = component_file.read_text() if component_file.exists() else "Component specification not found"
        
        # Load current increment content
        # Extract increment number if it's a full name (e.g., "02-configuration-and-exceptions" -> "02")
        increment_id = increment.split('-')[0] if '-' in increment else increment
        increment_details = get_increment_details(memory_bank_path, release, component, increment_id)
        if increment_details and "filename" in increment_details:
            # Load actual increment file content
            increment_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "increments" / increment_details["filename"]
            try:
                increment_content = increment_file.read_text()
            except Exception:
                increment_content = "Increment file not found"
        else:
            increment_content = "Increment not found"
        
        # Load combined state
        state_content = _get_combined_state(memory_bank_path, release, component)
        
        # Load tech-lead focus template
        template = load_template("progress/tech-lead-focus.md", memory_bank_path)
        if not template:
            # Fallback template
            template = """---
datetime: "{datetime}"
increment: "{increment}"
component: "{component}"
release: "{release}"
---

## Your Role

You are the Tech Lead reviewing this increment implementation.
Your responsibilities:
- Validate implementation against requirements
- Ensure code quality and standards compliance
- Check for potential issues and edge cases
- Provide constructive feedback

## Product/Release Context

{product_context}

---

## Component

```md
{component_content}
```

## Increment (Implementation to review)

```md
{increment_content}
```

## State

```md
{combined_initial_state_plus_progress_state}
```
"""
        
        # Format template
        datetime_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        focus_content = template.format(
            datetime=datetime_str,
            increment=increment,
            component=component,
            release=release,
            destill_overview_of_product_and_release_by_increment_context=product_context,  # Keep old name for compatibility
            component_content=component_content,
            increment_content=increment_content,
            combined_initial_state_plus_progress_state=state_content
        )
        
        return focus_content
        
    except Exception as e:
        print(f"Error generating tech-lead focus: {e}")
        return None


def _get_combined_state(memory_bank_path: Path, release: str, component: str) -> str:
    """Get combined initial + progress state with metadata preserved."""
    combined = ""
    
    # Load initial state
    initial_state_file = memory_bank_path / "implementation" / "releases" / release / "components" / component / "initial-state.md"
    if initial_state_file.exists():
        try:
            content = initial_state_file.read_text()
            # Remove YAML header if present
            if content.startswith('---\n'):
                yaml_end = content.find('\n---\n', 4)
                if yaml_end != -1:
                    content = content[yaml_end + 5:]
            combined += "### Initial State\n\n" + content + "\n\n"
        except Exception:
            combined += "### Initial State\n\n*Unable to load initial state*\n\n"
    
    # Load progress state WITH metadata
    progress_state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "progress-state.md"
    if progress_state_file.exists():
        try:
            content = progress_state_file.read_text()
            yaml_metadata = None
            
            # Extract YAML metadata before removing it
            if content.startswith('---\n'):
                yaml_end = content.find('\n---\n', 4)
                if yaml_end != -1:
                    yaml_content = content[4:yaml_end]
                    content = content[yaml_end + 5:]
                    
                    # Parse YAML to extract key metadata
                    import yaml
                    try:
                        metadata = yaml.safe_load(yaml_content)
                        if metadata:
                            # Format metadata for inclusion in state
                            yaml_metadata = "**Current State Metadata:**\n"
                            if 'current_increment' in metadata:
                                yaml_metadata += f"- Current Increment: `{metadata['current_increment']}`\n"
                            if 'status' in metadata:
                                yaml_metadata += f"- Status: `{metadata['status']}`\n"
                            if 'datetime' in metadata:
                                yaml_metadata += f"- Last Updated: `{metadata['datetime']}`\n"
                            yaml_metadata += "\n"
                    except Exception:
                        pass  # If YAML parsing fails, continue without metadata
            
            combined += "### Progress State\n\n"
            if yaml_metadata:
                combined += yaml_metadata
            combined += content
        except Exception:
            combined += "### Progress State\n\n*Unable to load progress state*"
    else:
        combined += "### Progress State\n\n*No progress recorded yet*"
    
    return combined


def _optimized_paginate(content: str, page: int) -> dict:
    """Paginate content and return minimal JSON with just content and page info.
    
    Returns dict with:
    - c: content (using short key to minimize JSON size)
    - p: current page 
    - t: total pages
    """
    if not content or not content.strip():
        return {"c": "", "p": 1, "t": 1}
    
    # Use 20K chars per page (5K tokens * 4)
    chars_per_page = 20000
    
    # Split content by logical boundaries (markdown headers)
    import re
    sections = re.split(r'\n(?=##? )', content)
    
    # Rebuild sections with proper formatting
    formatted_sections = []
    for i, section in enumerate(sections):
        if i == 0:
            formatted_sections.append(section)
        else:
            formatted_sections.append('\n' + section)
    
    # Group sections into pages
    pages = []
    current_page_content = ""
    
    for section in formatted_sections:
        if len(current_page_content + section) > chars_per_page and current_page_content:
            pages.append(current_page_content.strip())
            current_page_content = section
        else:
            current_page_content += section
    
    # Add the last page
    if current_page_content.strip():
        pages.append(current_page_content.strip())
    
    if not pages:
        pages = [""]
    
    total_pages = len(pages)
    
    # Handle page bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        return {"error": f"Page {page} does not exist. Total: {total_pages}"}
    
    page_content = pages[page - 1]
    
    # Add minimal pagination markers at start and end
    if total_pages > 1:
        header = f"[Page {page}/{total_pages}]\n\n"
        footer = f"\n\n[Page {page}/{total_pages}]"
        if page < total_pages:
            footer += f" - Continue with page={page + 1}"
        page_content = header + page_content + footer
    
    return {
        "c": page_content,  # content
        "p": page,         # page
        "t": total_pages   # total
    }


def _pure_markdown_paginate(content: str, page: int) -> str:
    """Paginate content and return pure markdown string with clear markers.
    
    Returns pure markdown with:
    - Clear page indicator at start
    - Content
    - Continuation hint at end if more pages exist
    """
    if not content or not content.strip():
        return "<!-- Empty content -->\n"
    
    # Pure markdown = 4 chars per token, use 20K chars per page (5K tokens)
    # Reserve ~100 chars for pagination markers
    chars_per_page = 19900
    
    # Split content by major sections (## headers)
    import re
    # Match lines that start with ## (not ###)
    lines = content.split('\n')
    sections = []
    current_section = []
    in_first_section = True  # Track if we're still in the document header/intro
    
    for line in lines:
        # Start new section on ## headers (major sections)
        # But don't split on the first ## we encounter (keep header with first section)
        if line.strip().startswith('## '):
            if in_first_section:
                # Keep header/intro with first real section
                in_first_section = False
                current_section.append(line)
            elif current_section:
                # Start new section
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        else:
            current_section.append(line)
    
    # Add the last section
    if current_section:
        sections.append('\n'.join(current_section))
    
    # If no sections or content is small, treat as single section
    if not sections or len(content) < chars_per_page:
        sections = [content]
    
    # Group sections into pages
    pages = []
    current_page_content = ""
    
    for section in sections:
        # If adding this section would exceed page limit AND we have content already
        if len(current_page_content) + len(section) + 1 > chars_per_page and current_page_content:
            pages.append(current_page_content.strip())
            current_page_content = section
        else:
            # Add section to current page
            if current_page_content:
                current_page_content += "\n" + section
            else:
                current_page_content = section
    
    # Add the last page if it has content
    if current_page_content.strip():
        pages.append(current_page_content.strip())
    
    # If no pages were created (shouldn't happen), use original content
    if not pages:
        pages = [content]
    
    total_pages = len(pages)
    
    # Handle page bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        return f"❌ **Error**: Page {page} does not exist. Total pages: {total_pages}\n"
    
    page_content = pages[page - 1]
    
    # Build result with clear pagination markers
    result = f"📄 **Page {page} of {total_pages}**\n\n"
    result += "---\n\n"
    result += page_content
    
    if page < total_pages:
        result += f"\n\n---\n\n⚠️ **CONTENT CONTINUES** - Use `page={page + 1}` to read the next page"
    else:
        result += f"\n\n---\n\n✅ **END OF DOCUMENT** - This is the last page ({page} of {total_pages})"
    
    return result


def _paginate_with_minimal_markers(content: str, page: int, role: str, component: str, increment: str) -> str:
    """Paginate content and return pure markdown with minimal markers.
    
    Instead of JSON with embedded content, returns pure markdown with:
    - Pagination info as a single line comment at the top
    - Content
    - Navigation hint at the bottom if more pages exist
    """
    if not content or not content.strip():
        return "<!-- Empty content -->\n"
    
    # Use smaller page size to account for NO JSON overhead
    # Pure markdown = 4 chars per token
    chars_per_page = int(5000 * 4)  # 20K chars = 5K tokens
    
    # Split content by logical boundaries (markdown headers)
    import re
    sections = re.split(r'\n(?=##? )', content)
    
    # Rebuild sections with proper formatting
    formatted_sections = []
    for i, section in enumerate(sections):
        if i == 0:
            formatted_sections.append(section)
        else:
            formatted_sections.append('\n' + section)
    
    # Group sections into pages
    pages = []
    current_page_content = ""
    
    for section in formatted_sections:
        if len(current_page_content + section) > chars_per_page and current_page_content:
            pages.append(current_page_content.strip())
            current_page_content = section
        else:
            current_page_content += section
    
    # Add the last page
    if current_page_content.strip():
        pages.append(current_page_content.strip())
    
    if not pages:
        pages = [""]
    
    total_pages = len(pages)
    
    # Handle page bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        return f"<!-- Page {page} does not exist. Total pages: {total_pages} -->\n"
    
    page_content = pages[page - 1]
    
    # Build result with minimal markers
    result = f"<!-- Page {page}/{total_pages} | Role: {role} | Component: {component} | Increment: {increment} -->\n\n"
    result += page_content
    
    if page < total_pages:
        result += f"\n\n---\n<!-- To continue reading, call this function with page={page + 1} -->"
    else:
        result += f"\n\n---\n<!-- End of document (page {total_pages}) -->"
    
    return result


def _get_product_context(memory_bank_path: Path, release: str) -> str:
    """Get product context for focus documents.
    
    Loads actual product vision and release information from Memory Bank.
    """
    try:
        # Load product vision
        vision_file = memory_bank_path / "product" / "vision.md"
        if vision_file.exists():
            vision_content = vision_file.read_text()
            # Extract key sections (first 1000 chars or until first ## section)
            lines = vision_content.split('\n')
            vision_summary = []
            for line in lines:
                if line.startswith('## ') and len(vision_summary) > 5:
                    break
                vision_summary.append(line)
                if len('\n'.join(vision_summary)) > 1000:
                    break
            vision_text = '\n'.join(vision_summary).strip()
        else:
            vision_text = "**Kenoma** - AI-powered knowledge unification platform for fragmented digital workflows."
        
        # Load release information
        release_file = memory_bank_path / "product" / "releases" / f"{release}.md"
        if release_file.exists():
            release_content = release_file.read_text()
            # Extract key sections (first 800 chars or until decomposition section)
            lines = release_content.split('\n')
            release_summary = []
            for line in lines:
                if line.startswith('## Decomposition'):
                    break
                release_summary.append(line)
                if len('\n'.join(release_summary)) > 800:
                    break
            release_text = '\n'.join(release_summary).strip()
        else:
            release_text = f"**Release {release}** - Component implementation milestone."
        
        # Combine into product context (without header as template provides it)
        return f"""{vision_text}

---

### Current Release: {release}

{release_text}

*Full documentation available in Memory Bank product/ directory*
"""
    except Exception as e:
        # Fallback to minimal version (without header as template provides it)
        return f"""**Kenoma** - AI-powered knowledge unification platform for fragmented digital workflows.
**Release {release}** - Component implementation milestone.

*Full documentation available in Memory Bank product/ directory*
"""

