"""Utility functions for increment-based workflow."""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from .increment_models import IncrementState, ComponentProgress


def ensure_component_state(memory_bank_path: Path, release: str, component: str) -> Dict[str, Any]:
    """Ensure component state exists and is properly initialized.
    
    Creates the state file if it doesn't exist, or loads existing state.
    Progress-state.md structure:
    - YAML header: current state (current_increment always full name)
    - Markdown body: history of completed increments
    
    Args:
        memory_bank_path: Path to Memory Bank root
        release: Release name
        component: Component name
        
    Returns:
        Dictionary with current state data
    """
    # Paths
    progress_dir = memory_bank_path / "progress" / "releases" / release / "components" / component
    state_file = progress_dir / "progress-state.md"
    
    # Ensure directories exist
    progress_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize or load progress state
    if not state_file.exists():
        # Get full increment name for first increment
        first_increment_full = get_full_increment_name(memory_bank_path, release, component, "01")
        
        # Create new state - minimal fields only
        state = IncrementState(
            release=release,
            component=component,
            current_increment=first_increment_full  # Always use full name
        )
        
        # Write state file with YAML header - minimal structure
        content = f"""---
release: "{state.release}"
component: "{state.component}"
current_increment: "{state.current_increment}"
---

# Progress History - {component}

"""
        state_file.write_text(content)
        return state.model_dump()
    
    else:
        # Load existing state
        content = state_file.read_text()
        
        # Extract YAML header
        if content.startswith('---\n'):
            yaml_end = content.find('\n---\n', 4)
            if yaml_end != -1:
                yaml_content = content[4:yaml_end]
                state_data = yaml.safe_load(yaml_content) or {}
            else:
                state_data = {}
        else:
            state_data = {}
        
        # Ensure required fields
        if 'current_increment' not in state_data:
            state_data['current_increment'] = get_full_increment_name(memory_bank_path, release, component, '01')
        
        # Convert short increment to full name if needed (for backward compatibility)
        current_inc = state_data.get('current_increment', '01')
        if len(current_inc) <= 2 or '-' not in current_inc:
            state_data['current_increment'] = get_full_increment_name(memory_bank_path, release, component, current_inc)
            # Update the file with full name
            _update_state_file_header(state_file, state_data)
            
        return state_data


def _update_state_file_header(state_file: Path, state_data: Dict[str, Any]):
    """Update only the YAML header of the state file, preserving markdown content."""
    if not state_file.exists():
        return
    
    content = state_file.read_text()
    
    # Extract markdown content (everything after the YAML header)
    markdown_content = ""
    if content.startswith('---\n'):
        yaml_end = content.find('\n---\n', 4)
        if yaml_end != -1:
            markdown_content = content[yaml_end + 5:]
    else:
        markdown_content = content
    
    # Create new header with minimal data
    new_header = "---\n"
    # Only essential fields
    field_order = ['release', 'component', 'current_increment']
    
    for key in field_order:
        if key in state_data:
            value = state_data[key]
            # Always quote string values for safety
            if isinstance(value, str):
                new_header += f'{key}: "{value}"\n'
            else:
                new_header += f'{key}: {value}\n'
    
    new_header += "---\n"
    
    # Write back with new header
    state_file.write_text(new_header + markdown_content)


def get_increment_list(memory_bank_path: Path, release: str, component: str) -> List[str]:
    """Get list of all increments for a component.
    
    Args:
        memory_bank_path: Path to Memory Bank root
        release: Release name
        component: Component name
        
    Returns:
        List of increment IDs in order (just numbers like "01", "02")
    """
    increments_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "increments"
    
    if not increments_dir.exists():
        return []
    
    # Find all increment files
    increment_files = list(increments_dir.glob("*.md"))
    
    # Extract increment IDs (assuming format: "01-title.md", "02-title.md", etc.)
    increment_ids = []
    for file_path in sorted(increment_files):
        name = file_path.stem
        if '-' in name:
            increment_id = name.split('-')[0]
            if increment_id.isdigit() or (len(increment_id) == 2 and increment_id[0].isdigit()):
                increment_ids.append(increment_id)
    
    return sorted(set(increment_ids))


def get_increment_details(memory_bank_path: Path, release: str, component: str, increment: str) -> Optional[Dict[str, Any]]:
    """Get details about a specific increment.
    
    Args:
        memory_bank_path: Path to Memory Bank root
        release: Release name
        component: Component name
        increment: Increment ID
        
    Returns:
        Dictionary with increment details or None if not found
    """
    increments_dir = memory_bank_path / "implementation" / "releases" / release / "components" / component / "increments"
    
    if not increments_dir.exists():
        return None
    
    # Find increment file
    increment_files = list(increments_dir.glob(f"{increment}-*.md"))
    
    if not increment_files:
        return None
    
    increment_file = increment_files[0]
    
    try:
        content = increment_file.read_text()
        
        # Extract title from filename
        title = increment_file.stem.replace(f"{increment}-", "").replace("-", " ").title()
        
        # Extract description from content (first paragraph after header)
        lines = content.split('\n')
        description = ""
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('---'):
                description = line.strip()
                break
        
        return {
            "id": increment,
            "title": title,
            "description": description,
            "file": str(increment_file.relative_to(memory_bank_path)),
            "filename": increment_file.name
        }
    except Exception:
        return None


def update_component_progress(memory_bank_path: Path, release: str, component: str, 
                            completed_increment: Optional[str] = None) -> ComponentProgress:
    """Update component progress tracking.
    
    Args:
        memory_bank_path: Path to Memory Bank root
        release: Release name
        component: Component name
        completed_increment: Increment ID or full name that was just completed
        
    Returns:
        Updated ComponentProgress model
    """
    # Get all increments (these are just numbers like "01", "02")
    all_increments = get_increment_list(memory_bank_path, release, component)
    
    # Load current state
    state_data = ensure_component_state(memory_bank_path, release, component)
    
    # Determine completed increments
    completed = []
    current_idx = -1
    
    current_increment = state_data.get('current_increment', '01')
    # Extract just the number from current increment if it's a full name
    if '-' in current_increment:
        current_num = current_increment.split('-')[0]
    else:
        current_num = current_increment
    
    if current_num:
        try:
            current_idx = all_increments.index(current_num)
            # All increments before current are completed
            completed = all_increments[:current_idx]
        except ValueError:
            pass
    
    # Add newly completed increment if provided
    if completed_increment:
        # Extract just the number if full name provided
        if '-' in completed_increment:
            completed_num = completed_increment.split('-')[0]
        else:
            completed_num = completed_increment
        
        if completed_num not in completed:
            completed.append(completed_num)
    
    # Create progress model - use full name for current_increment
    progress = ComponentProgress(
        release=release,
        component=component,
        total_increments=len(all_increments),
        completed_increments=completed,
        current_increment=current_increment,  # Keep full name
        last_activity=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    
    # Calculate completion
    progress.calculate_completion()
    
    return progress


def get_full_increment_name(memory_bank_path: Path, release: str, component: str, increment: str) -> str:
    """Get full increment name with title.
    
    Args:
        memory_bank_path: Path to Memory Bank root
        release: Release name
        component: Component name
        increment: Increment ID (e.g., "01" or "01-initial-setup")
        
    Returns:
        Full increment name (e.g., "01-models-and-protocols") or just ID if not found
    """
    # If already has a name, return as is
    if len(increment) > 2 and "-" in increment:
        return increment
        
    # Get full name from implementation
    details = get_increment_details(memory_bank_path, release, component, increment)
    if details and "filename" in details:
        # Use the filename without .md extension
        return details["filename"].replace(".md", "")
    else:
        # Fallback to just the increment ID (no -increment suffix)
        return increment


def create_increment_structure(memory_bank_path: Path, release: str, component: str, increment: str):
    """Create directory structure for an increment.
    
    Args:
        memory_bank_path: Path to Memory Bank root
        release: Release name
        component: Component name
        increment: Increment ID (e.g., "01" or "01-initial-setup")
    """
    # Get full increment name with title
    increment_name = get_full_increment_name(memory_bank_path, release, component, increment)
    
    # Create increment directory in progress with full name
    increment_dir = memory_bank_path / "progress" / "releases" / release / "components" / component / "increments" / increment_name
    increment_dir.mkdir(parents=True, exist_ok=True)
    
    # Create journal file if doesn't exist
    journal_file = increment_dir / "journal.md"
    if not journal_file.exists():
        header = f"""---
datetime: "{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}"
release: "{release}"
component: "{component}"
increment: "{increment_name}"
---

# Journal - {component}/{increment_name}

"""
        journal_file.write_text(header)