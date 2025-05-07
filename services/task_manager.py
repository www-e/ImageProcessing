"""
Task management service for the Image Processing application
"""
import time
import threading
import gc
from datetime import datetime
from models.task import ProcessingTask

# Dictionary to store processing tasks
processing_tasks = {}

class TaskManager:
    """Class to manage image processing tasks"""
    def __init__(self):
        self.processing_tasks = {}
    
    def create_task(self, task_id, filename, params, estimated_time=0):
        """Create a new processing task"""
        task = ProcessingTask(task_id, filename, params)
        task.estimated_time = estimated_time
        self.processing_tasks[task_id] = task
        return task
    
    def get_task(self, task_id):
        """Get a task by ID"""
        return self.processing_tasks.get(task_id)
    
    def update_task_progress(self, task_id, progress):
        """Update the progress of a task"""
        task = self.get_task(task_id)
        if task:
            task.progress = progress
        return task
    
    def mark_task_completed(self, task_id, result_filename, history_id=None):
        """Mark a task as completed"""
        task = self.get_task(task_id)
        if task:
            task.mark_completed(result_filename, history_id)
        return task
    
    def mark_task_failed(self, task_id, error):
        """Mark a task as failed"""
        task = self.get_task(task_id)
        if task:
            task.mark_failed(error)
        return task
    
    def cleanup_old_tasks(self, max_age_seconds=3600):
        """Remove old tasks to free up memory"""
        current_time = time.time()
        tasks_to_remove = []
        
        for task_id, task in self.processing_tasks.items():
            if current_time - task.start_time > max_age_seconds:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            self.processing_tasks.pop(task_id, None)
        
        # Force garbage collection
        gc.collect()
        
        return len(tasks_to_remove)
    
    def run_task_in_background(self, target, args):
        """Run a task in a background thread"""
        thread = threading.Thread(target=target, args=args)
        thread.daemon = True
        thread.start()
        return thread

# Create a global task manager instance
task_manager = TaskManager()
