"""
Morphological filters for image processing.
This module provides optimized implementations of common morphological operations.
"""

import cv2
import numpy as np
import gc

def apply_dilation(image, params=None):
    """
    Apply dilation morphological operation to an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 5)
            - iterations: Number of times dilation is applied (default: 1)
    
    Returns:
        Dilated image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 5)
    iterations = params.get('iterations', 1)
    
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Create structuring element
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply dilation
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            dilated_channels = []
            
            for channel in channels:
                dilated = cv2.dilate(channel, kernel, iterations=iterations)
                dilated_channels.append(dilated)
            
            result = cv2.merge(dilated_channels)
        else:  # Grayscale image
            result = cv2.dilate(image, kernel, iterations=iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in dilation: {str(e)}")
        return image

def apply_erosion(image, params=None):
    """
    Apply erosion morphological operation to an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 5)
            - iterations: Number of times erosion is applied (default: 1)
    
    Returns:
        Eroded image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 5)
    iterations = params.get('iterations', 1)
    
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Create structuring element
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply erosion
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            eroded_channels = []
            
            for channel in channels:
                eroded = cv2.erode(channel, kernel, iterations=iterations)
                eroded_channels.append(eroded)
            
            result = cv2.merge(eroded_channels)
        else:  # Grayscale image
            result = cv2.erode(image, kernel, iterations=iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in erosion: {str(e)}")
        return image

def apply_opening(image, params=None):
    """
    Apply opening morphological operation to an image.
    Opening is erosion followed by dilation.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 5)
            - iterations: Number of times operation is applied (default: 1)
    
    Returns:
        Opened image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 5)
    iterations = params.get('iterations', 1)
    
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Create structuring element
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply opening
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            opened_channels = []
            
            for channel in channels:
                opened = cv2.morphologyEx(channel, cv2.MORPH_OPEN, kernel, iterations=iterations)
                opened_channels.append(opened)
            
            result = cv2.merge(opened_channels)
        else:  # Grayscale image
            result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in opening: {str(e)}")
        return image

def apply_closing(image, params=None):
    """
    Apply closing morphological operation to an image.
    Closing is dilation followed by erosion.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 5)
            - iterations: Number of times operation is applied (default: 1)
    
    Returns:
        Closed image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 5)
    iterations = params.get('iterations', 1)
    
    # Ensure kernel size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Create structuring element
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply closing
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            closed_channels = []
            
            for channel in channels:
                closed = cv2.morphologyEx(channel, cv2.MORPH_CLOSE, kernel, iterations=iterations)
                closed_channels.append(closed)
            
            result = cv2.merge(closed_channels)
        else:  # Grayscale image
            result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in closing: {str(e)}")
        return image

def apply_tophat(image, params=None):
    """
    Apply white top-hat morphological operation to an image.
    Top-hat is the difference between input image and its opening.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - kernel_size: Size of the structuring element (default: 5)
            - iterations: Number of times operation is applied (default: 1)
            - strength: Strength of the effect (0.0-1.0, default: 1.0)
    
    Returns:
        Top-hat filtered image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    kernel_size = params.get('kernel_size', 9)  # Larger default for top-hat
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
    
    # Apply top-hat
    try:
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Process each channel separately for better control
            channels = cv2.split(image)
            tophat_channels = []
            
            for channel in channels:
                tophat = cv2.morphologyEx(channel, cv2.MORPH_TOPHAT, kernel, iterations=iterations)
                # Apply strength factor
                if strength < 1.0:
                    tophat = cv2.multiply(tophat, strength)
                # Add top-hat to original for enhancement
                enhanced = cv2.add(channel, tophat)
                tophat_channels.append(enhanced)
            
            result = cv2.merge(tophat_channels)
        else:  # Grayscale image
            tophat = cv2.morphologyEx(image, cv2.MORPH_TOPHAT, kernel, iterations=iterations)
            # Apply strength factor
            if strength < 1.0:
                tophat = cv2.multiply(tophat, strength)
            # Add top-hat to original for enhancement
            result = cv2.add(image, tophat)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in top-hat: {str(e)}")
        return image
