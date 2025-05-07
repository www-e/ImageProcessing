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
        
        # Generate a descriptive name based on the parameters
        descriptive_name = self._generate_descriptive_name(params, result_filename)
        
        entry = {
            'id': entry_id,
            'timestamp': timestamp,
            'original_filename': original_filename,
            'result_filename': result_filename,
            'descriptive_name': descriptive_name,
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
    
    def _generate_descriptive_name(self, params, result_filename):
        """Generate a descriptive name based on the parameters"""
        # Check if it's a morphological filter
        if params.get('is_morphological') and params.get('filter_type'):
            return f"Morphological {params.get('filter_type').title()} Filter"
        
        # Check if it's using a preset
        if params.get('preset'):
            preset_name = params.get('preset').replace('_', ' ').title()
            return f"Preset: {preset_name}"
        
        # Check for multiple enhancement filters
        if 'filter_types' in params and params['filter_types']:
            filter_types = params['filter_types']
            if len(filter_types) > 1:
                return f"Multiple Filters ({len(filter_types)})"
            elif len(filter_types) == 1:
                filter_name = filter_types[0].replace('_', ' ').title()
                return f"{filter_name} Enhancement"
        
        # Default to adaptive enhancement
        if result_filename.startswith('enhanced_'):
            return "Adaptive Contrast Enhancement"
        
        # Extract from filename as fallback
        if '_' in result_filename:
            parts = result_filename.split('_')
            if len(parts) > 1:
                filter_type = parts[0].replace('morph_', '').title()
                return f"{filter_type} Filter"
        
        return "Image Enhancement"
