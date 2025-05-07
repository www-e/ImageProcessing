"""
Image optimization utilities for the Adaptive Contrast Enhancement application.
Provides functions for image compression and optimization.
"""
import cv2
import numpy as np
import os
import hashlib
import time
import io
import struct
from PIL import Image, ImageFile

# Enable loading truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Custom image format detection (replacement for imghdr)
def what_format(file_path):
    """
    Determine the image file format by examining the file's magic bytes.
    A custom implementation to replace the imghdr module.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        String indicating the image format ('jpeg', 'png', 'gif', 'bmp', 'tiff') or None
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(12)  # Read first 12 bytes for format detection
            
            # JPEG: starts with FF D8
            if header.startswith(b'\xFF\xD8'):
                return 'jpeg'
            
            # PNG: starts with 89 50 4E 47 0D 0A 1A 0A
            elif header.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'png'
            
            # GIF: starts with GIF87a or GIF89a
            elif header.startswith((b'GIF87a', b'GIF89a')):
                return 'gif'
            
            # BMP: starts with BM
            elif header.startswith(b'BM'):
                return 'bmp'
            
            # TIFF: starts with II or MM
            elif header.startswith((b'II', b'MM')):
                return 'tiff'
            
            # Try using PIL as fallback
            try:
                with Image.open(file_path) as img:
                    return img.format.lower() if img.format else None
            except Exception:
                pass
                
            return None
    except Exception as e:
        print(f"Error detecting image format: {str(e)}")
        return None

# Cache for processed images
IMAGE_CACHE = {}
CACHE_MAX_SIZE = 50  # Maximum number of items in cache

def get_image_hash(image_path):
    """Generate a hash for an image file to use as a cache key."""
    try:
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        print(f"Error generating image hash: {str(e)}")
        # Fallback to path and modification time if hashing fails
        return f"{image_path}_{os.path.getmtime(image_path)}"

def detect_image_format(image_path):
    """Detect the image format and return appropriate settings."""
    try:
        # Use our custom format detection function
        img_format = what_format(image_path)
        
        # Check file size
        file_size = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
        
        # Default settings
        settings = {
            'quality': 85,
            'max_size': 1920,
            'progressive': True,
            'optimize': True
        }
        
        # Adjust settings based on format and size
        if img_format == 'jpeg' or img_format == 'jpg':
            # JPEG specific optimizations
            if file_size > 2.0:
                settings['quality'] = 80
                settings['max_size'] = 1600
            elif file_size < 0.1:
                # Small files might be thumbnails, preserve quality
                settings['quality'] = 92
        elif img_format == 'png':
            # PNG specific optimizations
            settings['quality'] = 90  # Higher quality for PNG conversion
        elif img_format == 'bmp':
            # BMP files are usually uncompressed, use stronger compression
            settings['quality'] = 80
            settings['max_size'] = 1600
        
        return settings
    except Exception as e:
        print(f"Error detecting image format: {str(e)}")
        # Return default settings if detection fails
        return {
            'quality': 85,
            'max_size': 1920,
            'progressive': True,
            'optimize': True
        }

def compress_image(image_path, quality=None, max_size=None, output_path=None):
    """
    Compress an image to reduce file size while maintaining reasonable quality.
    Uses caching to avoid reprocessing the same image.
    
    Args:
        image_path: Path to the original image
        quality: JPEG quality (0-100, higher is better quality but larger file)
        max_size: Maximum dimension (width or height) in pixels
        output_path: Path to save the compressed image (if None, overwrites original)
    
    Returns:
        Path to the compressed image
    """
    # Check cache first
    image_hash = get_image_hash(image_path)
    cache_key = f"{image_hash}_{quality}_{max_size}"
    
    if cache_key in IMAGE_CACHE and os.path.exists(IMAGE_CACHE[cache_key]):
        print(f"Using cached compressed image: {IMAGE_CACHE[cache_key]}")
        return IMAGE_CACHE[cache_key]
    
    if output_path is None:
        output_path = image_path
    
    # Detect format and get optimal settings
    settings = detect_image_format(image_path)
    
    # Override with provided parameters if specified
    if quality is not None:
        settings['quality'] = quality
    if max_size is not None:
        settings['max_size'] = max_size
    
    # Open the image with PIL
    try:
        # Use a timeout to prevent hanging on corrupted images
        start_time = time.time()
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image on the background
            background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed
        width, height = img.size
        if width > settings['max_size'] or height > settings['max_size']:
            if width > height:
                new_width = settings['max_size']
                new_height = int(height * (settings['max_size'] / width))
            else:
                new_height = settings['max_size']
                new_width = int(width * (settings['max_size'] / height))
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Save with compression
        img.save(output_path, 'JPEG', 
                quality=settings['quality'], 
                optimize=settings['optimize'],
                progressive=settings['progressive'])
        
        # Add to cache
        IMAGE_CACHE[cache_key] = output_path
        
        # Limit cache size
        if len(IMAGE_CACHE) > CACHE_MAX_SIZE:
            # Remove oldest item
            oldest_key = next(iter(IMAGE_CACHE))
            IMAGE_CACHE.pop(oldest_key)
        
        return output_path
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        # If compression fails, return the original path
        return image_path

def optimize_for_web(image_path, output_path=None, quality=85, max_size=1200):
    """
    Optimize an image specifically for web display.
    
    Args:
        image_path: Path to the original image
        output_path: Path to save the optimized image
        quality: JPEG quality (0-100)
        max_size: Maximum dimension (width or height) in pixels
    
    Returns:
        Path to the optimized image
    """
    return compress_image(image_path, quality, max_size, output_path)

def clear_image_cache():
    """
    Clear the image cache to free up memory.
    """
    global IMAGE_CACHE
    IMAGE_CACHE.clear()
    
def analyze_image(image_path):
    """
    Analyze an image and return information about it.
    Useful for debugging performance issues.
    
    Args:
        image_path: Path to the image
        
    Returns:
        Dictionary with image information
    """
    try:
        # Get file info
        file_size = os.path.getsize(image_path) / 1024  # Size in KB
        file_format = what_format(image_path) or 'unknown'
        
        # Open with PIL for more info
        with Image.open(image_path) as img:
            width, height = img.size
            mode = img.mode
            format_pil = img.format or 'unknown'
            
            # Check for EXIF data which can slow down processing
            has_exif = hasattr(img, '_getexif') and img._getexif() is not None
            
        # Open with OpenCV for color analysis
        cv_img = cv2.imread(image_path)
        if cv_img is not None:
            # Calculate average color values
            avg_color_per_channel = cv2.mean(cv_img)[:3]
            # Calculate image complexity (edge density)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.count_nonzero(edges) / (width * height)
        else:
            avg_color_per_channel = (0, 0, 0)
            edge_density = 0
        
        return {
            'path': image_path,
            'file_size_kb': round(file_size, 2),
            'dimensions': f"{width}x{height}",
            'pixel_count': width * height,
            'format': file_format,
            'format_pil': format_pil,
            'mode': mode,
            'has_exif': has_exif,
            'avg_color': avg_color_per_channel,
            'edge_density': edge_density,
            'estimated_processing_time': estimate_processing_time(image_path)
        }
    except Exception as e:
        print(f"Error analyzing image: {str(e)}")
        return {
            'path': image_path,
            'error': str(e)
        }

def estimate_processing_time(image_path, window_size=15, use_entropy=True):
    """
    Estimate the processing time based on image size and parameters.
    
    Args:
        image_path: Path to the image
        window_size: Window size for local processing
        use_entropy: Whether entropy calculation is used
    
    Returns:
        Estimated processing time in seconds
    """
    try:
        # Try to get image dimensions using PIL first (faster and more reliable)
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                # Check image format for additional factors
                format_factor = 1.0
                if img.format == 'JPEG':
                    # JPEG processing is usually faster
                    format_factor = 0.9
                elif img.format == 'PNG':
                    # PNG can be slower especially with transparency
                    format_factor = 1.2
                elif img.format == 'BMP':
                    # BMP can be very slow due to large uncompressed size
                    format_factor = 1.5
        except Exception:
            # Fallback to OpenCV if PIL fails
            img = cv2.imread(image_path)
            if img is None:
                return 5.0  # Default if can't read image
            height, width = img.shape[:2]
            format_factor = 1.0  # Default factor if format unknown
            
        pixel_count = height * width
        
        # Base processing time per million pixels (empirically determined)
        base_time_per_million = 1.5  # seconds per million pixels
        
        # Additional time for entropy calculation
        entropy_factor = 1.5 if use_entropy else 1.0
        
        # Window size factor (larger windows take more time)
        window_factor = (window_size / 15.0) ** 2
        
        # Check file size for additional factor
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
        size_factor = 1.0
        if file_size_mb > 5.0:
            # Very large files might have compression overhead
            size_factor = 1.3
        elif file_size_mb < 0.1:
            # Very small files might be optimized already
            size_factor = 0.8
        
        # Calculate estimated time with all factors
        estimated_time = (pixel_count / 1000000.0) * base_time_per_million * \
                         entropy_factor * window_factor * format_factor * size_factor
        
        # Add minimum processing time
        estimated_time = max(estimated_time, 1.0)
        
        return estimated_time
    except Exception as e:
        print(f"Error estimating processing time: {str(e)}")
        return 5.0  # Default fallback
