"""MCP Tools for Memory Bank - active operations."""

import json
import yaml
from pathlib import Path
from datetime import datetime, timezone
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
from .increment_models import IncrementJournalEntry


# Create MCP server instance for tools
mcp = FastMCP("Memory-Bank Tools")


@mcp.tool(name="journal-note")
def journal_note(release: str, component: str, role: str, message: str) -> str:
    """Add journal entry for current increment.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        role: Agent role (dev/owner/pm/tech-lead)
        message: Journal note content
        
    Returns:
        JSON confirmation of journal entry creation
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return format_error_response("Memory-Bank not bound to current project")
    
    try:
        # Ensure component state exists
        state_data = ensure_component_state(memory_bank_path, release, component)
        current_increment = state_data.get("current_increment", "01")
        
        # Ensure increment structure exists (this will get full name)
        create_increment_structure(memory_bank_path, release, component, current_increment)
        
        # Get full increment name for journal path - use the helper function
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        # Get journal file path with full increment name
        journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
        
        # Ensure parent directories exist
        journal_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.now(timezone.utc)
        datetime_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Format journal entry
        entry = f"\n## {datetime_str} - {role}\n\n{message}\n"
        
        # If journal doesn't exist, create with header
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
            # Append to existing journal
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
    """Move to next increment within component.
    
    This triggers the implementation overview generation for the completed increment
    and updates the state to the next increment.
    
    Args:
        release: Release name (e.g. "01-pre-alpha")
        component: Component name (e.g. "01-core-api")
        
    Returns:
        JSON with next increment information
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return format_error_response("Memory-Bank not bound to current project")
    
    try:
        # Ensure component state and get current data
        state_data = ensure_component_state(memory_bank_path, release, component)
        state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "progress-state.md"
        
        current_increment = state_data.get("current_increment", "01")
        
        # Get full increment name
        increment_name = get_full_increment_name(memory_bank_path, release, component, current_increment)
        
        # Generate progress-state section using Claude Code SDK
        try:
            # Try to use Claude SDK for intelligent analysis
            overview = await _generate_progress_state_with_sdk(memory_bank_path, release, component, current_increment)
        except ImportError:
            # Claude SDK not available, use fallback
            overview = _get_journal_content_as_overview(memory_bank_path, release, component, increment_name)
        except Exception as e:
            # Any other error, use fallback with warning
            print(f"Warning: SDK generation failed ({e}), using fallback")
            overview = _get_journal_content_as_overview(memory_bank_path, release, component, increment_name)
        
        # Update progress-state with overview - just append to the end
        if state_file.exists():
            content = state_file.read_text()
            
            # The overview from SDK already contains the properly formatted section
            # starting with ## {increment_name}, so we just append it
            
            # Ensure proper spacing
            content = content.rstrip() + "\n\n" + overview + "\n"
            state_file.write_text(content)
            
            # Update state for next increment
            # Extract just the number from current increment
            current_num = current_increment.split('-')[0] if '-' in current_increment else current_increment
            next_increment_num = int(current_num) + 1
            next_increment_str = str(next_increment_num).zfill(2)
            # Get full name for next increment
            next_increment_full = get_full_increment_name(memory_bank_path, release, component, next_increment_str)
            
            # Update state data - only current_increment matters
            state_data["current_increment"] = next_increment_full
            
            # Use the helper function to update header while preserving content
            from .increment_utils import _update_state_file_header
            _update_state_file_header(state_file, state_data)
        
        # Get all increments and check if next exists
        all_increments = get_increment_list(memory_bank_path, release, component)
        
        if next_increment_str not in all_increments:
            # Component completed - all increments done
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
        
        # Update progress
        progress = update_component_progress(memory_bank_path, release, component, current_increment)
        
        # Create structure for next increment
        create_increment_structure(memory_bank_path, release, component, next_increment_full)
        
        return format_success_response({
            "status": "success",
            "previous_increment": increment_name,  # Use full name
            "current_increment": next_increment_full,  # Use full name
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


@mcp.tool(name="ask-memory-bank")
async def ask_memory_bank(release: str, component: str, query: str) -> str:
    """Ask intelligent question to Memory Bank.
    
    Uses Claude Code SDK to analyze Memory Bank content and provide clear answers.
    
    Args:
        release: Release name
        component: Component name  
        query: Question to ask
        
    Returns:
        JSON with analyzed response
    """
    memory_bank_path = get_memory_bank_path()
    if not memory_bank_path:
        return format_error_response("Memory-Bank not bound to current project")
    
    try:
        # Use Claude Code SDK with proper async pattern
        response = await _ask_with_claude_sdk_async(memory_bank_path, release, component, query)
        
        return format_success_response({
            "status": "success",
            "response": response,
            "method": "claude_sdk"
        })
        
    except ImportError as e:
        return format_error_response(f"Claude Code SDK not available: {e}")
    except Exception as e:
        return format_error_response(f"Failed to query Memory Bank: {e}")


async def _generate_increment_overview(memory_bank_path: Path, release: str, component: str, increment: str) -> str:
    """Generate implementation overview for completed increment.
    
    Uses Claude Code SDK to analyze increment implementation.
    """
    working_dir = get_working_directory()
    
    # Use Claude SDK with proper async pattern
    try:
        overview = await _generate_with_claude_sdk_async(memory_bank_path, release, component, increment, working_dir)
        # Check if we got a meaningful overview
        if overview and len(overview) > 100:
            # Additional validation - check for generic content patterns
            generic_patterns = [
                "Key Changes",
                "placeholder",
                "to be implemented",
                "TODO",
                "[описание]",
                "[компонент]",
                "[N]"
            ]
            is_generic = any(pattern in overview for pattern in generic_patterns)
            if not is_generic:
                # SUCCESS - return SDK result
                return f"[Claude SDK Generated]\n\n{overview}"
    except ImportError as e:
        # SDK not available - this is expected when not running in Claude Code
        import sys
        print(f"Claude SDK not available (expected outside Claude Code): {e}", file=sys.stderr)
    except Exception as e:
        # Other errors - these are unexpected
        import sys
        print(f"Claude SDK unexpected error: {e}", file=sys.stderr)
    
    # Fallback: Generate detailed overview from available data
    increment_name = get_full_increment_name(memory_bank_path, release, component, increment)
    
    # Get increment details for context
    increment_details = get_increment_details(memory_bank_path, release, component, increment)
    
    overview = f"[FALLBACK - Claude SDK not available]\n\n### Increment {increment_name} - Implementation Summary\n\n"
    
    if increment_details:
        overview += f"**Title**: {increment_details.get('title', 'N/A')}\n"
        overview += f"**Description**: {increment_details.get('description', 'N/A')}\n\n"
    
    # Check journal for actual work done
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
    
    if journal_file.exists():
        journal_content = journal_file.read_text()
        lines = journal_content.split('\n')
        
        # Extract meaningful entries
        dev_entries = []
        tech_entries = []
        owner_entries = []
        
        current_role = None
        current_entry = []
        
        for line in lines:
            if '## ' in line and ' - ' in line:
                # Save previous entry if exists
                if current_role and current_entry:
                    entry_text = '\n'.join(current_entry).strip()
                    if current_role == 'dev':
                        dev_entries.append(entry_text)
                    elif current_role == 'tech-lead':
                        tech_entries.append(entry_text)
                    elif current_role == 'owner':
                        owner_entries.append(entry_text)
                
                # Start new entry
                if ' - dev' in line.lower():
                    current_role = 'dev'
                elif ' - tech' in line.lower():
                    current_role = 'tech-lead'
                elif ' - owner' in line.lower():
                    current_role = 'owner'
                else:
                    current_role = None
                current_entry = []
            elif current_role:
                current_entry.append(line)
        
        # Save last entry
        if current_role and current_entry:
            entry_text = '\n'.join(current_entry).strip()
            if current_role == 'dev':
                dev_entries.append(entry_text)
            elif current_role == 'tech-lead':
                tech_entries.append(entry_text)
            elif current_role == 'owner':
                owner_entries.append(entry_text)
        
        # Add development work summary
        if dev_entries:
            overview += "#### Development Activities\n"
            for i, entry in enumerate(dev_entries[-3:], 1):  # Last 3 dev entries
                # Extract key info from entry
                summary = entry[:200] + "..." if len(entry) > 200 else entry
                overview += f"{i}. {summary}\n"
            overview += "\n"
        
        # Add tech lead review summary
        if tech_entries:
            overview += "#### Technical Review Notes\n"
            for entry in tech_entries[-2:]:  # Last 2 tech reviews
                summary = entry[:150] + "..." if len(entry) > 150 else entry
                overview += f"- {summary}\n"
            overview += "\n"
        
        # Add owner decisions
        if owner_entries:
            overview += "#### Key Decisions\n"
            for entry in owner_entries[-2:]:  # Last 2 owner decisions
                summary = entry[:150] + "..." if len(entry) > 150 else entry
                overview += f"- {summary}\n"
            overview += "\n"
    
    # Check for actual files created/modified (if we have access to git)
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", "5", f"--grep={increment}"],
            cwd=str(working_dir),
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            overview += "#### Related Commits\n"
            for line in result.stdout.strip().split('\n')[:3]:
                overview += f"- {line}\n"
            overview += "\n"
    except:
        pass  # Git not available or failed
    
    # Add completion metadata
    overview += "#### Completion Details\n"
    overview += f"- **Status**: Completed\n"
    overview += f"- **Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
    overview += f"- **Working Directory**: {working_dir}\n"
    
    return overview


async def _generate_with_claude_sdk_async(memory_bank_path: Path, release: str, component: str, increment: str, working_dir: Path) -> str:
    """Use Claude Code SDK with proper async pattern to generate increment overview."""
    from claude_code_sdk import query as claude_query, ClaudeCodeOptions
    from ..config import get_global_config
    
    config = get_global_config()
    if not config:
        raise Exception("Global config not available")
    
    # Set API key if available (not needed for plan mode)
    import os
    if config.anthropic_api_key:
        os.environ['ANTHROPIC_API_KEY'] = config.anthropic_api_key
    
    # IMPORTANT: Set WORKING_DIR for the Claude SDK agent
    os.environ['WORKING_DIR'] = str(working_dir)
    
    # Load increment-implementation-overview prompt template (simplified version)
    template = load_template("workflow/memory-bank/increment-implementation-overview.md", memory_bank_path)
    if not template:
        raise Exception("Template not found: workflow/memory-bank/increment-implementation-overview.md")
    
    # Remove YAML frontmatter if present (it confuses Claude SDK)
    if template.startswith('---'):
        # Find the end of frontmatter
        end_marker = template.find('---', 3)
        if end_marker != -1:
            template = template[end_marker + 3:].strip()
    
    # Get full increment name
    increment_name = get_full_increment_name(memory_bank_path, release, component, increment)
    
    # Format prompt with context - using only essential parameters
    try:
        prompt = template.format(
            release=release,
            component=component,
            increment=increment_name,
            last_completed_increment=increment_name,  # Same as increment for overview generation
            memory_bank_path=str(memory_bank_path),
            working_dir=str(working_dir),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except KeyError as e:
        # If template has extra placeholders, use safe substitute
        from string import Template
        template_obj = Template(template)
        prompt = template_obj.safe_substitute(
            release=release,
            component=component,
            increment=increment_name,
            last_completed_increment=increment_name,
            memory_bank_path=str(memory_bank_path),
            working_dir=str(working_dir),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    # For MCP context, always bypass permissions - no plan mode!
    permission_mode = "bypassPermissions"
    
    # Set up options with full access for increment overview
    options = ClaudeCodeOptions(
        max_turns=15,  # Allow thorough analysis
        allowed_tools=["Read", "Grep", "LS", "Bash"],
        cwd=str(working_dir),  # Work from component repo
        permission_mode=permission_mode
    )
    
    # Execute query following official Claude Code SDK example pattern
    # Collect ALL text blocks from ALL messages (like in the PR review example)
    findings = []  # Accumulate all text blocks
    message_count = 0
    
    async for message in claude_query(prompt=prompt, options=options):
        message_count += 1
        
        # Check if message has content (following the example pattern)
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text') and block.text:
                    # Accumulate all text blocks (don't separate by message)
                    findings.append(block.text)
        
        # ResultMessage indicates completion
        if type(message).__name__ == "ResultMessage":
            # Return all accumulated text joined together
            if findings:
                return ''.join(findings)
            break
    
    # Check if we got any text
    if not findings:
        raise Exception(f"No text content from Claude Code SDK (processed {message_count} messages)")
    
    # Return accumulated findings
    return ''.join(findings)




async def _ask_with_claude_sdk_async(memory_bank_path: Path, release: str, component: str, query: str) -> str:
    """Use Claude Code SDK with proper async pattern to analyze and answer query."""
    # Import Claude Code SDK
    from claude_code_sdk import query as claude_query, ClaudeCodeOptions
    
    # Get config for permission mode check
    from ..config import get_global_config
    config = get_global_config()
    
    # Set API key if available (not needed for plan mode)
    import os
    if config and config.anthropic_api_key:
        os.environ['ANTHROPIC_API_KEY'] = config.anthropic_api_key
    
    # Load ask-memory-bank prompt template
    template = load_template("workflow/memory-bank/ask-memory-bank.md", memory_bank_path)
    if not template:
        template = _get_builtin_ask_template()
    
    # Remove YAML frontmatter if present (it confuses Claude SDK)
    if template.startswith('---'):
        # Find the end of frontmatter
        end_marker = template.find('---', 3)
        if end_marker != -1:
            template = template[end_marker + 3:].strip()
    
    # Prepare context information
    state_data = ensure_component_state(memory_bank_path, release, component)
    current_increment = state_data.get("current_increment", "01")
    
    # Format prompt
    prompt = template.format(
        query=query,
        release=release,
        component=component,
        current_increment=current_increment,
        memory_bank_path=str(memory_bank_path),
        working_dir=str(get_working_directory())
    )
    
# Prompt ready for Claude SDK
    
    # Set up options with unlimited turns and full access for Memory Bank analysis
    options = ClaudeCodeOptions(
        max_turns=20,  # Allow full analysis without artificial limits  
        allowed_tools=["Read", "Grep", "LS", "Bash"],  # EXTREMELY DANGEROUS - full access
        cwd=str(memory_bank_path),  # Work from Memory Bank directory for ask-memory-bank
        permission_mode="bypassPermissions"  # EXTREMELY DANGEROUS - bypass all permissions
    )
    
    # Execute query following official Claude Code SDK example pattern
    # Collect ALL text blocks from ALL messages (like in the PR review example)
    message_count = 0
    findings = []  # Accumulate all text blocks
    
    try:
        async for message in claude_query(prompt=prompt, options=options):
            message_count += 1
            
            # Check if message has content (following the example pattern)
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text') and block.text:
                        # Accumulate all text blocks (don't separate by message)
                        findings.append(block.text)
            
            # ResultMessage indicates completion
            if type(message).__name__ == "ResultMessage":
                # Return all accumulated text joined together
                if findings:
                    return ''.join(findings)
                break
        
        # Check if we got any text
        if not findings:
            raise Exception(f"No text content from Claude Code SDK (processed {message_count} messages)")
        
        # Return accumulated findings
        return ''.join(findings)
        
    except Exception:
        raise






def _get_builtin_ask_template() -> str:
    """Get built-in template for ask-memory-bank when not found in Memory Bank."""
    return """# Memory Bank Query Assistant

You are analyzing a Memory Bank structure to answer a specific question.

## Query
{query}

## Context
- Release: {release}
- Component: {component}
- Current Increment: {current_increment}
- Memory Bank Path: {memory_bank_path}
- Working Directory: {working_dir}

## Instructions

1. **Search Strategy**:
   - First check the component specification and decomposition
   - Review current state and progress
   - Look for relevant technical context
   - Check architecture documentation

2. **Analysis Approach**:
   - Understand the context of the question
   - Find relevant information from multiple sources
   - Synthesize a comprehensive answer
   - Be specific and reference actual files

3. **Response Format**:
   - Provide a clear, direct answer
   - Include specific references to files and sections
   - Give actionable information when applicable
   - No follow-up questions - provide complete information

## Available Directories to Search

- `implementation/releases/{release}/components/{component}/` - Component specification and increments
- `progress/releases/{release}/components/{component}/` - Current state and journal
- `architecture/` - Technical context and standards
- `product/` - Product vision and requirements

## Your Task

Answer the query comprehensively based on the Memory Bank content. Be thorough but concise.
Focus on providing actionable, specific information that directly addresses the question.
"""


def _get_journal_content_as_overview(memory_bank_path: Path, release: str, component: str, increment: str) -> str:
    """Extract journal content to use as implementation overview.
    
    Simple fallback approach that reuses existing journal entries as overview.
    """
    # Get full increment name
    increment_name = get_full_increment_name(memory_bank_path, release, component, increment)
    
    # Get journal file path
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
    
    if not journal_file.exists():
        return f"Increment {increment_name} completed - no journal entries found."
    
    try:
        content = journal_file.read_text()
        
        # Remove YAML header if present
        if content.startswith('---'):
            end_marker = content.find('---', 3)
            if end_marker != -1:
                content = content[end_marker + 3:].strip()
        
        # Remove the title line (# Journal - ...)
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            if line.startswith('# Journal -'):
                continue
            filtered_lines.append(line)
        
        journal_content = '\n'.join(filtered_lines).strip()
        
        if journal_content:
            return f"### Implementation Summary\n\n```md\n{journal_content}\n```"
        else:
            return f"Increment {increment_name} completed - journal entries available but empty."
            
    except Exception as e:
        return f"Increment {increment_name} completed - error reading journal: {e}"


async def _generate_progress_state_with_sdk(memory_bank_path: Path, release: str, component: str, increment: str) -> str:
    """Generate progress-state section from journal using Claude Code SDK.
    
    Uses the increment_journal_to_progress.md template to analyze journal entries
    and produce a properly formatted progress-state section.
    """
    from claude_code_sdk import query as claude_query, ClaudeCodeOptions
    from ..config import get_global_config
    
    config = get_global_config()
    
    # Set API key if available
    import os
    if config and config.anthropic_api_key:
        os.environ['ANTHROPIC_API_KEY'] = config.anthropic_api_key
    
    # Load the workflow template - first from Memory Bank, then from defaults
    template = load_template("workflow/memory-bank/increment-journal-to-progress.md", memory_bank_path)
    if not template:
        # Fallback to simplified generation if template not found
        return await _fallback_progress_generation(memory_bank_path, release, component, increment)
    
    # Remove YAML frontmatter if present
    if template.startswith('---'):
        end_marker = template.find('---', 3)
        if end_marker != -1:
            template = template[end_marker + 3:].strip()
    
    # Get full increment name
    increment_name = get_full_increment_name(memory_bank_path, release, component, increment)
    
    # Load journal content
    journal_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name / "journal.md"
    if not journal_file.exists():
        return f"## {increment_name}\n\n### State\nNo changes tracked - journal not found.\n\n### Progress\nIncrement completed without tracked changes."
    
    journal_content = journal_file.read_text()
    
    # Load existing progress-state for context
    state_file = memory_bank_path / "progress" / "releases" / release / "components" / component / "progress-state.md"
    existing_state = ""
    if state_file.exists():
        existing_state = state_file.read_text()
    else:
        existing_state = "No previous progress state - this is the first increment."
    
    # Format the template with placeholders
    prompt = template.format(
        release=release,
        component=component,
        increment_name=increment_name,
        journal_content=journal_content,
        existing_state=existing_state
    )
    
    # Set up options - limited tools since we're just analyzing provided content
    options = ClaudeCodeOptions(
        max_turns=1,  # Single response needed - no exploration
        allowed_tools=[],  # No tools needed - all content provided in prompt
        cwd=str(memory_bank_path),
        permission_mode="default"  # Standard mode for analysis
    )
    
    # Execute query and collect response
    response_text = []
    
    try:
        async for message in claude_query(prompt=prompt, options=options):
            # Collect text blocks from response
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text') and block.text:
                        response_text.append(block.text)
            
            # ResultMessage indicates completion
            if type(message).__name__ == "ResultMessage":
                break
        
        if not response_text:
            # Fallback if no response
            return await _fallback_progress_generation(memory_bank_path, release, component, increment)
        
        # Join all text and return
        return ''.join(response_text).strip()
        
    except Exception as e:
        # On any error, use fallback
        print(f"Claude SDK error: {e}, using fallback")
        return await _fallback_progress_generation(memory_bank_path, release, component, increment)


async def _fallback_progress_generation(memory_bank_path: Path, release: str, component: str, increment: str) -> str:
    """Fallback method to generate basic progress-state from journal."""
    increment_name = get_full_increment_name(memory_bank_path, release, component, increment)
    
    # Use the existing simple extraction
    journal_summary = _get_journal_content_as_overview(memory_bank_path, release, component, increment)
    
    # Format as progress-state section
    return f"""## {increment_name}

### State
Changes tracked in journal - see implementation summary below.

### Progress
{journal_summary}
"""


