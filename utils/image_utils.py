import cv2
import numpy as np
from scipy import stats
import math

def load_image(file_path):
    """
    Load an image from the given file path.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Loaded image in BGR format
    """
    image = cv2.imread(file_path)
    if image is None:
        raise ValueError(f"Could not load image from {file_path}")
    return image

def save_image(image, file_path):
    """
    Save an image to the given file path.
    
    Args:
        image: Image to save
        file_path: Path where to save the image
    
    Returns:
        True if successful, False otherwise
    """
    return cv2.imwrite(file_path, image)

def convert_to_grayscale(image):
    """
    Convert a BGR image to grayscale.
    
    Args:
        image: BGR image
        
    Returns:
        Grayscale image
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def convert_to_rgb(image):
    """
    Convert a BGR image to RGB.
    
    Args:
        image: BGR image
        
    Returns:
        RGB image
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def normalize_image(image):
    """
    Normalize image values to range [0, 255].
    
    Args:
        image: Input image
        
    Returns:
        Normalized image
    """
    min_val = np.min(image)
    max_val = np.max(image)
    
    if max_val == min_val:
        return np.zeros_like(image)
    
    normalized = 255 * (image - min_val) / (max_val - min_val)
    return normalized.astype(np.uint8)

def calculate_local_statistics(image, window_size):
    """
    Calculate local mean and standard deviation for each pixel.
    Optimized for performance with integral images.
    
    Args:
        image: Input image
        window_size: Size of the local window (must be odd)
        
    Returns:
        Tuple of (local_mean, local_std)
    """
    # Ensure window_size is odd
    if window_size % 2 == 0:
        window_size += 1
    
    # Convert to grayscale if needed
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
    else:
        gray = image.astype(np.float32)
    
    # Use faster methods for local statistics
    # 1. For mean, use a simple box filter which is very fast
    local_mean = cv2.boxFilter(gray, ddepth=-1, ksize=(window_size, window_size), 
                              normalize=True, borderType=cv2.BORDER_REFLECT)
    
    # 2. For variance, use a more efficient approach
    # Calculate squared image
    gray_squared = cv2.multiply(gray, gray)
    
    # Calculate local sum of squares
    local_sum_squares = cv2.boxFilter(gray_squared, ddepth=-1, ksize=(window_size, window_size), 
                                    normalize=True, borderType=cv2.BORDER_REFLECT)
    
    # Calculate variance: E[X²] - (E[X])²
    local_var = local_sum_squares - cv2.multiply(local_mean, local_mean)
    
    # Calculate standard deviation with a small epsilon to avoid sqrt of negative numbers
    epsilon = 1e-5
    local_std = cv2.sqrt(cv2.max(local_var, epsilon))
    
    return local_mean, local_std

def shannon_entropy(image):
    """
    Calculate Shannon entropy of an image.
    
    Args:
        image: Input image (grayscale)
        
    Returns:
        Shannon entropy value
    """
    # Calculate histogram
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = hist.ravel() / hist.sum()
    
    # Remove zeros (log(0) is undefined)
    hist = hist[hist > 0]
    
    # Calculate entropy
    entropy = -np.sum(hist * np.log2(hist))
    return entropy

def calculate_local_entropy(image, window_size):
    """
    Calculate local entropy for each pixel.
    Optimized version using histogram-based approach and integral images.
    
    Args:
        image: Input image
        window_size: Size of the local window (must be odd)
        
    Returns:
        Local entropy map
    """
    # Ensure window_size is odd
    if window_size % 2 == 0:
        window_size += 1
    
    # Convert to grayscale if needed
    if len(image.shape) > 2:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Use a faster approach for entropy calculation
    # Reduce precision to speed up calculation (use 16 bins instead of 256)
    # This significantly reduces computation while maintaining good results
    reduced_precision = (gray // 16).astype(np.uint8)
    
    # Initialize entropy map
    entropy_map = np.zeros_like(gray, dtype=np.float32)
    
    # Use a sliding window approach with optimized histogram calculation
    pad_size = window_size // 2
    padded = cv2.copyMakeBorder(reduced_precision, pad_size, pad_size, pad_size, pad_size, 
                               cv2.BORDER_REFLECT)
    
    # Use a more efficient implementation with vectorized operations
    # Process in chunks to improve cache locality
    chunk_size = 64  # Process in 64x64 chunks for better cache performance
    
    for y_start in range(0, gray.shape[0], chunk_size):
        y_end = min(y_start + chunk_size, gray.shape[0])
        
        for x_start in range(0, gray.shape[1], chunk_size):
            x_end = min(x_start + chunk_size, gray.shape[1])
            
            # Process current chunk
            for y in range(y_start, y_end):
                for x in range(x_start, x_end):
                    # Extract window
                    window = padded[y:y+window_size, x:x+window_size]
                    
                    # Calculate histogram (optimized for 16 bins)
                    hist = np.bincount(window.flatten(), minlength=16)
                    hist = hist / hist.sum()
                    
                    # Calculate entropy only for non-zero probabilities
                    non_zero = hist > 0
                    if np.any(non_zero):
                        entropy = -np.sum(hist[non_zero] * np.log2(hist[non_zero]))
                    else:
                        entropy = 0
                    
                    entropy_map[y, x] = entropy
    
    # Normalize entropy map to [0, 1] range
    if np.max(entropy_map) > 0:
        entropy_map = entropy_map / np.max(entropy_map)
    
    return entropy_map

def clip_and_normalize(image):
    """
    Clip values to [0, 255] range and convert to uint8.
    
    Args:
        image: Input image
        
    Returns:
        Clipped and normalized image
    """
    return np.clip(image, 0, 255).astype(np.uint8)
