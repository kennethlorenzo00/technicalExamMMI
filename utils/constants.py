
# Task Priorities
PRIORITIES = {
    'low': 1,
    'medium': 2,
    'high': 3
}

PRIORITY_NAMES = {
    1: 'Low',
    2: 'Medium',
    3: 'High'
}

# Task Statuses
STATUSES = {
    'pending': 1,
    'in_progress': 2,
    'completed': 3
}

STATUS_NAMES = {
    1: 'Pending',
    2: 'In Progress',
    3: 'Completed'
}

# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'task_management',
    'collection': 'tasks'
}

# CLI Colors
COLORS = {
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'white': '\033[97m',
    'bold': '\033[1m',
    'underline': '\033[4m',
    'end': '\033[0m'
}

# Application Messages
MESSAGES = {
    'welcome': 'Task Management Application',
    'goodbye': 'Bye bye!',
    'invalid_command': 'Invalid command. Type "help" for available commands.',
    'task_added': 'Task added successfully!',
    'task_updated': 'Task updated successfully!',
    'task_completed': 'Task marked as completed!',
    'task_deleted': 'Task deleted successfully!',
    'no_tasks': 'No tasks found.',
    'task_not_found': 'Task not found.',
    'invalid_input': 'Invalid input. Please try again.',
    'database_error': 'Database connection error.',
    'validation_error': 'Validation error: '
}

# Date Formats
DATE_FORMATS = [
    '%Y-%m-%d',
    '%d/%m/%Y',
    '%m/%d/%Y',
    '%d-%m-%Y',
    '%Y/%m/%d'
]

# Special Date Keywords
DATE_KEYWORDS = {
    'today': 'today',
    'tomorrow': 'tomorrow',
    'next_week': 'next_week',
    'next_month': 'next_month'
} 