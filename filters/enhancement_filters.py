"""
Enhancement filters for image processing.
This module provides optimized implementations of enhancement operations.
"""

import cv2
import numpy as np
import gc
from utils.image_utils import normalize_image, clip_and_normalize

def apply_brightness_contrast(image, params=None):
    """
    Apply brightness and contrast adjustment to an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - brightness: Brightness adjustment (-100 to 100, default: 0)
            - contrast: Contrast adjustment (-100 to 100, default: 0)
    
    Returns:
        Adjusted image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    brightness = params.get('brightness', 0)
    contrast = params.get('contrast', 0)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply brightness and contrast adjustment
    try:
        # Convert brightness and contrast to alpha-beta values
        if contrast > 0:
            alpha = 1 + contrast / 100.0
        else:
            alpha = 1 + contrast / 127.0
        
        beta = brightness
        
        # Process color and grayscale images appropriately
        result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in brightness/contrast adjustment: {str(e)}")
        return image

def apply_exposure(image, params=None):
    """
    Apply exposure adjustment to an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - exposure: Exposure adjustment (-100 to 100, default: 0)
    
    Returns:
        Adjusted image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    exposure = params.get('exposure', 0)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply exposure adjustment
    try:
        # Convert exposure to gamma value
        if exposure > 0:
            gamma = 1 - exposure / 100.0  # Increase exposure (lower gamma)
        else:
            gamma = 1 + abs(exposure) / 50.0  # Decrease exposure (higher gamma)
        
        # Create lookup table for gamma correction
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        
        # Process color and grayscale images appropriately
        if len(image.shape) > 2:  # Color image
            # Apply gamma correction using lookup table
            result = cv2.LUT(image, table)
        else:  # Grayscale image
            result = cv2.LUT(image, table)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in exposure adjustment: {str(e)}")
        return image

def apply_vibrance(image, params=None):
    """
    Apply vibrance adjustment to an image.
    Vibrance increases saturation of less-saturated colors more than already-saturated colors.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - vibrance: Vibrance adjustment (0 to 100, default: 50)
    
    Returns:
        Adjusted image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    vibrance = params.get('vibrance', 50) / 100.0
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply vibrance adjustment
    try:
        # Only works on color images
        if len(image.shape) > 2:  # Color image
            # Convert to HSV color space
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
            
            # Split channels
            h, s, v = cv2.split(hsv)
            
            # Calculate average saturation
            avg_sat = np.mean(s)
            
            # Apply vibrance: increase saturation more for less saturated pixels
            mask = (255 - s) / 255.0  # Mask is stronger for less saturated pixels
            s = s + mask * s * vibrance
            s = np.clip(s, 0, 255)
            
            # Merge channels
            hsv = cv2.merge([h, s, v])
            
            # Convert back to BGR
            result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Clean up to free memory
            gc.collect()
            
            return result
        else:  # Grayscale image - vibrance has no effect
            return image
    except Exception as e:
        print(f"Error in vibrance adjustment: {str(e)}")
        return image

def apply_clarity(image, params=None):
    """
    Apply clarity adjustment to an image.
    Clarity enhances midtone contrast.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - clarity: Clarity adjustment (0 to 100, default: 50)
    
    Returns:
        Adjusted image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    clarity = params.get('clarity', 50) / 100.0
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply clarity adjustment
    try:
        # Create a blurred version of the image
        blur_amount = int(10 * clarity) * 2 + 1  # Ensure odd number
        blurred = cv2.GaussianBlur(image, (blur_amount, blur_amount), 0)
        
        # Apply unsharp mask technique for midtone contrast
        result = cv2.addWeighted(image, 1 + clarity, blurred, -clarity, 0)
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in clarity adjustment: {str(e)}")
        return image

def apply_shadows_highlights(image, params=None):
    """
    Apply shadows and highlights adjustment to an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - shadows: Shadow adjustment (0 to 100, default: 50)
            - highlights: Highlight adjustment (0 to 100, default: 50)
    
    Returns:
        Adjusted image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    shadows = params.get('shadows', 50) / 100.0
    highlights = params.get('highlights', 50) / 100.0
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply shadows and highlights adjustment
    try:
        # Convert to LAB color space
        if len(image.shape) > 2:  # Color image
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
        else:  # Grayscale image
            l = image.copy()
        
        # Create shadow and highlight masks
        shadow_mask = (1.0 - l / 255.0) ** 2  # Stronger for darker pixels
        highlight_mask = (l / 255.0) ** 2  # Stronger for brighter pixels
        
        # Apply adjustments
        l = l.astype(np.float32)
        l += shadow_mask * shadows * 100  # Lighten shadows
        l -= highlight_mask * highlights * 100  # Darken highlights
        l = np.clip(l, 0, 255).astype(np.uint8)
        
        # Merge channels if color image
        if len(image.shape) > 2:
            lab = cv2.merge([l, a, b])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            result = l
        
        # Clean up to free memory
        gc.collect()
        
        return result
    except Exception as e:
        print(f"Error in shadows/highlights adjustment: {str(e)}")
        return image

def apply_hdr_effect(image, params=None):
    """
    Apply HDR-like effect to an image.
    
    Args:
        image: Input image
        params: Dictionary of parameters
            - strength: Effect strength (0 to 100, default: 50)
            - radius: Local contrast radius (1 to 100, default: 20)
    
    Returns:
        HDR-effect image
    """
    if params is None:
        params = {}
    
    # Get parameters with defaults
    strength = params.get('strength', 50) / 100.0
    radius = params.get('radius', 20)
    
    # Convert image to appropriate type
    if image.dtype != np.uint8:
        image = np.clip(image, 0, 255).astype(np.uint8)
    
    # Apply HDR effect
    try:
        # Convert to 32-bit float
        img_float = image.astype(np.float32) / 255.0
        
        # Create tonemapped version
        if len(image.shape) > 2:  # Color image
            # Convert to LAB for better processing
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply local tone mapping to L channel
            tonemap = cv2.createTonemapDrago(gamma=1.0, saturation=1.0, bias=0.85)
            l_mapped = tonemap.process(l.astype(np.float32) / 255.0) * 255.0
            
            # Blend original and tonemapped version
            l_result = cv2.addWeighted(l.astype(np.float32), 1 - strength, l_mapped.astype(np.float32), strength, 0)
            
            # Merge channels
            result_lab = cv2.merge([l_result.astype(np.uint8), a, b])
            result = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
            
            # Enhance local contrast
            kernel_size = radius * 2 + 1
            blurred = cv2.GaussianBlur(result, (kernel_size, kernel_size), 0)
            result = cv2.addWeighted(result, 1 + strength * 0.5, blurred, -strength * 0.5, 0)
        else:  # Grayscale image
            tonemap = cv2.createTonemapDrago(gamma=1.0, saturation=1.0, bias=0.85)
            mapped = tonemap.process(img_float) * 255.0
            result = cv2.addWeighted(image.astype(np.float32), 1 - strength, mapped.astype(np.float32), strength, 0)
            
            # Enhance local contrast
            kernel_size = radius * 2 + 1
            blurred = cv2.GaussianBlur(result, (kernel_size, kernel_size), 0)
            result = cv2.addWeighted(result, 1 + strength * 0.5, blurred, -strength * 0.5, 0)
        
        # Clean up to free memory
        gc.collect()
        
        return np.clip(result, 0, 255).astype(np.uint8)
    except Exception as e:
        print(f"Error in HDR effect: {str(e)}")
        return image
