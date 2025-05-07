"""
Models for tracking image processing tasks
"""
import time

class ProcessingTask:
    """Class to track the status of image processing tasks"""
    def __init__(self, task_id, filename, params):
        self.task_id = task_id
        self.filename = filename
        self.params = params
        self.status = 'processing'  # 'processing', 'completed', 'failed'
        self.progress = 0  # 0-100
        self.result_filename = None
        self.error = None
        self.start_time = time.time()
        self.estimated_time = 0
        self.history_id = None
    
    def update_progress(self, progress, message=None):
        """Update the progress of the task"""
        self.progress = progress
        return self
    
    def mark_completed(self, result_filename, history_id=None):
        """Mark the task as completed"""
        self.status = 'completed'
        self.result_filename = result_filename
        self.progress = 100
        self.history_id = history_id
        return self
    
    def mark_failed(self, error):
        """Mark the task as failed"""
        self.status = 'failed'
        self.error = error
        return self
    
    def to_dict(self):
        """Convert the task to a dictionary for JSON response"""
        response = {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress
        }
        
        if self.status == 'completed':
            response['result'] = self.result_filename
            if self.history_id:
                response['history_id'] = self.history_id
        elif self.status == 'failed':
            response['error'] = self.error
        elif self.status == 'processing':
            elapsed_time = time.time() - self.start_time
            response['elapsed_time'] = elapsed_time
            response['estimated_time'] = self.estimated_time
            response['estimated_remaining'] = max(0, self.estimated_time - elapsed_time)
        
        return response
