"""
Main routes for the Image Processing application
"""
import os
import time
from flask import (
    Blueprint, render_template, request, jsonify, 
    send_from_directory, redirect, url_for
)
from werkzeug.utils import secure_filename
from datetime import datetime

from config.settings import (
    UPLOAD_FOLDER, RESULT_FOLDER, PLACEHOLDER_FOLDER
)
from services.task_manager import task_manager
from services.history_manager import HistoryManager
from services.image_processor import (
    analyze_image, compress_image, estimate_processing_time
)
from utils.file_utils import allowed_file, secure_file_path, cleanup_all_old_files

# Create a blueprint for main routes
main_bp = Blueprint('main', __name__)

# Create a history manager instance
history_manager = HistoryManager()

@main_bp.route('/')
def index():
    """Render the main application page"""
    return render_template('index.html')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify(success=False, error='No file part')
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify(success=False, error='No selected file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Clean up old files to prevent disk space issues
            cleanup_all_old_files()
            
            # Compress the image for faster processing
            compressed_path = compress_image(file_path, filename)
            use_compressed = compressed_path != file_path
            
            # Analyze the image
            analysis = analyze_image(compressed_path if use_compressed else file_path)
            
            return jsonify({
                'success': True, 
                'filename': filename,
                'analysis': analysis,
                'compressed': use_compressed
            })
        else:
            return jsonify(success=False, error='File type not allowed')
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify(success=False, error=f'Error uploading file: {str(e)}')

@main_bp.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@main_bp.route('/analyze/<filename>', methods=['GET'])
def analyze_image_endpoint(filename):
    """Analyze an image and return information about it"""
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify(success=False, error='Invalid filename')
        
        # Check if compressed version exists
        compressed_path = os.path.join('static', 'compressed', f"compressed_{filename}")
        if os.path.exists(compressed_path):
            image_path = compressed_path
        else:
            image_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(image_path):
            return jsonify(success=False, error='Image file not found')
        
        # Analyze the image
        analysis = analyze_image(image_path)
        return jsonify(success=True, analysis=analysis)
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return jsonify(success=False, error=f'Error analyzing image: {str(e)}')

@main_bp.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear all caches to free up memory"""
    try:
        # Clear processing tasks older than 1 hour
        removed_tasks = task_manager.cleanup_old_tasks(3600)  # 1 hour
        
        return jsonify(success=True, message=f"Cache cleared. Removed {removed_tasks} old tasks.")
    except Exception as e:
        print(f"Error clearing cache: {str(e)}")
        return jsonify(success=False, error=f'Error clearing cache: {str(e)}')

@main_bp.route('/create_placeholder', methods=['GET'])
def create_placeholder():
    """Create placeholder image directory if it doesn't exist"""
    try:
        placeholder_dir = os.path.join('static', 'img')
        os.makedirs(placeholder_dir, exist_ok=True)
        
        # Check if placeholder.png exists, if not create a simple one
        placeholder_path = os.path.join(placeholder_dir, 'placeholder.png')
        if not os.path.exists(placeholder_path):
            # Create a simple placeholder image (gray square)
            import numpy as np
            import cv2
            placeholder = np.ones((300, 300, 3), dtype=np.uint8) * 200  # Light gray
            cv2.putText(placeholder, 'No Image', (60, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            cv2.imwrite(placeholder_path, placeholder)
        
        return jsonify(success=True)
    except Exception as e:
        print(f"Error creating placeholder: {str(e)}")
        return jsonify(success=True)  # Return success even on error to prevent UI issues
