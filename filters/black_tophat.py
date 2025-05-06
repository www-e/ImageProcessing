"""
Black Top-Hat morphological filter for image processing.
This module provides an optimized implementation of the black top-hat operation.
"""

import cv2
import numpy as np
import gc

def apply_black_tophat(image, params=None):
    """
    Apply black top-hat morphological operation to an image.
    Black top-hat is the difference between the closing of the image and the input image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 5)
            - iterations: Number of times operation is applied (default: 1)
            - strength: Strength of the effect (0.0-1.0, default: 1.0)
    
    Returns:
        Black top-hat filtered image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 5)
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
    
    # Apply black top-hat
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            result_channels = []
            
            for channel in channels:
                # Black top-hat is closing minus original
                black_tophat = cv2.morphologyEx(channel, cv2.MORPH_BLACKHAT, kernel, iterations=iterations)
                
                # Apply strength parameter
                if strength < 1.0:
                    black_tophat = cv2.multiply(black_tophat, strength)
                
                # Add the top-hat result to the original image for enhancement
                result_channel = cv2.add(channel, black_tophat)
                result_channels.append(result_channel)
            
            result = cv2.merge(result_channels)
        else:  # Grayscale image
            # Black top-hat is closing minus original
            black_tophat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, kernel, iterations=iterations)
            
            # Apply strength parameter
            if strength < 1.0:
                black_tophat = cv2.multiply(black_tophat, strength)
            
            # Add the top-hat result to the original image for enhancement
            result = cv2.add(image, black_tophat)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in black top-hat: {str(e)}")
        return image
