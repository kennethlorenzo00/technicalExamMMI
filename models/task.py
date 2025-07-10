"""
Task model class 
"""

from datetime import datetime
from typing import Optional
try:
    from ..utils.helpers import (
        generate_task_id, parse_date, format_date, 
        get_priority_value, get_status_value,
        validate_priority, validate_status
    )
    from ..utils.constants import PRIORITIES, STATUSES
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('.')
    from utils.helpers import (
        generate_task_id, parse_date, format_date, 
        get_priority_value, get_status_value,
        validate_priority, validate_status
    )
    from utils.constants import PRIORITIES, STATUSES


class Task:
    def __init__(self, title: str, description: str = "", due_date: Optional[str] = None,
                 priority: str = "medium", status: str = "pending", task_id: Optional[str] = None):
        self._task_id = task_id or generate_task_id()
        self._title = title.strip()
        self._description = description.strip()
        self._due_date = parse_date(due_date) if due_date else None
        self._priority = get_priority_value(priority)
        self._status = get_status_value(status)
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        
        # Validate inputs
        self._validate_inputs()
    
    def _validate_inputs(self) -> None:
        """
        Validate task inputs and raise ValueError if invalid.
        """
        if not self._title:
            raise ValueError("Task title cannot be empty")
        
        if len(self._title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        
        if len(self._description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
        
        if self._priority not in PRIORITIES.values():
            raise ValueError("Invalid priority level")
        
        if self._status not in STATUSES.values():
            raise ValueError("Invalid status")
    
    # Property getters
    @property
    def task_id(self) -> str:
        """Get task ID."""
        return self._task_id
    
    @property
    def title(self) -> str:
        """Get task title."""
        return self._title
    
    @property
    def description(self) -> str:
        """Get task description."""
        return self._description
    
    @property
    def due_date(self) -> Optional[datetime]:
        """Get task due date."""
        return self._due_date
    
    @property
    def priority(self) -> int:
        """Get task priority."""
        return self._priority
    
    @property
    def status(self) -> int:
        """Get task status."""
        return self._status
    
    @property
    def created_at(self) -> datetime:
        """Get task creation timestamp."""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get task last update timestamp."""
        return self._updated_at
    
    # Property setters with validation
    @title.setter
    def title(self, value: str) -> None:
        """Set task title with validation."""
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be empty")
        if len(value) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        self._title = value
        self._updated_at = datetime.now()
    
    @description.setter
    def description(self, value: str) -> None:
        """Set task description with validation."""
        value = value.strip()
        if len(value) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
        self._description = value
        self._updated_at = datetime.now()
    
    @due_date.setter
    def due_date(self, value: Optional[str]) -> None:
        """Set task due date with validation."""
        if value is None:
            self._due_date = None
        else:
            parsed_date = parse_date(value)
            if parsed_date is None:
                raise ValueError("Invalid date format")
            self._due_date = parsed_date
        self._updated_at = datetime.now()
    
    @priority.setter
    def priority(self, value: str) -> None:
        """Set task priority with validation."""
        if not validate_priority(value):
            raise ValueError("Invalid priority level")
        self._priority = get_priority_value(value)
        self._updated_at = datetime.now()
    
    @status.setter
    def status(self, value: str) -> None:
        """Set task status with validation."""
        if not validate_status(value):
            raise ValueError("Invalid status")
        self._status = get_status_value(value)
        self._updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """
        Convert task to dictionary for database storage.
        """
        return {
            'task_id': self._task_id,
            'title': self._title,
            'description': self._description,
            'due_date': self._due_date,
            'priority': self._priority,
            'status': self._status,
            'created_at': self._created_at,
            'updated_at': self._updated_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """
        Create Task instance from dictionary.
        """
        task = cls.__new__(cls)
        task._task_id = data.get('task_id', generate_task_id())
        task._title = data.get('title', '')
        task._description = data.get('description', '')
        task._due_date = data.get('due_date')
        task._priority = data.get('priority', 2)  # medium
        task._status = data.get('status', 1)  # pending
        task._created_at = data.get('created_at', datetime.now())
        task._updated_at = data.get('updated_at', datetime.now())
        return task
    
    def is_overdue(self) -> bool:
        """
        Check if task is overdue.
        """
        if not self._due_date:
            return False
        return datetime.now() > self._due_date
    
    def is_completed(self) -> bool:
        """
        Check if task is completed.
        """
        return self._status == STATUSES['completed']
    
    def mark_completed(self) -> None:
        """Mark task as completed."""
        self._status = STATUSES['completed']
        self._updated_at = datetime.now()
    
    def get_days_until_due(self) -> int:
        """
        Get number of days until due date.
        """
        if not self._due_date:
            return 0
        delta = self._due_date.date() - datetime.now().date()
        return delta.days
    
    def __str__(self) -> str:
        """String representation of the task."""
        status_text = "✓" if self.is_completed() else "○"
        overdue_text = " (OVERDUE)" if self.is_overdue() else ""
        return f"{status_text} {self._title}{overdue_text}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the task."""
        return (f"Task(id={self._task_id}, title='{self._title}', "
                f"priority={self._priority}, status={self._status})")
    
    def __eq__(self, other) -> bool:
        """Check if two tasks are equal."""
        if not isinstance(other, Task):
            return False
        return self._task_id == other._task_id
    
    def __hash__(self) -> int:
        """Hash based on task ID."""
        return hash(self._task_id) 