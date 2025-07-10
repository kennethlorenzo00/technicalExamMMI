
import uuid
from datetime import datetime, timedelta
from dateutil import parser
from typing import Optional, Union
try:
    from .constants import DATE_FORMATS, DATE_KEYWORDS
except ImportError:
    import sys
    sys.path.append('.')
    from utils.constants import DATE_FORMATS, DATE_KEYWORDS


def generate_task_id() -> str:
    return str(uuid.uuid4())[:8]


def parse_date(date_string: str) -> Optional[datetime]:
    if not date_string:
        return None
    
    # Handle special keywords
    date_string = date_string.lower().strip()
    if date_string in DATE_KEYWORDS:
        today = datetime.now().date()
        if date_string == 'today':
            return datetime.combine(today, datetime.min.time())
        elif date_string == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            return datetime.combine(tomorrow, datetime.min.time())
        elif date_string == 'next_week':
            next_week = today + timedelta(days=7)
            return datetime.combine(next_week, datetime.min.time())
        elif date_string == 'next_month':
            next_month = today + timedelta(days=30)
            return datetime.combine(next_month, datetime.min.time())
    
    # Try parsing with dateutil first (handles most formats)
    try:
        return parser.parse(date_string)
    except (ValueError, TypeError):
        pass
    
    # Try specific formats
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None


def format_date(date_obj: Union[datetime, None]) -> str:
    if not date_obj:
        return "Not set"
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d %H:%M')
    return str(date_obj)


def format_priority(priority: int) -> str:
    """
    Format priority number to readable string.
    """
    try:
        from .constants import PRIORITY_NAMES
    except ImportError:
        from utils.constants import PRIORITY_NAMES
    return PRIORITY_NAMES.get(priority, 'Unknown')


def format_status(status: int) -> str:
    """
    Format status number to readable string.
    """
    try:
        from .constants import STATUS_NAMES
    except ImportError:
        from utils.constants import STATUS_NAMES
    return STATUS_NAMES.get(status, 'Unknown')


def validate_priority(priority: str) -> bool:
    """
    Validate priority input.
    """
    try:
        from .constants import PRIORITIES
    except ImportError:
        from utils.constants import PRIORITIES
    return priority.lower() in PRIORITIES


def validate_status(status: str) -> bool:
    """
    Validate status input.
    """
    try:
        from .constants import STATUSES
    except ImportError:
        from utils.constants import STATUSES
    return status.lower() in STATUSES


def get_priority_value(priority: str) -> int:
    """
    Get priority value from string.
    """
    try:
        from .constants import PRIORITIES
    except ImportError:
        from utils.constants import PRIORITIES
    return PRIORITIES.get(priority.lower(), 1)


def get_status_value(status: str) -> int:
    """
    Get status value from string.
    """
    try:
        from .constants import STATUSES
    except ImportError:
        from utils.constants import STATUSES
    return STATUSES.get(status.lower(), 1)


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to specified length.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def is_overdue(due_date: datetime) -> bool:
    """
    Check if a task is overdue.
    """
    if not due_date:
        return False
    return datetime.now() > due_date


def get_days_until_due(due_date: datetime) -> int:
    """
    Get number of days until due date.
    """
    if not due_date:
        return 0
    delta = due_date.date() - datetime.now().date()
    return delta.days 