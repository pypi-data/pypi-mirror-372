"""Data models for Memory-Bank module."""

from datetime import datetime
from pathlib import Path
from pydantic import BaseModel


class ProjectBinding(BaseModel):
    """Project binding to Memory-Bank."""
    
    memory_bank_name: str
    memory_bank_path: Path
    bound_at: datetime