"""
File utility functions for the Image Processing application
"""
import os
import shutil
from werkzeug.utils import secure_filename
from config.settings import (
    UPLOAD_FOLDER, RESULT_FOLDER, COMPRESSED_FOLDER,
    ALLOWED_EXTENSIONS, MAX_UPLOAD_FILES, MAX_RESULT_FILES, MAX_COMPRESSED_FILES
)

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_file_path(folder, filename):
    """Create a secure file path"""
    secure_name = secure_filename(filename)
    return os.path.join(folder, secure_name)

def cleanup_old_files(folder, max_files=50):
    """Clean up old files to prevent disk space issues"""
    try:
        files = [os.path.join(folder, f) for f in os.listdir(folder) 
                if os.path.isfile(os.path.join(folder, f))]
        
        # Sort files by modification time (oldest first)
        files.sort(key=lambda x: os.path.getmtime(x))
        
        # Remove oldest files if we have more than max_files
        if len(files) > max_files:
            for file_to_remove in files[:-max_files]:
                try:
                    os.remove(file_to_remove)
                    print(f"Removed old file: {file_to_remove}")
                except Exception as e:
                    print(f"Error removing file {file_to_remove}: {str(e)}")
    except Exception as e:
        print(f"Error cleaning up old files: {str(e)}")

def cleanup_all_old_files():
    """Clean up old files in all folders"""
    cleanup_old_files(UPLOAD_FOLDER, MAX_UPLOAD_FILES)
    cleanup_old_files(RESULT_FOLDER, MAX_RESULT_FILES)
    cleanup_old_files(COMPRESSED_FOLDER, MAX_COMPRESSED_FILES)

def get_file_info(file_path):
    """Get file information"""
    try:
        if not os.path.exists(file_path):
            return None
        
        file_size = os.path.getsize(file_path)
        file_modified = os.path.getmtime(file_path)
        file_name = os.path.basename(file_path)
        
        return {
            'name': file_name,
            'size': file_size,
            'modified': file_modified,
            'path': file_path
        }
    except Exception as e:
        print(f"Error getting file info: {str(e)}")
        return None
