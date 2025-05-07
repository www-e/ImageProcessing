"""
Image processing service for the Image Processing application
"""
import os
import cv2
import numpy as np
import time
import gc
from datetime import datetime
from config.settings import (
    UPLOAD_FOLDER, RESULT_FOLDER, COMPRESSED_FOLDER,
    DEFAULT_MAX_PROCESSING_DIMENSION, ENABLE_PERFORMANCE_OPTIMIZATIONS
)

# Import optimization utilities
from services.image_optimization import (
    load_image as utils_load_image,
    save_image as utils_save_image,
    compress_image as utils_compress_image,
    analyze_image as utils_analyze_image,
    estimate_processing_time as utils_estimate_processing_time,
    clear_image_cache as utils_clear_image_cache
)

# Dictionary to store loaded images for caching
image_cache = {}

def load_image(image_path):
    """Load an image from file or cache"""
    # Use the optimized load_image function from utils
    if image_path in image_cache:
        return image_cache[image_path].copy()
    
    try:
        # Use the optimized version from utils
        image = utils_load_image(image_path)
        
        # Cache the image for future use
        image_cache[image_path] = image.copy()
        
        return image
    except Exception as e:
        print(f"Error loading image with optimized function: {str(e)}")
        # Fallback to standard OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Cache the image for future use
        image_cache[image_path] = image.copy()
        
        return image

def save_image(image, output_path):
    """Save an image to file"""
    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    
    try:
        # Use the optimized version from utils
        return utils_save_image(image, output_path)
    except Exception as e:
        print(f"Error saving image with optimized function: {str(e)}")
        # Fallback to standard OpenCV
        success = cv2.imwrite(output_path, image)
        if not success:
            raise ValueError(f"Failed to save image to {output_path}")
        
        return output_path

def clear_image_cache():
    """Clear the image cache to free memory"""
    global image_cache
    image_cache.clear()
    
    # Also clear the utils cache
    try:
        utils_clear_image_cache()
    except Exception as e:
        print(f"Error clearing utils image cache: {str(e)}")
    
    gc.collect()
    return True

def compress_image(image_path, filename, max_dimension=DEFAULT_MAX_PROCESSING_DIMENSION):
    """Compress an image for faster processing"""
    try:
        # Use the optimized version from utils
        compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")
        result = utils_compress_image(image_path, quality=85, max_size=max_dimension, output_path=compressed_path)
        
        if result and os.path.exists(compressed_path):
            return compressed_path
    except Exception as e:
        print(f"Error compressing image with optimized function: {str(e)}")
    
    # Fallback to standard compression
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Calculate new dimensions while preserving aspect ratio
        height, width = image.shape[:2]
        if max(height, width) > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            # Resize the image
            compressed = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Save compressed image
            compressed_path = os.path.join(COMPRESSED_FOLDER, f"compressed_{filename}")
            cv2.imwrite(compressed_path, compressed)
            
            return compressed_path
        
        return image_path
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        return image_path

def estimate_processing_time(image_path, window_size=5):
    """Estimate processing time based on image size"""
    try:
        # Use the optimized version from utils
        use_entropy = not ENABLE_PERFORMANCE_OPTIMIZATIONS  # Disable entropy for performance
        return utils_estimate_processing_time(image_path, window_size=window_size, use_entropy=use_entropy)
    except Exception as e:
        print(f"Error estimating processing time with optimized function: {str(e)}")
    
    # Fallback to standard estimation
    try:
        # Get image dimensions
        image = cv2.imread(image_path)
        if image is None:
            return 5.0  # Default if image can't be loaded
        
        height, width = image.shape[:2]
        pixel_count = height * width
        
        # Base time estimate (empirically determined)
        base_time = 1.0
        
        # Scale based on pixel count and window size
        # This is a simplified model and should be adjusted based on actual performance
        time_estimate = base_time + (pixel_count / 1000000) * (window_size / 5) * 2
        
        # Add some buffer
        return max(2.0, time_estimate * 1.2)
    except Exception as e:
        print(f"Error estimating processing time: {str(e)}")
        return 5.0  # Default fallback

def analyze_image(image_path):
    """Analyze an image and return information about it"""
    try:
        # Use the optimized version from utils
        analysis = utils_analyze_image(image_path)
        if analysis and 'error' not in analysis:
            # Convert numpy booleans to Python booleans for JSON serialization
            if 'is_color' in analysis:
                analysis['is_color'] = bool(analysis['is_color'])
            if 'needs_enhancement' in analysis:
                analysis['needs_enhancement'] = bool(analysis['needs_enhancement'])
            return analysis
    except Exception as e:
        print(f"Error analyzing image with optimized function: {str(e)}")
    
    # Fallback to standard analysis
    try:
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Failed to load image'}
        
        height, width = image.shape[:2]
        channels = 1 if len(image.shape) == 2 else image.shape[2]
        file_size = os.path.getsize(image_path) / 1024  # KB
        
        # Calculate average brightness
        if channels == 1:
            avg_brightness = np.mean(image)
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
        
        # Calculate contrast (standard deviation of grayscale image)
        if channels == 1:
            contrast = np.std(image)
        else:
            contrast = np.std(gray)
        
        # Check if image is color or grayscale
        is_color = bool(channels > 1 and not np.allclose(image[:,:,0], image[:,:,1]) and not np.allclose(image[:,:,0], image[:,:,2]))
        
        # Estimate if image needs enhancement
        needs_enhancement = bool(avg_brightness < 100 or contrast < 40 or avg_brightness > 200)
        
        # Recommended enhancement
        recommended_enhancement = None
        if avg_brightness < 100:
            recommended_enhancement = 'brightness'
        elif contrast < 40:
            recommended_enhancement = 'contrast'
        elif avg_brightness > 200:
            recommended_enhancement = 'exposure'
        
        return {
            'dimensions': f"{width}x{height}",
            'width': width,
            'height': height,
            'channels': channels,
            'file_size_kb': round(file_size, 2),
            'avg_brightness': round(avg_brightness, 2),
            'contrast': round(contrast, 2),
            'is_color': is_color,
            'needs_enhancement': needs_enhancement,
            'recommended_enhancement': recommended_enhancement
        }
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {'error': str(e)}
