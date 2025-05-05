import cv2
import numpy as np
from utils.image_utils import normalize_image, clip_and_normalize, calculate_local_statistics

def clahe_filter(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).
    
    Args:
        image: Input grayscale image
        clip_limit: Threshold for contrast limiting
        tile_grid_size: Size of grid for histogram equalization
        
    Returns:
        CLAHE-enhanced image
    """
    # Create CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    
    # Apply CLAHE
    if len(image.shape) == 2:  # Grayscale
        return clahe.apply(image)
    else:  # Color image
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel
        lab_planes = list(cv2.split(lab))
        lab_planes[0] = clahe.apply(lab_planes[0])
        
        # Merge channels
        lab = cv2.merge(lab_planes)
        
        # Convert back to BGR
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def local_contrast_enhancement(image, window_size=15, clip_limit=3.0, alpha=2.0):
    """
    Enhance contrast based on local statistics.
    
    Args:
        image: Input image
        window_size: Size of the local window
        clip_limit: Limit for contrast enhancement
        alpha: Enhancement strength parameter
        
    Returns:
        Enhanced image
    """
    # Convert to float for processing
    float_img = image.astype(np.float32)
    
    # Calculate local mean and standard deviation
    local_mean, local_std = calculate_local_statistics(float_img, window_size)
    
    # Global mean and standard deviation
    global_mean = np.mean(float_img)
    global_std = np.std(float_img)
    
    # Clip local standard deviation to limit excessive enhancement
    local_std = np.minimum(local_std, clip_limit * global_std)
    
    # Enhanced image: global_mean + alpha * (local_std / global_std) * (image - local_mean)
    enhanced = global_mean + alpha * (local_std / (global_std + 1e-5)) * (float_img - local_mean)
    
    # Clip values to valid range and convert back to original data type
    return clip_and_normalize(enhanced)

def adaptive_gamma_correction(image, window_size=15, gamma_min=0.5, gamma_max=2.0):
    """
    Apply adaptive gamma correction based on local brightness.
    
    Args:
        image: Input image
        window_size: Size of the local window
        gamma_min: Minimum gamma value
        gamma_max: Maximum gamma value
        
    Returns:
        Gamma-corrected image
    """
    # Convert to float for processing
    float_img = image.astype(np.float32) / 255.0
    
    # Calculate local mean (brightness)
    local_mean, _ = calculate_local_statistics(float_img, window_size)
    
    # Map local mean to gamma values (inverse relationship)
    # Bright regions (high mean) get gamma < 1 (darken)
    # Dark regions (low mean) get gamma > 1 (brighten)
    gamma_map = gamma_max - (gamma_max - gamma_min) * local_mean
    
    # Apply pixel-wise gamma correction
    corrected = np.power(float_img, gamma_map)
    
    # Scale back to [0, 255] and convert to uint8
    return (corrected * 255).astype(np.uint8)

def detail_enhancement(image, sigma_s=10, sigma_r=0.15):
    """
    Enhance details in the image using domain transform filter.
    
    Args:
        image: Input image
        sigma_s: Spatial standard deviation
        sigma_r: Range standard deviation
        
    Returns:
        Detail-enhanced image
    """
    # Convert to 8-bit if needed
    if image.dtype != np.uint8:
        image = normalize_image(image)
    
    # Apply detail enhancement
    return cv2.detailEnhance(image, sigma_s=sigma_s, sigma_r=sigma_r)

def edge_preserving_filter(image, flags=1, sigma_s=60, sigma_r=0.4):
    """
    Apply edge-preserving filter.
    
    Args:
        image: Input image
        flags: Type of filter (1: RECURS_FILTER, 2: NORMCONV_FILTER)
        sigma_s: Spatial standard deviation
        sigma_r: Range standard deviation
        
    Returns:
        Filtered image
    """
    # Convert to 8-bit if needed
    if image.dtype != np.uint8:
        image = normalize_image(image)
    
    return cv2.edgePreservingFilter(image, flags=flags, sigma_s=sigma_s, sigma_r=sigma_r)

def local_tone_mapping(image, window_size=15, alpha=1.5, beta=0.5):
    """
    Apply local tone mapping based on local statistics.
    
    Args:
        image: Input image
        window_size: Size of the local window
        alpha: Detail enhancement factor
        beta: Brightness adjustment factor
        
    Returns:
        Tone-mapped image
    """
    # Convert to float for processing
    float_img = image.astype(np.float32)
    
    # Calculate local mean and standard deviation
    local_mean, local_std = calculate_local_statistics(float_img, window_size)
    
    # Decompose image into base and detail layers
    base_layer = local_mean
    detail_layer = float_img - base_layer
    
    # Enhance detail layer
    enhanced_detail = alpha * detail_layer
    
    # Adjust base layer (compress dynamic range)
    adjusted_base = beta * base_layer
    
    # Recombine layers
    result = adjusted_base + enhanced_detail
    
    # Clip values to valid range and convert back to original data type
    return clip_and_normalize(result)
