"""
History management service for the Image Processing application
"""
import os
import json
import time
import uuid
import shutil
from datetime import datetime
from config.settings import HISTORY_FOLDER

class HistoryManager:
    """Class to manage image enhancement history"""
    def __init__(self, history_folder=HISTORY_FOLDER):
        self.history_folder = history_folder
        os.makedirs(self.history_folder, exist_ok=True)
        self.history_file = os.path.join(self.history_folder, 'history.json')
        self.load_history()
    
    def load_history(self):
        """Load history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            self.history = []
    
    def save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {str(e)}")
    
    def add_entry(self, original_filename, result_filename, params):
        """Add a new entry to the history"""
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        entry = {
            'id': entry_id,
            'timestamp': timestamp,
            'original_filename': original_filename,
            'result_filename': result_filename,
            'params': params
        }
        
        self.history.append(entry)
        self.save_history()
        return entry_id
    
    def get_history(self):
        """Get all history entries"""
        return self.history
    
    def get_entry(self, entry_id):
        """Get a specific history entry"""
        for entry in self.history:
            if entry['id'] == entry_id:
                return entry
        return None
    
    def delete_entry(self, entry_id):
        """Delete a specific history entry"""
        for i, entry in enumerate(self.history):
            if entry['id'] == entry_id:
                del self.history[i]
                self.save_history()
                return True
        return False
    
    def clear_history(self):
        """Clear all history entries"""
        count = len(self.history)
        self.history = []
        self.save_history()
        return count
