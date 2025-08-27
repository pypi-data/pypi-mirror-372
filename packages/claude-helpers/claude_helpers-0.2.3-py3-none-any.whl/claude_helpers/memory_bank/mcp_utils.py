"""Utility functions for Memory Bank MCP operations."""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import re


def get_memory_bank_path() -> Optional[Path]:
    """Get Memory-Bank path from current working directory binding."""
    # Look for .helpers/memory_bank.json in current directory
    helpers_dir = Path.cwd() / ".helpers"
    binding_file = helpers_dir / "memory_bank.json"
    
    if binding_file.exists():
        try:
            with open(binding_file, 'r') as f:
                binding = json.load(f)
            memory_bank_path = Path(binding['memory_bank_path'])
            if memory_bank_path.exists():
                return memory_bank_path
        except Exception:
            pass
    
    return None


def get_working_directory() -> Path:
    """Get current working directory for the project.
    
    Prioritizes WORKING_DIR environment variable, falls back to cwd.
    """
    import os
    working_dir = os.environ.get('WORKING_DIR')
    if working_dir:
        return Path(working_dir)
    return Path.cwd()


def extract_yaml_datetime(file_path: Path) -> Optional[float]:
    """Extract datetime from YAML header and convert to timestamp."""
    if not file_path.exists():
        return None
    
    try:
        content = file_path.read_text()
        if not content.startswith('---\n'):
            return None
            
        # Find end of YAML header
        yaml_end = content.find('\n---\n', 4)
        if yaml_end == -1:
            return None
            
        yaml_content = content[4:yaml_end]
        yaml_data = yaml.safe_load(yaml_content)
        
        if 'datetime' in yaml_data:
            dt_str = yaml_data['datetime']
            # Parse as UTC and convert to local timestamp for comparison with file mtime
            dt_utc = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            # Convert UTC to local time for proper comparison with file system timestamps
            import time
            return dt_utc.timestamp() + time.timezone
    except Exception:
        pass
    
    return None


def paginate_content(content: str, page: int = 1, page_size_tokens: int = 5000) -> Dict[str, Any]:
    """Paginate content with smart section-based splitting.
    
    Args:
        content: Full content to paginate
        page: Page number (1-indexed)
        page_size_tokens: Approximate tokens per page
        
    Returns:
        Dict with content and pagination metadata
    """
    if not content or not content.strip():
        return {
            "content": "",
            "pagination": {
                "current_page": 1,
                "total_pages": 1,
                "has_more": False,
                "total_size": "0KB",
                "page_size": "0KB"
            }
        }
    
    # Account for JSON encoding overhead (approximately 30-50% for markdown with lots of newlines)
    # We use a conservative 2.5x factor instead of 4x to account for JSON escaping
    # This gives us ~12.5K chars per page for 5K tokens, which after JSON encoding
    # will be approximately 18-20K chars in the final JSON
    chars_per_page = int(page_size_tokens * 2.5)
    
    # Split content by logical boundaries (markdown headers)
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
        # Check if adding this section would exceed page size
        if len(current_page_content + section) > chars_per_page and current_page_content:
            # Current page is full, start new page
            pages.append(current_page_content.strip())
            current_page_content = section
        else:
            # Add section to current page
            current_page_content += section
    
    # Add the last page if it has content
    if current_page_content.strip():
        pages.append(current_page_content.strip())
    
    if not pages:
        pages = [""]
    
    total_pages = len(pages)
    
    # Handle page bounds
    if page < 1:
        page = 1
    elif page > total_pages:
        return {
            "content": "",
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "has_more": False,
                "total_size": f"{len(content) // 1024}KB",
                "page_size": "0KB",
                "error": f"Page {page} does not exist. Total pages: {total_pages}"
            }
        }
    
    page_content = pages[page - 1]
    
    # Add pagination markers to the content itself
    if total_pages > 1:
        # Add header showing page info
        page_header = f"📄 **PAGE {page} OF {total_pages}**\n\n"
        
        # Add footer with clear instructions
        if page < total_pages:
            page_footer = f"\n\n---\n\n⚠️ **CONTENT CONTINUES ON NEXT PAGE**\n"
            page_footer += f"📄 This is page {page} of {total_pages}. To read the next page, call this function again with `page={page + 1}`\n"
            page_footer += f"❗ **IMPORTANT**: You MUST read ALL {total_pages} pages to get the complete context!\n"
        else:
            page_footer = f"\n\n---\n\n✅ **END OF DOCUMENT** (Page {page} of {total_pages})\n"
        
        # Combine with actual content
        page_content = page_header + page_content + page_footer
    
    return {
        "content": page_content,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "has_more": page < total_pages,
            "total_size": f"{len(content) // 1024}KB",
            "page_size": f"{len(page_content) // 1024}KB",
            "next_page_hint": f"Use page={page + 1} to continue reading" if page < total_pages else None
        }
    }


def create_yaml_header(**metadata) -> str:
    """Create YAML header for markdown files."""
    yaml_content = yaml.dump(metadata, default_flow_style=False)
    return f"---\n{yaml_content}---\n\n"


def safe_load_yaml(file_path: Path) -> Dict[str, Any]:
    """Safely load YAML file with error handling."""
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Handle YAML header in markdown files
        if content.startswith('---\n'):
            yaml_end = content.find('\n---\n', 4)
            if yaml_end != -1:
                yaml_content = content[4:yaml_end]
                return yaml.safe_load(yaml_content) or {}
        
        # Plain YAML file
        return yaml.safe_load(content) or {}
    except Exception:
        return {}


def load_template(template_name: str, memory_bank_path: Optional[Path] = None) -> Optional[str]:
    """Load template from Memory Bank or fallback to built-in.
    
    Priority:
    1. Memory Bank templates/workflow/memory-bank/
    2. Memory Bank templates/workflow/pm/
    3. Memory Bank templates/progress/
    4. Built-in templates in claude-helpers
    """
    # Try Memory Bank templates first
    if memory_bank_path and memory_bank_path.exists():
        template_paths = [
            memory_bank_path / "templates" / "workflow" / "memory-bank" / template_name,
            memory_bank_path / "templates" / "workflow" / "pm" / template_name,
            memory_bank_path / "templates" / "progress" / template_name,
            memory_bank_path / "templates" / template_name
        ]
        
        for template_path in template_paths:
            if template_path.exists():
                try:
                    return template_path.read_text()
                except Exception:
                    pass
    
    # Fallback to built-in templates
    from pathlib import Path as PathLib
    package_root = PathLib(__file__).parent
    
    built_in_paths = [
        package_root / "template_sources" / "workflow" / template_name,
        package_root / "template_sources" / "progress" / template_name,
        package_root / "template_sources" / template_name
    ]
    
    for template_path in built_in_paths:
        if template_path.exists():
            try:
                return template_path.read_text()
            except Exception:
                pass
    
    return None


def format_error_response(error_msg: str) -> str:
    """Format error message as JSON response."""
    return json.dumps({"error": error_msg})


def format_success_response(data: Dict[str, Any]) -> str:
    """Format success response as JSON."""
    return json.dumps(data)