"""
Thickening filter for image processing.
This module provides an optimized implementation of the morphological thickening operation.
"""

import cv2
import numpy as np
import gc

def apply_thickening(image, params=None):
    """
    Apply thickening morphological operation to an image.
    Thickening adds pixels to the boundaries of objects in a binary image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - iterations: Number of iterations (default: 3)
            - threshold: Threshold for binarization (0-255, default: 127)
            - preserve_original: Whether to overlay the result on the original (default: True)
    
    Returns:
        Thickened image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    iterations = params.get('iterations', 3)
    threshold_value = params.get('threshold', 127)
    preserve_original = params.get('preserve_original', True)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply thickening
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Convert to grayscale for thickening
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Binarize the image
            _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Apply thickening
            thickened = morphological_thickening(binary, iterations)
            
            if preserve_original:
                # For better visualization, overlay the thickening result on the original
                result = image.copy()
                # Create a mask where thickened image has added pixels
                # (pixels that are in thickened but not in binary)
                mask = (thickened > 0) & (binary == 0)
                # Set those pixels to a distinct color (e.g., green)
                result[mask] = [0, 255, 0]  # Green color for thickened areas
            else:
                # Create a color image from the thickened result
                result = cv2.cvtColor(thickened, cv2.COLOR_GRAY2BGR)
        else:  # Grayscale image
            # Binarize the image
            _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Apply thickening
            result = morphological_thickening(binary, iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in thickening: {str(e)}")
        return image

def morphological_thickening(image, iterations=3):
    """
    Implements morphological thickening.
    
    Args:
        image: Binary image
        iterations: Number of iterations
    
    Returns:
        Thickened binary image
    """
    # Create structuring elements for thickening
    # Thickening uses hit-or-miss transform with specific structuring elements
    
    # Define a list of structuring element pairs for different directions
    # Each direction contributes to thickening from that side
    se_pairs = []
    
    # North direction
    se_north_hit = np.array([
        [0, 0, 0],
        [0, 1, 0],
        [1, 1, 1]
    ], dtype=np.uint8)
    se_north_miss = np.array([
        [1, 1, 1],
        [0, 0, 0],
        [0, 0, 0]
    ], dtype=np.uint8)
    se_pairs.append((se_north_hit, se_north_miss))
    
    # South direction
    se_south_hit = np.array([
        [1, 1, 1],
        [0, 1, 0],
        [0, 0, 0]
    ], dtype=np.uint8)
    se_south_miss = np.array([
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1]
    ], dtype=np.uint8)
    se_pairs.append((se_south_hit, se_south_miss))
    
    # East direction
    se_east_hit = np.array([
        [1, 0, 0],
        [1, 1, 0],
        [1, 0, 0]
    ], dtype=np.uint8)
    se_east_miss = np.array([
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1]
    ], dtype=np.uint8)
    se_pairs.append((se_east_hit, se_east_miss))
    
    # West direction
    se_west_hit = np.array([
        [0, 0, 1],
        [0, 1, 1],
        [0, 0, 1]
    ], dtype=np.uint8)
    se_west_miss = np.array([
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0]
    ], dtype=np.uint8)
    se_pairs.append((se_west_hit, se_west_miss))
    
    # Make a copy of the image
    result = image.copy()
    
    # Apply thickening for the specified number of iterations
    for _ in range(iterations):
        for hit_kernel, miss_kernel in se_pairs:
            # Create a kernel for hit-or-miss transform
            # OpenCV doesn't directly support the hit-miss with two kernels
            # So we'll implement it manually
            
            # Erode with hit kernel
            hit = cv2.erode(result, hit_kernel)
            
            # Erode inverted image with miss kernel
            miss = cv2.erode(255 - result, miss_kernel)
            
            # Combine hit and miss
            hitmiss = cv2.bitwise_and(hit, miss)
            
            # Add the hit-miss result to the original image for thickening
            result = cv2.bitwise_or(result, hitmiss)
    
    return result
