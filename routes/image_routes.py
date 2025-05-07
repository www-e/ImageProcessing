"""
Image processing routes for the Image Processing application
"""
import os
import time
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from config.settings import UPLOAD_FOLDER, RESULT_FOLDER
from services.task_manager import task_manager
from services.history_manager import HistoryManager
from services.image_processor import estimate_processing_time
from services.task_processor import process_image_task, process_morphological_task, process_enhancement_task

# Import image processing functions
from filters.enhancement import (
    apply_brightness_contrast, apply_exposure, apply_vibrance,
    apply_clarity, apply_shadows_highlights
)
from filters.morphological import (
    apply_dilation, apply_erosion, apply_opening, apply_closing,
    apply_tophat, apply_black_tophat, apply_morphological_gradient,
    apply_hit_miss_transform, apply_thinning, apply_thickening,
    apply_skeletonization
)

# Create a blueprint for image processing routes
image_bp = Blueprint('image', __name__)

# Create a history manager instance
history_manager = HistoryManager()

@image_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the status of a processing task"""
    try:
        task = task_manager.get_task(task_id)
        if not task:
            return jsonify(success=False, error='Task not found')
        
        # Return task data directly in the response instead of nesting it
        response = {'success': True}
        response.update(task.to_dict())
        return jsonify(response)
    except Exception as e:
        print(f"Error getting task status: {str(e)}")
        return jsonify(success=False, error=f'Error getting task status: {str(e)}')

@image_bp.route('/enhance', methods=['POST'])
def enhance_image():
    """Apply image enhancement"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify(success=False, error='No filename provided')
        
        # Validate filename to prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify(success=False, error='Invalid filename')
        
        # Check if the file exists
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        compressed_path = os.path.join('static', 'compressed', f"compressed_{filename}")
        
        if os.path.exists(compressed_path):
            use_compressed = True
            image_path = compressed_path
        else:
            use_compressed = False
        
        if not os.path.exists(image_path):
            return jsonify(success=False, error='Image file not found')
        
        # Create a task ID
        task_id = f"enhance_{int(time.time())}"
        
        # Get parameters from request
        params = data.get('params', {})
        
        # Estimate processing time
        estimated_time = estimate_processing_time(image_path)
        
        # Create a task
        task = task_manager.create_task(task_id, filename, params, estimated_time)
        
        # Start processing in a background thread
        task_manager.run_task_in_background(
            process_image_task,
            (task_id, image_path, filename, params, use_compressed, data)
        )
        
        # Return task ID for status polling
        return jsonify({
            'success': True,
            'task_id': task_id,
            'estimated_time': estimated_time
        })
    except Exception as e:
        print(f"Error enhancing image: {str(e)}")
        return jsonify(success=False, error=f'Error enhancing image: {str(e)}')

@image_bp.route('/apply_morphological', methods=['POST'])
def apply_morphological():
    """Apply morphological filter to an image"""
    try:
        data = request.json
        
        # Check if an image is uploaded
        if not os.listdir(UPLOAD_FOLDER):
            return jsonify({'error': 'No image uploaded'})
        
        # Get the latest uploaded image
        latest_file = max([os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER)], key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        # Get filter parameters
        filter_type = data.get('filter_type')
        kernel_size = data.get('kernel_size', 3)
        iterations = data.get('iterations', 1)
        
        # Additional parameters based on filter type
        strength = data.get('strength', 1.0)
        pattern = data.get('pattern', 'cross')
        threshold = data.get('threshold', 128)
        preserve_original = data.get('preserve_original', False)
        max_iterations = data.get('max_iterations', 10)
        
        # Create a task ID
        task_id = f"morph_{int(time.time())}"
        
        # Create a processing task
        params = {
            'filter_type': filter_type,
            'kernel_size': kernel_size,
            'iterations': iterations,
            'strength': strength,
            'pattern': pattern,
            'threshold': threshold,
            'preserve_original': preserve_original,
            'max_iterations': max_iterations
        }
        
        # Estimate processing time
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        estimated_time = estimate_processing_time(image_path, window_size=kernel_size)
        
        # Create a task object
        task = task_manager.create_task(task_id, filename, params, estimated_time)
        
        # Start processing in a background thread
        task_manager.run_task_in_background(
            process_morphological_task,
            (task_id, image_path, filename, params, False, data)
        )
        
        # Return task ID for status polling
        return jsonify({
            'success': True,
            'task_id': task_id,
            'estimated_time': task.estimated_time
        })
    except Exception as e:
        print(f"Error applying morphological filter: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@image_bp.route('/apply_enhancement', methods=['POST'])
def apply_enhancement():
    """Apply enhancement filter to an image"""
    try:
        data = request.json
        
        # Check if an image is uploaded
        if not os.listdir(UPLOAD_FOLDER):
            return jsonify({'error': 'No image uploaded'})
        
        # Get the latest uploaded image
        latest_file = max([os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER)], key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        # Get filter parameters
        filter_type = data.get('filter_type')
        
        # Create a task ID
        task_id = f"enhance_{int(time.time())}"
        
        # Create a processing task with filter-specific parameters
        params = {'filter_type': filter_type}
        
        # Add parameters based on filter type
        if filter_type == 'brightness_contrast':
            params['brightness'] = data.get('brightness', 0.0)
            params['contrast'] = data.get('contrast', 1.0)
        elif filter_type == 'exposure':
            params['exposure'] = data.get('exposure', 0.0)
            params['highlights'] = data.get('highlights', 0.0)
            params['shadows'] = data.get('shadows', 0.0)
        elif filter_type == 'vibrance':
            params['vibrance'] = data.get('vibrance', 0.0)
            params['saturation'] = data.get('saturation', 0.0)
        elif filter_type == 'clarity':
            params['clarity'] = data.get('clarity', 0.0)
            params['edge_kernel'] = data.get('edge_kernel', 3)
            params['edge_scale'] = data.get('edge_scale', 1.0)
            params['apply_clahe'] = data.get('apply_clahe', True)
            params['clahe_clip'] = data.get('clahe_clip', 2.0)
            params['clahe_grid'] = data.get('clahe_grid', 8)
        elif filter_type == 'shadows_highlights':
            params['shadows_recovery'] = data.get('shadows_recovery', 0.0)
            params['highlights_recovery'] = data.get('highlights_recovery', 0.0)
            params['mid_tone_contrast'] = data.get('mid_tone_contrast', 0.0)
        
        # Estimate processing time
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        estimated_time = estimate_processing_time(image_path, window_size=5)
        
        # Create a task object
        task = task_manager.create_task(task_id, filename, params, estimated_time)
        
        # Start processing in a background thread
        task_manager.run_task_in_background(
            process_enhancement_task,
            (task_id, image_path, filename, params, False, data)
        )
        
        # Return task ID for status polling
        return jsonify({
            'success': True,
            'task_id': task_id,
            'estimated_time': task.estimated_time
        })
    except Exception as e:
        print(f"Error applying enhancement filter: {str(e)}")
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})
