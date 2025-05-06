"""
Thinning filter for image processing.
This module provides an optimized implementation of the morphological thinning operation.
"""

import cv2
import numpy as np
import gc

def apply_thinning(image, params=None):
    """
    Apply thinning morphological operation to an image.
    Thinning reduces binary objects to lines of single-pixel thickness.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - iterations: Maximum number of iterations (default: 10)
            - threshold: Threshold for binarization (0-255, default: 127)
            - preserve_original: Whether to overlay the result on the original (default: True)
    
    Returns:
        Thinned image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    max_iterations = params.get('iterations', 10)
    threshold_value = params.get('threshold', 127)
    preserve_original = params.get('preserve_original', True)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply thinning
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Convert to grayscale for thinning
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Binarize the image
            _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Apply thinning using Zhang-Suen algorithm
            thinned = zhang_suen_thinning(binary, max_iterations)
            
            if preserve_original:
                # For better visualization, overlay the thinning result on the original
                result = image.copy()
                # Create a mask where thinned image has lines
                mask = (thinned > 0)
                # Set those pixels to a distinct color (e.g., red)
                result[mask] = [0, 0, 255]  # Red color for thinned lines
            else:
                # Create a color image from the thinned result
                result = cv2.cvtColor(thinned, cv2.COLOR_GRAY2BGR)
        else:  # Grayscale image
            # Binarize the image
            _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)
            
            # Apply thinning using Zhang-Suen algorithm
            result = zhang_suen_thinning(binary, max_iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in thinning: {str(e)}")
        return image

def zhang_suen_thinning(image, max_iterations=10):
    """
    Implements the Zhang-Suen thinning algorithm.
    
    Args:
        image: Binary image
        max_iterations: Maximum number of iterations
    
    Returns:
        Thinned binary image
    """
    # Make a copy of the image
    skeleton = image.copy()
    
    # Convert to binary (0 and 1)
    skeleton = skeleton // 255
    
    # Initialize change flag
    changing = True
    iteration = 0
    
    # Repeat until no change occurs or max iterations reached
    while changing and iteration < max_iterations:
        iteration += 1
        changing = False
        
        # First sub-iteration
        changing1 = zhang_suen_sub_iteration(skeleton, 0)
        
        # Second sub-iteration
        changing2 = zhang_suen_sub_iteration(skeleton, 1)
        
        # Update changing flag
        changing = changing1 or changing2
    
    # Convert back to 0-255 range
    return skeleton * 255

def zhang_suen_sub_iteration(image, step):
    """
    Performs one sub-iteration of the Zhang-Suen thinning algorithm.
    
    Args:
        image: Binary image (0 and 1)
        step: 0 for first sub-iteration, 1 for second
    
    Returns:
        Whether any pixel was changed
    """
    # Create a copy to store changes
    marker = np.zeros_like(image)
    
    # Get image dimensions
    rows, cols = image.shape
    
    # Flag to track changes
    changed = False
    
    # Process each pixel
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            # Skip background pixels
            if image[i, j] == 0:
                continue
            
            # Get 8-neighbors
            p2 = image[i-1, j]
            p3 = image[i-1, j+1]
            p4 = image[i, j+1]
            p5 = image[i+1, j+1]
            p6 = image[i+1, j]
            p7 = image[i+1, j-1]
            p8 = image[i, j-1]
            p9 = image[i-1, j-1]
            
            # Calculate A(P1) - number of 0-1 transitions in the ordered sequence
            neighbors = [p2, p3, p4, p5, p6, p7, p8, p9, p2]
            transitions = sum((neighbors[k] == 0 and neighbors[k+1] == 1) for k in range(8))
            
            # Calculate B(P1) - number of non-zero neighbors
            non_zero = sum(neighbors[:-1])
            
            # Conditions for deletion in first sub-iteration
            if step == 0:
                condition = (p2 * p4 * p6 == 0) and (p4 * p6 * p8 == 0)
            # Conditions for deletion in second sub-iteration
            else:
                condition = (p2 * p4 * p8 == 0) and (p2 * p6 * p8 == 0)
            
            # Mark for deletion if all conditions are met
            if (2 <= non_zero <= 6) and (transitions == 1) and condition:
                marker[i, j] = 1
                changed = True
    
    # Apply deletion
    image[marker == 1] = 0
    
    return changed
