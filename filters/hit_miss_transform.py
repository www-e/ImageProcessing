"""
Hit-or-Miss Transform filter for image processing.
This module provides an optimized implementation of the hit-or-miss transform operation.
"""

import cv2
import numpy as np
import gc

def apply_hit_miss_transform(image, params=None):
    """
    Apply hit-or-miss transform to an image.
    Hit-or-miss transform is used for shape detection in binary images.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 3)
            - iterations: Number of times operation is applied (default: 1)
            - pattern: Pattern type for the structuring element (default: 'cross')
                Options: 'cross', 'horizontal', 'vertical', 'diagonal'
    
    Returns:
        Hit-or-miss transformed image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 3)
    iterations = params.get('iterations', 1)
    pattern = params.get('pattern', 'cross')
    
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Create structuring elements based on pattern
    if pattern == 'horizontal':
        kernel1 = np.zeros((kernel_size, kernel_size), np.uint8)
        kernel1[kernel_size//2, :] = 1
        kernel2 = np.zeros((kernel_size, kernel_size), np.uint8)
        kernel2[0, :] = 1
        kernel2[-1, :] = 1
    elif pattern == 'vertical':
        kernel1 = np.zeros((kernel_size, kernel_size), np.uint8)
        kernel1[:, kernel_size//2] = 1
        kernel2 = np.zeros((kernel_size, kernel_size), np.uint8)
        kernel2[:, 0] = 1
        kernel2[:, -1] = 1
    elif pattern == 'diagonal':
        kernel1 = np.zeros((kernel_size, kernel_size), np.uint8)
        np.fill_diagonal(kernel1, 1)
        kernel2 = np.zeros((kernel_size, kernel_size), np.uint8)
        np.fill_diagonal(np.fliplr(kernel2), 1)
    else:  # Default to cross pattern
        kernel1 = np.zeros((kernel_size, kernel_size), np.uint8)
        kernel1[kernel_size//2, :] = 1
        kernel1[:, kernel_size//2] = 1
        kernel2 = np.zeros((kernel_size, kernel_size), np.uint8)
        kernel2[0, 0] = 1
        kernel2[0, -1] = 1
        kernel2[-1, 0] = 1
        kernel2[-1, -1] = 1
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply hit-or-miss transform
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Convert to grayscale for hit-miss transform
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Binarize the image for hit-miss transform
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Apply hit-miss transform
            hit_miss = cv2.morphologyEx(binary, cv2.MORPH_HITMISS, kernel1, iterations=iterations)
            
            # For visualization, create a color result
            result = np.zeros_like(image)
            # Set detected points to white
            mask = hit_miss > 0
            result[mask] = [255, 255, 255]
            
            # For better visualization, blend with original
            alpha = 0.7
            result = cv2.addWeighted(image, alpha, result, 1-alpha, 0)
        else:  # Grayscale image
            # Binarize the image for hit-miss transform
            _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            
            # Apply hit-miss transform
            hit_miss = cv2.morphologyEx(binary, cv2.MORPH_HITMISS, kernel1, iterations=iterations)
            
            # Scale result to visible range
            result = hit_miss * 255
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in hit-miss transform: {str(e)}")
        return image
