import cv2
import numpy as np
from utils.image_utils import normalize_image, clip_and_normalize

def gaussian_blur(image, kernel_size=5, sigma=0):
    """
    Apply Gaussian blur to an image.
    
    Args:
        image: Input image
        kernel_size: Size of the Gaussian kernel (must be odd)
        sigma: Standard deviation of the Gaussian kernel (0 means auto-calculated)
        
    Returns:
        Blurred image
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel size is odd
    
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

def average_blur(image, kernel_size=5):
    """
    Apply average (mean) blur to an image.
    
    Args:
        image: Input image
        kernel_size: Size of the averaging kernel (must be odd)
        
    Returns:
        Blurred image
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel size is odd
    
    return cv2.blur(image, (kernel_size, kernel_size))

def median_blur(image, kernel_size=5):
    """
    Apply median blur to an image.
    
    Args:
        image: Input image
        kernel_size: Size of the median filter kernel (must be odd)
        
    Returns:
        Blurred image
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel size is odd
    
    return cv2.medianBlur(image, kernel_size)

def laplacian_filter(image, kernel_size=3, scale=1.0):
    """
    Apply Laplacian filter to an image for edge detection and sharpening.
    
    Args:
        image: Input image
        kernel_size: Size of the Laplacian kernel (must be odd)
        scale: Scaling factor for the Laplacian result
        
    Returns:
        Filtered image
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel size is odd
    
    # Convert to float for processing
    float_img = image.astype(np.float32)
    
    # Apply Laplacian filter
    laplacian = cv2.Laplacian(float_img, cv2.CV_32F, ksize=kernel_size)
    
    # Scale the result
    laplacian = laplacian * scale
    
    return laplacian

def unsharp_mask(image, kernel_size=5, sigma=1.0, amount=1.0, threshold=0):
    """
    Apply unsharp masking to sharpen an image.
    
    Args:
        image: Input image
        kernel_size: Size of the Gaussian kernel for blurring
        sigma: Standard deviation of the Gaussian kernel
        amount: Strength of the sharpening effect (1.0 = 100%)
        threshold: Minimum brightness difference to apply sharpening
        
    Returns:
        Sharpened image
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel size is odd
    
    # Convert to float for processing
    float_img = image.astype(np.float32)
    
    # Create the blurred version
    blurred = cv2.GaussianBlur(float_img, (kernel_size, kernel_size), sigma)
    
    # Calculate the high-frequency components (detail)
    detail = float_img - blurred
    
    # Apply threshold to the detail
    if threshold > 0:
        detail = np.where(np.abs(detail) < threshold, 0, detail)
    
    # Add scaled detail to the original image
    sharpened = float_img + amount * detail
    
    # Clip values to valid range and convert back to original data type
    return clip_and_normalize(sharpened)

def high_boost_filter(image, kernel_size=5, boost_factor=2.0):
    """
    Apply high-boost filtering to enhance high-frequency components.
    
    Args:
        image: Input image
        kernel_size: Size of the smoothing kernel
        boost_factor: Factor to boost high frequencies (> 1.0)
        
    Returns:
        Enhanced image
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure kernel size is odd
    
    # Convert to float for processing
    float_img = image.astype(np.float32)
    
    # Create the blurred version (low-pass filtered)
    blurred = cv2.GaussianBlur(float_img, (kernel_size, kernel_size), 0)
    
    # Calculate the high-frequency components (mask)
    mask = float_img - blurred
    
    # Apply high-boost filter: original + boost_factor * mask
    boosted = float_img + boost_factor * mask
    
    # Clip values to valid range and convert back to original data type
    return clip_and_normalize(boosted)

def bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """
    Apply bilateral filter for edge-preserving smoothing.
    
    Args:
        image: Input image
        d: Diameter of each pixel neighborhood
        sigma_color: Filter sigma in the color space
        sigma_space: Filter sigma in the coordinate space
        
    Returns:
        Filtered image
    """
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

def guided_filter(image, guide=None, radius=8, eps=100):
    """
    Apply guided filter for edge-preserving smoothing.
    
    Args:
        image: Input image
        guide: Guidance image (if None, use input image as guide)
        radius: Radius of the filter
        eps: Regularization parameter
        
    Returns:
        Filtered image
    """
    if guide is None:
        guide = image
    
    # OpenCV's guided filter implementation
    return cv2.ximgproc.guidedFilter(guide, image, radius, eps)
