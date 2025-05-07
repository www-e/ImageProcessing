"""
Image optimization service for the Image Processing application
Integrates the optimization utilities from utils/image_optimizer.py and utils/image_utils.py
"""
import os
import sys
from utils.image_optimizer import (
    compress_image, optimize_for_web, clear_image_cache, 
    analyze_image, estimate_processing_time
)
from utils.image_utils import (
    load_image, save_image, convert_to_grayscale, convert_to_rgb,
    normalize_image, calculate_local_statistics, shannon_entropy,
    calculate_local_entropy, clip_and_normalize
)

# Re-export all the functions for use in the application
__all__ = [
    # From image_optimizer
    'compress_image', 'optimize_for_web', 'clear_image_cache',
    'analyze_image', 'estimate_processing_time',
    
    # From image_utils
    'load_image', 'save_image', 'convert_to_grayscale', 'convert_to_rgb',
    'normalize_image', 'calculate_local_statistics', 'shannon_entropy',
    'calculate_local_entropy', 'clip_and_normalize'
]
