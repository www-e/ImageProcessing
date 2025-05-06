"""
Morphological Gradient filter for image processing.
This module provides an optimized implementation of the morphological gradient operation.
"""

import cv2
import numpy as np
import gc

def apply_morphological_gradient(image, params=None):
    """
    Apply morphological gradient operation to an image.
    Morphological gradient is the difference between dilation and erosion of an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 3)
            - iterations: Number of times operation is applied (default: 1)
            - strength: Strength of the effect (0.0-2.0, default: 1.0)
    
    Returns:
        Morphological gradient image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 3)
    iterations = params.get('iterations', 1)
    strength = params.get('strength', 1.0)
    
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Create structuring element
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply morphological gradient
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            result_channels = []
            
            for channel in channels:
                # Morphological gradient is dilation minus erosion
                morph_gradient = cv2.morphologyEx(channel, cv2.MORPH_GRADIENT, kernel, iterations=iterations)
                
                # Apply strength parameter
                if strength != 1.0:
                    morph_gradient = cv2.multiply(morph_gradient, strength)
                    morph_gradient = np.clip(morph_gradient, 0, 255).astype(np.uint8)
                
                # For visualization, we can blend the gradient with the original
                # or just return the gradient itself
                result_channels.append(morph_gradient)
            
            result = cv2.merge(result_channels)
        else:  # Grayscale image
            # Morphological gradient is dilation minus erosion
            morph_gradient = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel, iterations=iterations)
            
            # Apply strength parameter
            if strength != 1.0:
                morph_gradient = cv2.multiply(morph_gradient, strength)
                morph_gradient = np.clip(morph_gradient, 0, 255).astype(np.uint8)
            
            result = morph_gradient
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in morphological gradient: {str(e)}")
        return image
