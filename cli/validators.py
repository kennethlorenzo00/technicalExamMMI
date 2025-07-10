"""
Input validation functions for the CLI interface.
"""

import re
from typing import Optional, Tuple, Any
try:
    from ..utils.helpers import validate_priority, validate_status, parse_date
    from ..utils.constants import PRIORITIES, STATUSES
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('.')
    from utils.helpers import validate_priority, validate_status, parse_date
    from utils.constants import PRIORITIES, STATUSES


def validate_task_id(task_id: str) -> Tuple[bool, str]:
    if not task_id:
        return False, "Task ID cannot be empty"
    
    if not re.match(r'^[a-zA-Z0-9]{8}$', task_id):
        return False, "Task ID must be 8 alphanumeric characters"
    
    return True, ""


def validate_title(title: str) -> Tuple[bool, str]:
    if not title or not title.strip():
        return False, "Title cannot be empty"
    
    if len(title.strip()) > 200:
        return False, "Title cannot exceed 200 characters"
    
    return True, ""


def validate_description(description: str) -> Tuple[bool, str]:
    if len(description) > 1000:
        return False, "Description cannot exceed 1000 characters"
    
    return True, ""


def validate_due_date(due_date: str) -> Tuple[bool, str]:
    if not due_date:
        return True, ""  # Empty is valid (optional field)
    
    parsed_date = parse_date(due_date)
    if parsed_date is None:
        return False, "Invalid date format. Use YYYY-MM-DD, DD/MM/YYYY, or keywords like 'today', 'tomorrow'"
    
    return True, ""


def validate_priority_input(priority: str) -> Tuple[bool, str]:
    """
    Validate priority input.
    """
    if not priority:
        return False, "Priority cannot be empty"
    
    if not validate_priority(priority):
        valid_priorities = ", ".join(PRIORITIES.keys())
        return False, f"Invalid priority. Must be one of: {valid_priorities}"
    
    return True, ""


def validate_status_input(status: str) -> Tuple[bool, str]:
    """
    Validate status input.
    """
    if not status:
        return False, "Status cannot be empty"
    
    if not validate_status(status):
        valid_statuses = ", ".join(STATUSES.keys())
        return False, f"Invalid status. Must be one of: {valid_statuses}"
    
    return True, ""


def validate_yes_no_input(response: str) -> Tuple[bool, str]:
    """
    Validate yes/no input.
    """
    if not response:
        return False, "Please enter 'y' or 'n'"
    
    response_lower = response.lower().strip()
    if response_lower not in ['y', 'yes', 'n', 'no']:
        return False, "Please enter 'y' or 'n'"
    
    return True, ""


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_str)
    
    # Remove extra whitespace
    sanitized = ' '.join(sanitized.split())
    
    return sanitized.strip()


def validate_filter_input(filter_type: str, filter_value: str) -> Tuple[bool, str]:
    """
    Validate filter input for task listing.
    """
    if filter_type == "priority":
        return validate_priority_input(filter_value)
    elif filter_type == "status":
        return validate_status_input(filter_value)
    elif filter_type == "due_date":
        return validate_due_date(filter_value)
    else:
        return False, f"Unknown filter type: {filter_type}"

