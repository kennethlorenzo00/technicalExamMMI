"""
Handles all database operations 
"""

import pymongo
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, DuplicateKeyError
try:
    from ..utils.constants import DATABASE_CONFIG, MESSAGES
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append('.')
    from utils.constants import DATABASE_CONFIG, MESSAGES


class MongoClient:
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or DATABASE_CONFIG
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self) -> bool:
        try:
            self.client = pymongo.MongoClient(
                host=self.config['host'],
                port=self.config['port'],
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10, 
                minPoolSize=1
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[self.config['database']]
            self.collection = self.db[self.config['collection']]
            
            # Create indexes
            self._create_indexes()
            
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"{MESSAGES['database_error']} {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected database error: {str(e)}")
            return False
    
    def _create_indexes(self) -> None:
        """
        Create database indexes for better query performance.
        """
        try:
            if self.collection is None:
                return
                
            # Index on task_id for fast lookups
            self.collection.create_index("task_id", unique=True)
            
            # Index on status for filtering
            self.collection.create_index("status")
            
            # Index on priority for sorting
            self.collection.create_index("priority")
            
            # Index on due_date for date-based queries
            self.collection.create_index("due_date")
            
            # Compound index for status and priority
            self.collection.create_index([("status", 1), ("priority", -1)])
            
        except Exception as e:
            print(f"Warning: Could not create indexes: {str(e)}")
    
    def is_connected(self) -> bool:
        """
        Check if database connection is active.
        """
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
            return False
        except:
            return False
    
    def insert_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Insert a new task into the database.
        """
        try:
            if not self.is_connected():
                if not self._connect():
                    return False
            
            if self.collection is None:
                return False
            
            # Add timestamps
            task_data['created_at'] = datetime.now()
            task_data['updated_at'] = datetime.now()
            
            result = self.collection.insert_one(task_data)
            return result.inserted_id is not None
            
        except DuplicateKeyError:
            print("Error: Task ID already exists.")
            return False
        except Exception as e:
            print(f"Error inserting task: {str(e)}")
            return False
    
    def find_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Retrieve all tasks from the database.
        """
        try:
            if not self.is_connected():
                if not self._connect():
                    return []
            
            if self.collection is None:
                return []
            
            cursor = self.collection.find({}).sort([("created_at", -1)])
            return list(cursor)
            
        except Exception as e:
            print(f"Error retrieving tasks: {str(e)}")
            return []
    
    
    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an existing task.
        """
        try:
            if not self.is_connected():
                if not self._connect():
                    return False
            
            if self.collection is None:
                return False
            
            # Add update timestamp
            update_data['updated_at'] = datetime.now()
            
            result = self.collection.update_one(
                {"task_id": task_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating task: {str(e)}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from the database.
        """
        try:
            if not self.is_connected():
                if not self._connect():
                    return False
            
            if self.collection is None:
                return False
            
            result = self.collection.delete_one({"task_id": task_id})
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting task: {str(e)}")
            return False
    
    
    def close_connection(self) -> None:
        """
        Close the database connection.
        """
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            print(f"Error closing connection: {str(e)}")
    
    def __del__(self):
        """
        Destructor to ensure connection is closed.
        """
        self.close_connection() 