"""
TaskManager class 
"""

import threading
from typing import List, Dict, Optional, Callable
from datetime import datetime
try:
    from .task import Task
    from ..database.mongo_client import MongoClient
    from ..utils.helpers import format_priority, format_status, format_date, truncate_text
    from ..utils.constants import STATUSES, PRIORITIES
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('.')
    from models.task import Task
    from database.mongo_client import MongoClient
    from utils.helpers import format_priority, format_status, format_date, truncate_text
    from utils.constants import STATUSES, PRIORITIES


class TaskManager:
    
    def __init__(self, db_client: Optional[MongoClient] = None):
        self._db_client = db_client or MongoClient()
        self._tasks: Dict[str, Task] = {}  # O(1) lookup by task_id
        self._task_list: List[Task] = []   # Ordered list for display
        self._lock = threading.Lock()      # Thread safety
        self._background_tasks: List[threading.Thread] = []
        
        # Load tasks from database
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        try:
            with self._lock:
                task_data_list = self._db_client.find_all_tasks()
                self._tasks.clear()
                self._task_list.clear()
                
                for task_data in task_data_list:
                    task = Task.from_dict(task_data)
                    self._tasks[task.task_id] = task
                    self._task_list.append(task)
                
                # Sort by creation date (newest first)
                self._task_list.sort(key=lambda t: t.created_at, reverse=True)
                
        except Exception as e:
            print(f"Error loading tasks: {str(e)}")
    
    def add_task(self, title: str, description: str = "", due_date: Optional[str] = None,
                 priority: str = "medium", status: str = "pending") -> Optional[Task]:
        """
        Add a new task 
        """
        try:
            task = Task(title, description, due_date, priority, status)
            
            with self._lock:
                # Check if task_id already exists (very unlikely but possible)
                if task.task_id in self._tasks:
                    task = Task(title, description, due_date, priority, status)  # Generate new ID
                
                # Save to database
                if self._db_client.insert_task(task.to_dict()):
                    # Add to memory
                    self._tasks[task.task_id] = task
                    self._task_list.append(task)
                    
                    # Sort by creation date
                    self._task_list.sort(key=lambda t: t.created_at, reverse=True)
                    
                    return task
                else:
                    return None
                    
        except ValueError as e:
            print(f"Validation error: {str(e)}")
            return None
        except Exception as e:
            print(f"Error adding task: {str(e)}")
            return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID with O(1) lookup.
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks 
        """
        with self._lock:
            return self._task_list.copy()
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """
        Update task properties with validation.
        """
        try:
            with self._lock:
                task = self._tasks.get(task_id)
                if not task:
                    return False
                
                # Update properties
                update_data = {}
                
                if 'title' in kwargs:
                    task.title = kwargs['title']
                    update_data['title'] = task.title
                
                if 'description' in kwargs:
                    task.description = kwargs['description']
                    update_data['description'] = task.description
                
                if 'due_date' in kwargs:
                    task.due_date = kwargs['due_date']
                    update_data['due_date'] = task.due_date
                
                if 'priority' in kwargs:
                    task.priority = kwargs['priority']
                    update_data['priority'] = task.priority
                
                if 'status' in kwargs:
                    task.status = kwargs['status']
                    update_data['status'] = task.status
                
                # Update in database
                if self._db_client.update_task(task_id, update_data):
                    return True
                else:
                    return False
                    
        except ValueError as e:
            print(f"Validation error: {str(e)}")
            return False
        except Exception as e:
            print(f"Error updating task: {str(e)}")
            return False
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark task as completed
        """
        try:
            with self._lock:
                task = self._tasks.get(task_id)
                if not task:
                    return False
                
                task.mark_completed()
                
                # Update in database
                return self._db_client.update_task(task_id, {
                    'status': task.status,
                    'updated_at': task.updated_at
                })
                
        except Exception as e:
            print(f"Error completing task: {str(e)}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        """
        try:
            with self._lock:
                task = self._tasks.get(task_id)
                if not task:
                    return False
                
                # Delete from database
                if self._db_client.delete_task(task_id):
                    # Remove from memory
                    del self._tasks[task_id]
                    self._task_list.remove(task)
                    return True
                else:
                    return False
                    
        except Exception as e:
            print(f"Error deleting task: {str(e)}")
            return False
    
    def filter_tasks(self, priority: Optional[str] = None, status: Optional[str] = None,
                    due_date: Optional[str] = None, search: Optional[str] = None) -> List[Task]:
        """
        Filter tasks based on multiple criteria with efficient algorithms.
        """
        with self._lock:
            filtered_tasks = self._task_list.copy()
            
            # Filter by priority
            if priority:
                priority_value = PRIORITIES.get(priority.lower())
                if priority_value is not None:
                    filtered_tasks = [t for t in filtered_tasks if t.priority == priority_value]
            
            # Filter by status
            if status:
                status_value = STATUSES.get(status.lower())
                if status_value is not None:
                    filtered_tasks = [t for t in filtered_tasks if t.status == status_value]
            
            # Filter by due date
            if due_date:
                if due_date.lower() == 'today':
                    today = datetime.now().date()
                    filtered_tasks = [
                        t for t in filtered_tasks 
                        if t.due_date and t.due_date.date() == today
                    ]
                elif due_date.lower() == 'overdue':
                    filtered_tasks = [t for t in filtered_tasks if t.is_overdue()]
            
            # Search in title and description
            if search:
                search_lower = search.lower()
                filtered_tasks = [
                    t for t in filtered_tasks
                    if search_lower in t.title.lower() or search_lower in t.description.lower()
                ]
            
            return filtered_tasks
    
    def sort_tasks(self, tasks: List[Task], sort_by: str = "created_at", 
                   reverse: bool = True) -> List[Task]:
        """
        Sort tasks by specified criteria.
        """
        if sort_by == "created_at":
            return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)
        elif sort_by == "due_date":
            return sorted(tasks, key=lambda t: t.due_date or datetime.max, reverse=reverse)
        elif sort_by == "priority":
            return sorted(tasks, key=lambda t: t.priority, reverse=reverse)
        elif sort_by == "title":
            return sorted(tasks, key=lambda t: t.title.lower(), reverse=reverse)
        else:
            return tasks
    

    def cleanup_background_tasks(self) -> None:
        """
        Clean up completed background tasks.
        """
        self._background_tasks = [t for t in self._background_tasks if t.is_alive()]
    
    def get_tasks_for_display(self, filters: Optional[Dict] = None, 
                             sort_by: str = "created_at", reverse: bool = True) -> List[Dict]:
        """
        Get tasks formatted for display.
        
        """
        # Apply filters
        if filters:
            tasks = self.filter_tasks(**filters)
        else:
            tasks = self.get_all_tasks()
        
        # Sort tasks
        tasks = self.sort_tasks(tasks, sort_by, reverse)
        
        # Format for display
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                'ID': task.task_id,
                'Title': truncate_text(task.title, 30),
                'Description': truncate_text(task.description, 40),
                'Due Date': format_date(task.due_date),
                'Priority': format_priority(task.priority),
                'Status': format_status(task.status),
                'Created': format_date(task.created_at),
                'Overdue': 'Yes' if task.is_overdue() else 'No'
            })
        
        return formatted_tasks
    
    def close(self) -> None:
        """
        Clean up resources and close database connection.
        """
        self.cleanup_background_tasks()
        if self._db_client:
            self._db_client.close_connection() 