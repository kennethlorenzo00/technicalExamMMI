# Task Management Application

## Features

- Add, list, update, complete, and delete tasks

## Quick Start

### 1. Install Dependencies

```
pip install -r requirements.txt
```

### 2. Start MongoDB (if not already running)


### 3. Run the Application

```
python main.py
```

## Usage

Once the application starts, you'll see a welcome screen. Use these commands:

### Basic Commands

- `add` - Add a new task
- `list` - List all tasks
- `update` - Update task details
- `complete` - Mark a task as completed
- `delete` - Delete a task
- `help` - Show available commands
- `exit` - Exit the application

### Examples

```bash
# Add a new task
add

# List all tasks
list

# List high priority tasks
list --priority high

# List tasks due today
list --due-date today

# List overdue tasks
list --due-date overdue

# Search for tasks containing "meeting"
search meeting

# Update a task (you'll be prompted for the task ID)
update

# Complete a task (you'll be prompted for the task ID)
complete

# Delete a task (you'll be prompted for the task ID)
delete
```


## Project Structure

```
├── main.py                 # Main application entry point
├── models/
│   ├── task.py            # Task model class
│   └── task_manager.py    # TaskManager class
├── database/
│   └── mongo_client.py    # MongoDB connection and operations
├── cli/
│   ├── interface.py       # CLI interface class
│   └── validators.py      # Input validation functions
├── utils/
│   ├── constants.py       # Application constants
│   └── helpers.py         # Helper functions
├── requirements.txt       # Python dependencies
└── README.md            
```

## Database Schema

Each task document contains:
- `task_id` - Unique 8-character identifier
- `title` - Task title (max 200 characters)
- `description` - Task description (max 1000 characters)
- `due_date` - Due date (optional)
- `priority` - Priority level (1=low, 2=medium, 3=high)
- `status` - Status (1=pending, 2=in_progress, 3=completed)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
