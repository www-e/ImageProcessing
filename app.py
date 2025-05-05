import os
import cv2
import numpy as np
import json
import shutil
import threading
import time
import gc
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

from filters.adaptive_enhancement import AdaptiveContrastEnhancement
from utils.image_utils import load_image, save_image
from utils.history_manager import HistoryManager
from utils.image_optimizer import compress_image, estimate_processing_time, analyze_image, clear_image_cache

app = Flask(__name__)

# Configure upload and result folders
UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')
PLACEHOLDER_FOLDER = os.path.join('static', 'img')
HISTORY_FOLDER = os.path.join('static', 'history')
COMPRESSED_FOLDER = os.path.join('static', 'compressed')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(PLACEHOLDER_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}

# Initialize the enhancement algorithm
enhancer = AdaptiveContrastEnhancement()

# Initialize the history manager
history_manager = HistoryManager(HISTORY_FOLDER, RESULT_FOLDER)

# Dictionary to track processing status
processing_tasks = {}

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

def allowed_file(filename):
    """Check if the file extension is allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page."""
    # Clear image cache on page load to free memory
    clear_image_cache()
    return render_template('index.html')

@app.route('/create_placeholder')
def create_placeholder():
    """Create placeholder image if it doesn't exist."""
    placeholder_path = os.path.join(PLACEHOLDER_FOLDER, 'placeholder.png')
    loading_path = os.path.join(PLACEHOLDER_FOLDER, 'loading.png')
    
    try:
        # Create placeholder image if it doesn't exist
        if not os.path.exists(placeholder_path):
            # Create a simple placeholder image
            placeholder = np.ones((300, 400, 3), dtype=np.uint8) * 200
            cv2.putText(placeholder, 'No Image', (120, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            cv2.imwrite(placeholder_path, placeholder)
        
        # Create loading image if it doesn't exist
        if not os.path.exists(loading_path):
            # Create a simple loading image
            loading = np.ones((300, 400, 3), dtype=np.uint8) * 200
            cv2.putText(loading, 'Loading...', (120, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            cv2.imwrite(loading_path, loading)
    except Exception as e:
        print(f"Error creating placeholder images: {str(e)}")
    
    return jsonify(success=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    try:
        # Clean up old uploads to prevent disk space issues
        cleanup_old_files(UPLOAD_FOLDER, max_files=50)
        cleanup_old_files(COMPRESSED_FOLDER, max_files=50)
        
        if 'image' not in request.files:
            return jsonify(success=False, error='No file part')
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify(success=False, error='No selected file')
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify(success=False, error=f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}')
        
        # Check file content type as additional validation
        try:
            file_content = file.read(1024)  # Read first 1KB to check content
            file.seek(0)  # Reset file pointer
            
            # Simple magic number check for common image formats
            is_valid_image = False
            
            # JPEG: starts with FF D8
            if file_content.startswith(b'\xFF\xD8'):
                is_valid_image = True
            # PNG: starts with 89 50 4E 47 0D 0A 1A 0A
            elif file_content.startswith(b'\x89PNG\r\n\x1a\n'):
                is_valid_image = True
            # GIF: starts with GIF87a or GIF89a
            elif file_content.startswith((b'GIF87a', b'GIF89a')):
                is_valid_image = True
            # BMP: starts with BM
            elif file_content.startswith(b'BM'):
                is_valid_image = True
            # TIFF: starts with II or MM
            elif file_content.startswith((b'II', b'MM')):
                is_valid_image = True
                
            if not is_valid_image:
                return jsonify(success=False, error='Invalid image content')
        except Exception as e:
            print(f"Error checking file content: {str(e)}")
        
        # Secure the filename and add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{secure_filename(file.filename)}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file
        file.save(file_path)
        
        # Verify the file was saved correctly
        if not os.path.exists(file_path):
            return jsonify(success=False, error='Failed to save file')
        
        # Verify the file can be opened as an image
        try:
            test_image = cv2.imread(file_path)
            if test_image is None or test_image.size == 0:
                os.remove(file_path)  # Clean up invalid file
                return jsonify(success=False, error='File is not a valid image')
        except Exception as e:
            os.remove(file_path)  # Clean up invalid file
            return jsonify(success=False, error=f'Error opening image: {str(e)}')
        
        # Compress the image for faster processing
        try:
            compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")
            compress_image(file_path, quality=85, max_size=1920, output_path=compressed_path)
            
            # Estimate processing time
            est_time = estimate_processing_time(compressed_path)
            
            return jsonify(success=True, filename=filename, estimated_time=est_time)
        except Exception as e:
            print(f"Error compressing image: {str(e)}")
            # If compression fails, continue with original file
            return jsonify(success=True, filename=filename, estimated_time=5.0)
    except Exception as e:
        print(f"Unexpected error in upload_file: {str(e)}")
        return jsonify(success=False, error=f'Server error: {str(e)}')

@app.route('/enhance', methods=['POST'])
def enhance_image():
    """Enhance the image with the provided parameters."""
    try:
        # Clean up old results to prevent disk space issues
        cleanup_old_files(RESULT_FOLDER, max_files=100)
        
        data = request.json
        
        if not data or 'filename' not in data:
            return jsonify(success=False, error='No filename provided')
        
        filename = data['filename']
        params = data.get('params', {})
        
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify(success=False, error='Invalid filename')
            
        # Create a unique task ID
        task_id = f"task_{int(time.time() * 1000)}"
        
        # Check if compressed version exists
        compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")
        if os.path.exists(compressed_path):
            image_path = compressed_path
            use_compressed = True
        else:
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            use_compressed = False
        
        if not os.path.exists(image_path):
            return jsonify(success=False, error='Image file not found')
            
        # Create a processing task
        task = ProcessingTask(task_id, filename, params)
        task.estimated_time = estimate_processing_time(image_path, 
                                                    params.get('window_size', 15),
                                                    params.get('use_entropy', True))
        processing_tasks[task_id] = task
        
        # Start processing in a background thread
        thread = threading.Thread(target=process_image_task, 
                                 args=(task_id, image_path, filename, params, use_compressed, data))
        thread.daemon = True
        thread.start()
        
        return jsonify(success=True, task_id=task_id, estimated_time=task.estimated_time)
    except Exception as e:
        print(f"Unexpected error in enhance_image: {str(e)}")
        return jsonify(success=False, error=f'Server error: {str(e)}')

def process_image_task(task_id, image_path, filename, params, use_compressed, data):
    """Process an image enhancement task in the background."""
    task = processing_tasks.get(task_id)
    if not task:
        return
    
    try:
        # Update progress
        task.progress = 10
        
        # EXTREME PERFORMANCE OPTIMIZATION
        # Check image size and apply aggressive optimizations for large images
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
        
        # For large files, apply extreme optimizations
        if file_size_mb > 1.0 or task.estimated_time > 5.0:
            print(f"Applying extreme performance optimizations for {filename} ({file_size_mb:.2f} MB)")
            
            # 1. Force disable entropy calculation (major performance impact)
            params['use_entropy'] = False
            
            # 2. Force smaller window size for faster processing
            if 'window_size' in params and params['window_size'] > 9:
                params['window_size'] = 9
            
            # 3. Add max processing dimension to force downscaling
            params['max_processing_dimension'] = 800
            
            # 4. Simplify processing for extreme speed
            params['simplified_processing'] = True
            
            print("Optimized parameters for speed:")
            print(f"- Entropy calculation: disabled")
            print(f"- Window size: {params.get('window_size', 9)}")
            print(f"- Max dimension: {params['max_processing_dimension']}")
        
        # Load the image
        try:
            image = load_image(image_path)
            task.progress = 20
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            task.status = 'failed'
            task.error = f'Error loading image: {str(e)}'
            return
        
        # Apply enhancement
        try:
            # Apply enhancement with optimized parameters
            enhanced = enhancer.enhance(image, params)
            task.progress = 80
            
            # Free memory immediately
            del image
            gc.collect()
        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            task.status = 'failed'
            task.error = f'Error enhancing image: {str(e)}'
            return
        
        # Save the result with a unique timestamp to prevent overwriting
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        result_filename = f"enhanced_{timestamp}_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        
        try:
            save_image(enhanced, result_path)
            task.progress = 90
            
            # Free memory
            del enhanced
            gc.collect()
        except Exception as e:
            print(f"Error saving result: {str(e)}")
            task.status = 'failed'
            task.error = f'Error saving result: {str(e)}'
            return
        
        # Add to history
        try:
            # Add preset name to params if it exists in the request
            if 'preset' in data:
                params['preset'] = data['preset']
                
            history_id = history_manager.add_entry(filename, result_filename, params)
            task.history_id = history_id
            task.progress = 95
        except Exception as e:
            print(f"Error adding to history: {str(e)}")
            # Continue even if history fails
        
        # Update task status
        task.status = 'completed'
        task.result_filename = result_filename
        task.progress = 100
    except Exception as e:
        print(f"Unexpected error in process_image_task: {str(e)}")
        task.status = 'failed'
        task.error = f'Server error: {str(e)}'
    finally:
        # Make sure to clean up memory
        gc.collect()

@app.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the status of a processing task."""
    task = processing_tasks.get(task_id)
    if not task:
        return jsonify(success=False, error='Task not found')
    
    response = {
        'success': True,
        'status': task.status,
        'progress': task.progress
    }
    
    if task.status == 'completed':
        response['result'] = task.result_filename
        response['history_id'] = task.history_id
    elif task.status == 'failed':
        response['error'] = task.error
    elif task.status == 'processing':
        elapsed_time = time.time() - task.start_time
        response['elapsed_time'] = elapsed_time
        response['estimated_time'] = task.estimated_time
        response['estimated_remaining'] = max(0, task.estimated_time - elapsed_time)
    
    return jsonify(response)

# History API endpoints
@app.route('/history', methods=['GET'])
def get_history():
    """Get the enhancement history."""
    try:
        history = history_manager.get_history()
        return jsonify(success=True, history=history)
    except Exception as e:
        print(f"Error getting history: {str(e)}")
        return jsonify(success=False, error=f'Error getting history: {str(e)}')

@app.route('/history/<entry_id>', methods=['GET'])
def get_history_entry(entry_id):
    """Get a specific history entry."""
    try:
        entry = history_manager.get_entry(entry_id)
        if not entry:
            return jsonify(success=False, error='History entry not found')
        return jsonify(success=True, entry=entry)
    except Exception as e:
        print(f"Error getting history entry: {str(e)}")
        return jsonify(success=False, error=f'Error getting history entry: {str(e)}')

@app.route('/history/<entry_id>', methods=['DELETE'])
def delete_history_entry(entry_id):
    """Delete a specific history entry."""
    try:
        success = history_manager.delete_entry(entry_id)
        if not success:
            return jsonify(success=False, error='History entry not found')
        return jsonify(success=True)
    except Exception as e:
        print(f"Error deleting history entry: {str(e)}")
        return jsonify(success=False, error=f'Error deleting history entry: {str(e)}')

@app.route('/history', methods=['DELETE'])
def clear_history():
    """Clear all history entries."""
    try:
        count = history_manager.clear_history()
        return jsonify(success=True, count=count)
    except Exception as e:
        print(f"Error clearing history: {str(e)}")
        return jsonify(success=False, error=f'Error clearing history: {str(e)}')

# Utility functions
def cleanup_old_files(folder, max_files=50):
    """Clean up old files to prevent disk space issues."""
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

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@app.route('/analyze/<filename>', methods=['GET'])
def analyze_image_endpoint(filename):
    """Analyze an image and return information about it."""
    try:
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify(success=False, error='Invalid filename')
        
        # Check if compressed version exists
        compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")
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

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear all caches to free up memory."""
    try:
        # Clear image cache
        clear_image_cache()
        
        # Clear processing tasks older than 1 hour
        current_time = time.time()
        tasks_to_remove = []
        for task_id, task in processing_tasks.items():
            if current_time - task.start_time > 3600:  # 1 hour
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            processing_tasks.pop(task_id, None)
        
        # Force garbage collection
        gc.collect()
        
        return jsonify(success=True, message=f"Cache cleared. Removed {len(tasks_to_remove)} old tasks.")
    except Exception as e:
        print(f"Error clearing cache: {str(e)}")
        return jsonify(success=False, error=f'Error clearing cache: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
