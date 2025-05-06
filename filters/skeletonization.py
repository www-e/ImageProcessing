"""
Skeletonization filter for image processing.
This module provides an optimized implementation of the morphological skeletonization operation.
"""

import cv2
import numpy as np
import gc

def apply_skeletonization(image, params=None):
    """
    Apply skeletonization morphological operation to an image.
    Skeletonization reduces binary objects to a skeleton of single-pixel width.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - max_iterations: Maximum number of iterations (default: 100)
            - threshold: Threshold for binarization (0-255, default: 127)
            - preserve_original: Whether to overlay the result on the original (default: True)
    
    Returns:
        Skeletonized image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    max_iterations = params.get('max_iterations', 100)
    threshold_value = params.get('threshold', 127)
    preserve_original = params.get('preserve_original', True)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply skeletonization
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Convert to grayscale for skeletonization
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Binarize the image
            _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Apply skeletonization
            skeleton = morphological_skeleton(binary, max_iterations)
            
            if preserve_original:
                # For better visualization, overlay the skeleton on the original
                result = image.copy()
                # Create a mask where skeleton has lines
                mask = (skeleton > 0)
                # Set those pixels to a distinct color (e.g., blue)
                result[mask] = [255, 0, 0]  # Blue color for skeleton lines
            else:
                # Create a color image from the skeleton
                result = cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)
        else:  # Grayscale image
            # Binarize the image
            _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Apply skeletonization
            result = morphological_skeleton(binary, max_iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in skeletonization: {str(e)}")
        return image

def morphological_skeleton(image, max_iterations=100):
    """
    Implements morphological skeletonization using the algorithm of successive erosions and openings.
    
    Args:
        image: Binary image
        max_iterations: Maximum number of iterations
    
    Returns:
        Skeletonized binary image
    """
    # Create a structuring element
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    
    # Make a copy of the image
    img = image.copy()
    
    # Initialize skeleton
    skeleton = np.zeros(img.shape, np.uint8)
    
    # Initialize a flag to track changes
    done = False
    iteration = 0
    
    # Repeat until the image is eroded to nothing or max iterations reached
    while not done and iteration < max_iterations:
        # Erode the image
        eroded = cv2.erode(img, kernel)
        
        # Open the eroded image
        opened = cv2.morphologyEx(eroded, cv2.MORPH_OPEN, kernel)
        
        # Subtract the opened image from the eroded image
        temp = cv2.subtract(eroded, opened)
        
        # Add the temporary image to the skeleton
        skeleton = cv2.bitwise_or(skeleton, temp)
        
        # Set the eroded image for the next iteration
        img = eroded.copy()
        
        # Check if the eroded image has any white pixels left
        done = cv2.countNonZero(img) == 0
        
        # Increment iteration counter
        iteration += 1
    
    return skeleton
