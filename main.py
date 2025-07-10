#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from cli.interface import CLIInterface
    from models.task_manager import TaskManager
    from database.mongo_client import MongoClient
    from utils.constants import MESSAGES, COLORS
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('.')
    from cli.interface import CLIInterface
    from models.task_manager import TaskManager
    from database.mongo_client import MongoClient
    from utils.constants import MESSAGES, COLORS
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def check_dependencies() -> bool:
    """
    Check if all required dependencies are available.
    """
    try:
        import pymongo
        import colorama
        import tabulate
        from dateutil import parser
        return True
    except ImportError as e:
        print(f"{Fore.RED}Missing dependency: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please install dependencies with: pip install -r requirements.txt{Style.RESET_ALL}")
        return False


def main() -> None:
    """
    Main application entry point.
    """
    try:
        # Check dependencies
        print(f"{Fore.CYAN}Checking dependencies...{Style.RESET_ALL}")
        if not check_dependencies():
            sys.exit(1)
        
        print(f"\n{Fore.GREEN}✓ All checks passed!{Style.RESET_ALL}")
        
        # Initialize task manager and CLI interface
        print(f"\n{Fore.CYAN}Initializing application...{Style.RESET_ALL}")
        task_manager = TaskManager()
        cli = CLIInterface(task_manager)
        
        # Start the application
        cli.run()
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Application interrupted by user.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{MESSAGES['goodbye']}{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please check the error message above and try again.{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main() 