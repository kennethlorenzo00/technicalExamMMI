import sys
from typing import Optional, Dict, List
from tabulate import tabulate
from colorama import init, Fore, Back, Style

try:
    from ..models.task_manager import TaskManager
    from ..utils.constants import COLORS, MESSAGES, PRIORITIES, STATUSES
    from ..utils.helpers import format_date, format_priority, format_status
    from .validators import (
        validate_title, validate_description, validate_due_date,
        validate_priority_input, validate_status_input, validate_task_id,
        validate_yes_no_input, sanitize_input, validate_filter_input
    )
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('.')
    from models.task_manager import TaskManager
    from utils.constants import COLORS, MESSAGES, PRIORITIES, STATUSES
    from utils.helpers import format_date, format_priority, format_status
    from cli.validators import (
        validate_title, validate_description, validate_due_date,
        validate_priority_input, validate_status_input, validate_task_id,
        validate_yes_no_input, sanitize_input, validate_filter_input
    )

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class CLIInterface:
    
    def __init__(self, task_manager: Optional[TaskManager] = None):
        self.task_manager = task_manager or TaskManager()
        self.running = True
        self.commands = {
            'add': self.add_task,
            'list': self.list_tasks,
            'update': self.update_task,
            'complete': self.complete_task,
            'delete': self.delete_task,
            'help': self.show_help,
            'exit': self.exit_app
        }
    
    def run(self) -> None:
        self.print_welcome()
        
        while self.running:
            try:
                self.print_prompt()
                command = input().strip().lower()
                
                if not command:
                    continue
                
                self.process_command(command)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Use 'exit' to quit the application.{Style.RESET_ALL}")
            except EOFError:
                self.exit_app()
            except Exception as e:
                print(f"{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
    
    def print_welcome(self) -> None:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*30}")
        print(f"{Fore.CYAN}{Style.BRIGHT}  {MESSAGES['welcome']}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*30}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'help' to show available commands.{Style.RESET_ALL}\n")
    
    def print_prompt(self) -> None:
        print(f"{Fore.GREEN}user@task-manager>{Style.RESET_ALL} ", end="")
    
    def process_command(self, command: str) -> None:
        if ' ' in command:
            cmd, args = command.split(' ', 1)
        else:
            cmd, args = command, ""
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            print(f"{Fore.RED}{MESSAGES['invalid_command']}{Style.RESET_ALL}")
    
    def add_task(self, args: str = "") -> None:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Add New Task ==={Style.RESET_ALL}")
        
        try:
            # Get task title
            while True:
                title = input(f"{Fore.YELLOW}Title: {Style.RESET_ALL}").strip()
                is_valid, error = validate_title(title)
                if is_valid:
                    break
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            
            # Get task description
            description = input(f"{Fore.YELLOW}Description (optional): {Style.RESET_ALL}").strip()
            is_valid, error = validate_description(description)
            if not is_valid:
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")
                return
            
            # Get due date
            while True:
                due_date = input(f"{Fore.YELLOW}Due Date (optional, format: YYYY-MM-DD or 'today', 'tomorrow'): {Style.RESET_ALL}").strip()
                is_valid, error = validate_due_date(due_date)
                if is_valid:
                    break
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            
            # Get priority
            while True:
                print(f"{Fore.YELLOW}Priority: {Style.RESET_ALL}")
                for i, priority in enumerate(PRIORITIES.keys(), 1):
                    print(f"  {i}. {priority.title()}")
                
                priority_choice = input(f"{Fore.YELLOW}Enter choice (1-3): {Style.RESET_ALL}").strip()
                if priority_choice == "1":
                    priority = "low"
                    break
                elif priority_choice == "2":
                    priority = "medium"
                    break
                elif priority_choice == "3":
                    priority = "high"
                    break
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter 1, 2, or 3.{Style.RESET_ALL}")
            
            # Create task
            task = self.task_manager.add_task(
                title=sanitize_input(title),
                description=sanitize_input(description),
                due_date=due_date if due_date else None,
                priority=priority
            )
            
            if task:
                print(f"\n{Fore.GREEN}✓ {MESSAGES['task_added']}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Task ID: {task.task_id}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to add task.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Task creation cancelled.{Style.RESET_ALL}")
    
    def list_tasks(self, args: str = "") -> None:
        """
        List tasks with optional filtering.
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Task List ==={Style.RESET_ALL}")
        
        # Parse filter arguments
        filters = {}
        if args:
            parts = args.split()
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    filter_type = parts[i].lstrip('-').replace('-', '_') 
                    filter_value = parts[i + 1]
                    is_valid, error = validate_filter_input(filter_type, filter_value)
                    if is_valid:
                        filters[filter_type] = filter_value
                    else:
                        print(f"{Fore.RED}Invalid filter: {error}{Style.RESET_ALL}")
                        return
        
        # Get tasks for display
        tasks_data = self.task_manager.get_tasks_for_display(filters)
        
        if not tasks_data:
            print(f"{Fore.YELLOW}{MESSAGES['no_tasks']}{Style.RESET_ALL}")
            return
        
        # Display tasks in table format
        headers = list(tasks_data[0].keys())
        table_data = [[row[header] for header in headers] for row in tasks_data]
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n{Fore.CYAN}Total tasks: {len(tasks_data)}{Style.RESET_ALL}")
    
    def update_task(self, args: str = "") -> None:
        """
        Update an existing task.
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Update Task ==={Style.RESET_ALL}")
        
        # Get task ID
        task_id = args.strip() if args else input(f"{Fore.YELLOW}Enter Task ID: {Style.RESET_ALL}").strip()
        
        if not task_id:
            print(f"{Fore.RED}Task ID is required.{Style.RESET_ALL}")
            return
        
        # Validate task ID
        is_valid, error = validate_task_id(task_id)
        if not is_valid:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            return
        
        # Get task
        task = self.task_manager.get_task(task_id)
        if not task:
            print(f"{Fore.RED}{MESSAGES['task_not_found']}{Style.RESET_ALL}")
            return
        
        # Show current task details
        print(f"\n{Fore.CYAN}Current task details:{Style.RESET_ALL}")
        self._display_task_details(task)
        
        # Get update fields
        update_data = {}
        
        try:
            # Update title
            new_title = input(f"{Fore.YELLOW}New title (press Enter to keep current): {Style.RESET_ALL}").strip()
            if new_title:
                is_valid, error = validate_title(new_title)
                if is_valid:
                    update_data['title'] = sanitize_input(new_title)
                else:
                    print(f"{Fore.RED}{error}{Style.RESET_ALL}")
                    return
            
            # Update description
            new_description = input(f"{Fore.YELLOW}New description (press Enter to keep current): {Style.RESET_ALL}").strip()
            if new_description:
                is_valid, error = validate_description(new_description)
                if is_valid:
                    update_data['description'] = sanitize_input(new_description)
                else:
                    print(f"{Fore.RED}{error}{Style.RESET_ALL}")
                    return
            
            # Update due date
            new_due_date = input(f"{Fore.YELLOW}New due date (press Enter to keep current)(optional, format: YYYY-MM-DD or 'today', 'tomorrow'): {Style.RESET_ALL}").strip()
            if new_due_date:
                is_valid, error = validate_due_date(new_due_date)
                if is_valid:
                    update_data['due_date'] = new_due_date
                else:
                    print(f"{Fore.RED}{error}{Style.RESET_ALL}")
                    return
            
            # Update priority
            print(f"{Fore.YELLOW}New priority (press Enter to keep current): {Style.RESET_ALL}")
            for i, priority in enumerate(PRIORITIES.keys(), 1):
                print(f"  {i}. {priority.title()}")
            
            priority_choice = input(f"{Fore.YELLOW}Enter choice (1-3): {Style.RESET_ALL}").strip()
            if priority_choice:
                if priority_choice == "1":
                    update_data['priority'] = "low"
                elif priority_choice == "2":
                    update_data['priority'] = "medium"
                elif priority_choice == "3":
                    update_data['priority'] = "high"
                else:
                    print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                    return
            
            # Update status
            print(f"{Fore.YELLOW}New status (press Enter to keep current): {Style.RESET_ALL}")
            for i, status in enumerate(STATUSES.keys(), 1):
                print(f"  {i}. {status.replace('_', ' ').title()}")
            
            status_choice = input(f"{Fore.YELLOW}Enter choice (1-3): {Style.RESET_ALL}").strip()
            if status_choice:
                if status_choice == "1":
                    update_data['status'] = "pending"
                elif status_choice == "2":
                    update_data['status'] = "in_progress"
                elif status_choice == "3":
                    update_data['status'] = "completed"
                else:
                    print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                    return
            
            # Apply updates
            if update_data:
                if self.task_manager.update_task(task_id, **update_data):
                    print(f"\n{Fore.GREEN}✓ {MESSAGES['task_updated']}{Style.RESET_ALL}")
                else:
                    print(f"\n{Fore.RED}✗ Failed to update task.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}No changes made.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Task update cancelled.{Style.RESET_ALL}")
    
    def complete_task(self, args: str = "") -> None:
        """
        Mark a task as completed.
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Complete Task ==={Style.RESET_ALL}")
        
        # Get task ID
        task_id = args.strip() if args else input(f"{Fore.YELLOW}Enter Task ID: {Style.RESET_ALL}").strip()
        
        if not task_id:
            print(f"{Fore.RED}Task ID is required.{Style.RESET_ALL}")
            return
        
        # Validate task ID
        is_valid, error = validate_task_id(task_id)
        if not is_valid:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            return
        
        # Get task
        task = self.task_manager.get_task(task_id)
        if not task:
            print(f"{Fore.RED}{MESSAGES['task_not_found']}{Style.RESET_ALL}")
            return
        
        if task.is_completed():
            print(f"{Fore.YELLOW}Task is already completed.{Style.RESET_ALL}")
            return
        
        # Confirm completion
        print(f"\n{Fore.CYAN}Task to complete:{Style.RESET_ALL}")
        self._display_task_details(task)
        
        confirm = input(f"\n{Fore.YELLOW}Mark this task as completed? (y/n): {Style.RESET_ALL}").strip()
        is_valid, error = validate_yes_no_input(confirm)
        if not is_valid:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            return
        
        if confirm.lower() in ['y', 'yes']:
            if self.task_manager.complete_task(task_id):
                print(f"\n{Fore.GREEN}✓ {MESSAGES['task_completed']}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to complete task.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Task completion cancelled.{Style.RESET_ALL}")
    
    def delete_task(self, args: str = "") -> None:
        """
        Delete a task.
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Delete Task ==={Style.RESET_ALL}")
        
        # Get task ID
        task_id = args.strip() if args else input(f"{Fore.YELLOW}Enter Task ID: {Style.RESET_ALL}").strip()
        
        if not task_id:
            print(f"{Fore.RED}Task ID is required.{Style.RESET_ALL}")
            return
        
        # Validate task ID
        is_valid, error = validate_task_id(task_id)
        if not is_valid:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            return
        
        # Get task
        task = self.task_manager.get_task(task_id)
        if not task:
            print(f"{Fore.RED}{MESSAGES['task_not_found']}{Style.RESET_ALL}")
            return
        
        # Confirm deletion
        print(f"\n{Fore.RED}Task to delete:{Style.RESET_ALL}")
        self._display_task_details(task)
        
        confirm = input(f"\n{Fore.RED}Are you sure you want to delete this task? (y/n): {Style.RESET_ALL}").strip()
        is_valid, error = validate_yes_no_input(confirm)
        if not is_valid:
            print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            return
        
        if confirm.lower() in ['y', 'yes']:
            if self.task_manager.delete_task(task_id):
                print(f"\n{Fore.GREEN}✓ {MESSAGES['task_deleted']}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ Failed to delete task.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}Task deletion cancelled.{Style.RESET_ALL}")
    

    def show_help(self, args: str = "") -> None:
        """
        Show help information.
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Available Commands ==={Style.RESET_ALL}")
        
        help_text = [
            ("add", "Add a new task"),
            ("list [filters]", "List all tasks (use --priority, --status, --due-date for filters)"),
            ("update [task_id]", "Update an existing task"),
            ("complete [task_id]", "Mark a task as completed"),
            ("delete [task_id]", "Delete a task"),
            ("help", "Show this help message"),
            ("exit", "Exit the application")
        ]
        
        for command, description in help_text:
            print(f"{Fore.GREEN}{command:<15}{Style.RESET_ALL} {description}")
        
        print(f"\n{Fore.YELLOW}Examples:{Style.RESET_ALL}")
        print(f"  list --priority high")
        print(f"  list --status pending")
        print(f"  list --due-date today")
        print(f"  update abc12345")
    
    def exit_app(self, args: str = "") -> None:
        """
        Exit the application.
        """
        print(f"\n{Fore.CYAN}{MESSAGES['goodbye']}{Style.RESET_ALL}")
        self.running = False
        self.task_manager.close()
        sys.exit(0)
    
    def _display_task_details(self, task) -> None:
        """
        Display detailed task information.
        """
        print(f"{Fore.CYAN}ID: {task.task_id}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Title: {task.title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Description: {task.description}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Due Date: {format_date(task.due_date)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Priority: {format_priority(task.priority)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Status: {format_status(task.status)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Created: {format_date(task.created_at)}{Style.RESET_ALL}")
        
        if task.is_overdue():
            print(f"{Fore.RED}Status: OVERDUE{Style.RESET_ALL}") 