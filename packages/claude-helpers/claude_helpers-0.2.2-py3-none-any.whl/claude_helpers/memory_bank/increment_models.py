"""Data models for increment-based Memory Bank workflow."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Literal
from pydantic import BaseModel, Field


class IncrementState(BaseModel):
    """Component increment state for Memory Bank workflow."""
    
    release: str = Field(..., description="Release name (e.g. '01-pre-alpha')")
    component: str = Field(..., description="Component name (e.g. '01-core-api')")
    current_increment: str = Field(default="01", description="Current increment ID (e.g. '01', '02')")
    increment_status: Literal["not_started", "in_progress", "completed"] = Field(
        default="not_started",
        description="Status of current increment"
    )
    datetime: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        description="Last update timestamp in UTC"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "release": "01-pre-alpha",
                "component": "01-core-api",
                "current_increment": "03",
                "increment_status": "in_progress",
                "datetime": "2025-08-24T10:30:00Z"
            }
        }


class IncrementJournalEntry(BaseModel):
    """Journal entry for increment work."""
    
    datetime: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        description="Entry timestamp in UTC"
    )
    role: Literal["owner", "pm", "dev", "tech-lead"] = Field(
        ..., 
        description="Role making the entry"
    )
    increment: str = Field(..., description="Increment ID")
    message: str = Field(..., description="Journal message content")
    entry_type: Literal["note", "milestone", "issue", "decision"] = Field(
        default="note",
        description="Type of journal entry"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "datetime": "2025-08-24T10:30:00Z",
                "role": "dev",
                "increment": "03",
                "message": "Started implementation of authentication flow",
                "entry_type": "milestone"
            }
        }


class IncrementOverview(BaseModel):
    """Implementation overview generated when increment is completed."""
    
    increment: str = Field(..., description="Completed increment ID")
    completed_at: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        description="Completion timestamp"
    )
    working_directory: str = Field(..., description="Project working directory")
    summary: str = Field(..., description="Generated summary of implementation")
    key_changes: List[str] = Field(
        default_factory=list,
        description="List of key changes made"
    )
    issues_encountered: List[str] = Field(
        default_factory=list,
        description="Issues encountered during implementation"
    )
    next_steps: Optional[str] = Field(
        None,
        description="Recommended next steps"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "increment": "03",
                "completed_at": "2025-08-24T15:45:00Z",
                "working_directory": "/home/user/project",
                "summary": "Successfully implemented authentication flow with JWT tokens",
                "key_changes": [
                    "Added JWT token generation",
                    "Implemented login/logout endpoints",
                    "Created user session management"
                ],
                "issues_encountered": [
                    "Token refresh logic needed optimization"
                ],
                "next_steps": "Proceed with authorization and permissions increment"
            }
        }


class ComponentProgress(BaseModel):
    """Overall component progress tracking."""
    
    release: str
    component: str
    total_increments: int = Field(..., description="Total number of increments")
    completed_increments: List[str] = Field(
        default_factory=list,
        description="List of completed increment IDs"
    )
    current_increment: str = Field(..., description="Current active increment")
    started_at: Optional[str] = Field(None, description="Component work start time")
    last_activity: str = Field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        description="Last activity timestamp"
    )
    completion_percentage: float = Field(
        default=0.0,
        description="Percentage of increments completed"
    )
    
    def calculate_completion(self):
        """Calculate completion percentage based on completed increments."""
        if self.total_increments > 0:
            self.completion_percentage = (len(self.completed_increments) / self.total_increments) * 100
        return self.completion_percentage
    
    class Config:
        json_schema_extra = {
            "example": {
                "release": "01-pre-alpha",
                "component": "01-core-api",
                "total_increments": 8,
                "completed_increments": ["01", "02"],
                "current_increment": "03",
                "started_at": "2025-08-20T09:00:00Z",
                "last_activity": "2025-08-24T10:30:00Z",
                "completion_percentage": 25.0
            }
        }