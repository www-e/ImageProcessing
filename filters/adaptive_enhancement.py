import cv2
import numpy as np
from utils.image_utils import (
    calculate_local_statistics, 
    calculate_local_entropy,
    clip_and_normalize
)
from filters.basic_filters import (
    gaussian_blur,
    bilateral_filter,
    unsharp_mask,
    high_boost_filter
)
from filters.advanced_filters import (
    clahe_filter,
    local_contrast_enhancement,
    adaptive_gamma_correction
)

class AdaptiveContrastEnhancement:
    """
    Comprehensive Adaptive Contrast Enhancement based on local statistics.
    This class implements a full pipeline of adaptive enhancement techniques
    that dynamically adjust based on local image characteristics.
    """
    
    def __init__(self, window_size=15, clip_limit=3.0, disable_entropy=False, use_simplified_processing=False, max_processing_dimension=1200):
        """Initialize the enhancement pipeline with performance parameters.
        
        Args:
            window_size: Size of the local window for adaptive processing
            clip_limit: Limits the contrast enhancement to prevent noise amplification
            disable_entropy: When true, skips entropy calculation for faster processing
            use_simplified_processing: When true, uses a simplified processing path for better performance
            max_processing_dimension: Maximum dimension for processing (images will be resized if larger)
        """
        self.window_size = window_size
        self.clip_limit = clip_limit
        self.disable_entropy = disable_entropy
        self.progress_callback = None
        
        # Performance optimization flags
        self.use_simplified_processing = use_simplified_processing
        self.max_processing_dimension = max_processing_dimension
    
    def set_progress_callback(self, callback):
        """
        Set a callback function to report progress during enhancement.
        
        Args:
            callback: Function that takes a progress value (0-1) as argument
        """
        self.progress_callback = callback
    
    def update_progress(self, progress):
        """
        Update progress and call the progress callback if set.
        
        Args:
            progress: Progress value (0-1)
        """
        if self.progress_callback:
            self.progress_callback(progress)
    
    def enhance(self, image, params=None):
        """
        Apply the full adaptive contrast enhancement pipeline.
        Optimized for performance with parallel processing and reduced computation.
        
        Args:
            image: Input image
            params: Dictionary of parameters for the enhancement
                   If None, default parameters will be used
        
        Returns:
            Enhanced image
        """
        # Initialize parameters
        if params is None:
            params = {}
        
        # Use class parameters if not provided in params
        window_size = params.get('window_size', self.window_size)
        clip_limit = params.get('clip_limit', self.clip_limit)
        disable_entropy = params.get('disable_entropy', self.disable_entropy)
        use_simplified = params.get('simplified_processing', self.use_simplified_processing)
        max_dimension = params.get('max_processing_dimension', self.max_processing_dimension)
        
        # Report initial progress
        self.update_progress(0.05)
        
        # Performance optimization: Resize large images for faster processing
        original_size = None
        h, w = image.shape[:2]
        
        # Only resize if image is larger than the max dimension
        if max(h, w) > max_dimension:
            print(f"Resizing image from {w}x{h} to fit within {max_dimension}px for faster processing")
            scale = max_dimension / max(h, w)
            new_size = (int(w * scale), int(h * scale))
            original_size = (w, h)  # Store original size for later upscaling
            image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
            print(f"Resized to {new_size[0]}x{new_size[1]}")
        
        self.update_progress(0.1)
        
        # Make a copy of the input image and convert to float32 for processing
        result = image.copy().astype(np.float32)
        
        # Check if we should use simplified processing for extreme performance
        # Use the class parameter if not provided in params
        
        if use_simplified:
            print("Using simplified processing mode for extreme performance")
            # For extreme performance, use a very simple enhancement approach
            # This bypasses most of the complex calculations
            
            # Convert to LAB color space for better perceptual enhancement
            self.update_progress(0.15)
            
            if len(result.shape) > 2:  # Color image
                # Convert BGR to LAB
                lab = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2LAB)
                
                # Split channels
                l, a, b = cv2.split(lab)
                
                self.update_progress(0.25)
                
                # Apply CLAHE to L channel only (much faster than full adaptive enhancement)
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
                l = clahe.apply(l)
                
                self.update_progress(0.40)
                
                # Merge channels back
                enhanced_lab = cv2.merge((l, a, b))
                
                # Convert back to BGR
                result = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR).astype(np.float32)
                
                self.update_progress(0.60)
                
                # Apply a simple sharpening if requested
                if params.get('sharpen', True):
                    kernel = np.array([[-1, -1, -1],
                                      [-1, 9, -1],
                                      [-1, -1, -1]])
                    result = cv2.filter2D(result, -1, kernel)
                
                # Upscale back to original size if we resized earlier
                if original_size:
                    result = cv2.resize(result, original_size, interpolation=cv2.INTER_LINEAR)
                
                self.update_progress(0.90)
                
                # Final normalization
                result = clip_and_normalize(result)
                
                self.update_progress(1.0)
                return result
            else:  # Grayscale image
                self.update_progress(0.20)
                
                # Apply CLAHE directly
                clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
                result = clahe.apply(result.astype(np.uint8)).astype(np.float32)
                
                self.update_progress(0.50)
                
                # Apply a simple sharpening if requested
                if params.get('sharpen', True):
                    kernel = np.array([[-1, -1, -1],
                                      [-1, 9, -1],
                                      [-1, -1, -1]])
                    result = cv2.filter2D(result, -1, kernel)
                
                self.update_progress(0.75)
                
                # Upscale back to original size if we resized earlier
                if original_size:
                    result = cv2.resize(result, original_size, interpolation=cv2.INTER_LINEAR)
                
                self.update_progress(0.90)
                
                # Final normalization
                result = clip_and_normalize(result)
                
                self.update_progress(1.0)
                return result
        
        # Standard processing path (if not using simplified mode)
        self.update_progress(0.15)
        print("Using standard high-quality processing path")
        
        # We already have window_size from class parameters
        # For very large images, increase window size for better performance
        if original_size and max(original_size) > 2000:
            window_size = max(window_size, 21)  # Larger window = fewer calculations
            print(f"Using larger window size {window_size} for better performance")
        
        # Handle color images properly to avoid broadcasting errors
        if len(result.shape) > 2:  # Color image
            # Process each channel separately to avoid broadcasting issues
            self.update_progress(0.20)
            print(f"Processing color image with window size {window_size}")
            
            channels = cv2.split(result)
            local_mean_channels = []
            local_std_channels = []
            
            # Process each channel with progress updates
            for i, channel in enumerate(channels):
                self.update_progress(0.25 + (i * 0.05))  # Progress from 0.25 to 0.35
                mean, std = calculate_local_statistics(channel, window_size)
                local_mean_channels.append(mean)
                local_std_channels.append(std)
                
            # Combine channels
            self.update_progress(0.40)
            local_mean = cv2.merge(local_mean_channels)
            local_std = cv2.merge(local_std_channels)
        else:  # Grayscale image
            self.update_progress(0.20)
            print(f"Processing grayscale image with window size {window_size}")
            local_mean, local_std = calculate_local_statistics(result, window_size)
            self.update_progress(0.40)
        
        # Calculate local entropy if needed - with additional performance optimizations
        self.update_progress(0.45)
        
        # Use the class parameter for disable_entropy if not provided in params
        use_entropy = not disable_entropy and params.get('use_entropy', True)
        
        # Skip entropy calculation for very large images or if explicitly disabled
        if not use_entropy or (original_size and max(original_size) > 2500):
            # Create a dummy entropy map if entropy is not used
            local_entropy = np.ones_like(local_mean) * 0.5
            print("Entropy calculation skipped for performance reasons")
            self.update_progress(0.55)  # Skip ahead in progress
        else:
            # For large but not huge images, use a larger window size for entropy
            entropy_window_size = window_size
            if original_size and max(original_size) > 1800:
                entropy_window_size = min(31, window_size * 2)  # Larger window for better performance
                print(f"Using larger entropy window size {entropy_window_size} for better performance")
            
            self.update_progress(0.50)
            
            # Handle entropy calculation for color images properly
            if len(result.shape) > 2:  # Color image
                # Convert to grayscale for entropy calculation (faster and sufficient)
                print("Calculating entropy for color image (using grayscale conversion)")
                gray = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2GRAY)
                entropy_map = calculate_local_entropy(gray, entropy_window_size)
                
                # Expand to match channels for broadcasting
                local_entropy = np.expand_dims(entropy_map, axis=2)
                local_entropy = np.repeat(local_entropy, 3, axis=2)  # Repeat for each channel
            else:  # Grayscale image
                print(f"Calculating entropy for grayscale image with window size {entropy_window_size}")
                local_entropy = calculate_local_entropy(result, entropy_window_size)
            
            self.update_progress(0.60)
        
        # Apply noise reduction if enabled
        if params.get('denoise', True):
            self.update_progress(0.65)
            print("Applying adaptive noise reduction")
            result = self._apply_noise_reduction(result, local_std, params)
        
        # Apply adaptive enhancement based on local statistics
        self.update_progress(0.70)
        print("Applying adaptive contrast enhancement")
        result = self._apply_adaptive_enhancement(result, local_mean, local_std, local_entropy, params)
        
        # Apply detail enhancement if enabled
        if params.get('enhance_details', True):
            self.update_progress(0.80)
            print("Enhancing image details")
            result = self._apply_detail_enhancement(result, local_std, params)
        
        # Apply final adjustments
        self.update_progress(0.85)
        print("Applying final adjustments")
        result = self._apply_final_adjustments(result, params)
        
        # Upscale back to original size if we resized earlier
        if original_size:
            self.update_progress(0.90)
            print(f"Upscaling image back to original size {original_size[0]}x{original_size[1]}")
            result = cv2.resize(result, original_size, interpolation=cv2.INTER_LINEAR)
        
        self.update_progress(0.95)
        print("Finalizing image")
        result = clip_and_normalize(result)
        
        self.update_progress(1.0)
        print("Enhancement complete")
        return result
    
    def _apply_noise_reduction(self, image, local_std, params):
        """
        Apply adaptive noise reduction based on local standard deviation.
        Areas with low standard deviation (flat regions) get more smoothing.
        
        Args:
            image: Input image
            local_std: Local standard deviation map
            params: Enhancement parameters
            
        Returns:
            Noise-reduced image
        """
        # Normalize local standard deviation to [0, 1]
        std_max = np.max(local_std)
        if std_max > 0:
            std_norm = local_std / std_max
        else:
            std_norm = local_std
        
        # Calculate adaptive kernel size based on local standard deviation
        # Smaller std (flatter regions) get larger kernel for more smoothing
        min_kernel = params.get('min_kernel_size', 3)
        max_kernel = params.get('max_kernel_size', 7)
        
        # Create a kernel size map
        kernel_map = min_kernel + (max_kernel - min_kernel) * (1 - std_norm)
        kernel_map = np.round(kernel_map).astype(np.int32)
        
        # Ensure kernel sizes are odd
        kernel_map = kernel_map + (kernel_map % 2 == 0).astype(np.int32)
        
        # Apply bilateral filter with fixed parameters for edge preservation
        bilateral_strength = params.get('bilateral_strength', 1.0)
        d = params.get('bilateral_diameter', 9)
        sigma_color = params.get('bilateral_sigma_color', 75) * bilateral_strength
        sigma_space = params.get('bilateral_sigma_space', 75) * bilateral_strength
        
        denoised = bilateral_filter(image.astype(np.uint8), d, sigma_color, sigma_space)
        
        # Blend original and denoised based on local standard deviation
        # High std (edges) keeps more of original, low std (flat) gets more denoising
        blend_factor = params.get('denoise_blend_factor', 0.7)
        blend_map = std_norm * blend_factor
        
        # Blend using the map
        result = image * blend_map + denoised.astype(np.float32) * (1 - blend_map)
        
        return result
    
    def _apply_adaptive_enhancement(self, image, local_mean, local_std, local_entropy, params):
        """
        Apply adaptive enhancement based on local statistics.
        Highly optimized for performance with vectorized operations.
        
        Args:
            image: Input image
            local_mean: Local mean map
            local_std: Local standard deviation map
            local_entropy: Local entropy map
            params: Enhancement parameters
            
        Returns:
            Enhanced image
        """
        # Get parameters with defaults optimized for speed
        alpha = params.get('alpha', 1.0)  # Contrast enhancement factor
        beta = params.get('beta', 0.5)   # Brightness adjustment factor
        gamma = params.get('gamma', 0.75) # Local adaptation factor
        
        # Handle color and grayscale images properly to avoid broadcasting errors
        if len(image.shape) > 2:  # Color image
            # Ensure all arrays have the same shape for broadcasting
            if len(local_mean.shape) != 3 or local_mean.shape[2] != 3:
                print("Warning: Reshaping local_mean to match image dimensions")
                local_mean = np.expand_dims(cv2.cvtColor(local_mean.astype(np.uint8), cv2.COLOR_GRAY2BGR), axis=2)
            
            if len(local_std.shape) != 3 or local_std.shape[2] != 3:
                print("Warning: Reshaping local_std to match image dimensions")
                local_std = np.expand_dims(cv2.cvtColor(local_std.astype(np.uint8), cv2.COLOR_GRAY2BGR), axis=2)
            
            if len(local_entropy.shape) != 3 or local_entropy.shape[2] != 3:
                print("Warning: Reshaping local_entropy to match image dimensions")
                # Convert entropy to 3-channel if needed
                if len(local_entropy.shape) == 2:
                    local_entropy = np.repeat(np.expand_dims(local_entropy, axis=2), 3, axis=2)
            
            # Fast normalization of local statistics to [0, 1] range
            norm_mean = local_mean / 255.0
            max_std = np.max(local_std)
            norm_std = local_std / max_std if max_std > 0 else local_std
            
            # Calculate enhancement factors based on local statistics and entropy
            enhancement_factor = alpha * (1.0 + gamma * local_entropy)
            
            # Process all channels simultaneously with broadcasting for maximum performance
            img_norm = image.astype(np.float32) / 255.0
            
            # Apply enhancement with fully vectorized operations
            enhanced = norm_mean + enhancement_factor * (img_norm - norm_mean)
            enhanced = enhanced + beta * (1.0 - enhanced) * norm_std
            
            # Scale back to [0, 255] range
            enhanced = enhanced * 255.0
        else:  # Grayscale image
            # Fast normalization of local statistics to [0, 1] range
            norm_mean = local_mean / 255.0
            max_std = np.max(local_std)
            norm_std = local_std / max_std if max_std > 0 else local_std
            
            # Calculate enhancement factors based on local statistics and entropy
            enhancement_factor = alpha * (1.0 + gamma * local_entropy)
            
            # Normalize to [0, 1]
            img_norm = image.astype(np.float32) / 255.0
            
            # Apply enhancement with vectorized operations
            enhanced = norm_mean + enhancement_factor * (img_norm - norm_mean)
            enhanced = enhanced + beta * (1.0 - enhanced) * norm_std
            
            # Scale back to [0, 255] range
            enhanced = enhanced * 255.0
        
        return enhanced
    
    def _apply_detail_enhancement(self, image, local_std, params):
        """
        Apply adaptive detail enhancement based on local standard deviation.
        
        Args:
            image: Input image
            local_std: Local standard deviation map
            params: Enhancement parameters
            
        Returns:
            Detail-enhanced image
        """
        # Normalize local standard deviation to [0, 1]
        std_max = np.max(local_std)
        if std_max > 0:
            std_norm = local_std / std_max
        else:
            std_norm = local_std
        
        # Apply unsharp masking with adaptive amount
        kernel_size = params.get('unsharp_kernel_size', 5)
        sigma = params.get('unsharp_sigma', 1.0)
        base_amount = params.get('unsharp_amount', 1.0)
        threshold = params.get('unsharp_threshold', 5)
        
        # Calculate adaptive amount based on local standard deviation
        # Low std (flat regions) get less sharpening to avoid noise amplification
        adaptive_amount = base_amount * std_norm
        
        # Apply unsharp mask
        sharpened = unsharp_mask(image.astype(np.uint8), kernel_size, sigma, base_amount, threshold)
        
        # Blend original and sharpened based on adaptive amount
        result = image * (1 - std_norm) + sharpened.astype(np.float32) * std_norm
        
        return result
    
    def _apply_final_adjustments(self, image, params):
        """
        Apply final adjustments to the enhanced image.
        
        Args:
            image: Enhanced image
            params: Enhancement parameters
            
        Returns:
            Final adjusted image
        """
        # Apply CLAHE if enabled
        if params.get('apply_clahe', True):
            clip_limit = params.get('clahe_clip_limit', 2.0)
            tile_grid_size = params.get('clahe_tile_grid_size', (8, 8))
            
            # Convert to uint8 for CLAHE
            uint8_img = clip_and_normalize(image)
            
            # Apply CLAHE
            clahe_result = clahe_filter(uint8_img, clip_limit, tile_grid_size)
            
            # Blend with original enhanced image
            clahe_blend = params.get('clahe_blend', 0.5)
            image = image * (1 - clahe_blend) + clahe_result.astype(np.float32) * clahe_blend
        
        # Apply high-boost filtering if enabled
        if params.get('apply_high_boost', True):
            kernel_size = params.get('high_boost_kernel_size', 5)
            boost_factor = params.get('high_boost_factor', 1.5)
            
            # Convert to uint8 for high-boost
            uint8_img = clip_and_normalize(image)
            
            # Apply high-boost filter
            boosted = high_boost_filter(uint8_img, kernel_size, boost_factor)
            
            # Blend with enhanced image
            boost_blend = params.get('high_boost_blend', 0.3)
            image = image * (1 - boost_blend) + boosted.astype(np.float32) * boost_blend
        
        return image
    
    def get_default_params(self):
        """Get default parameters for enhancement"""
        return {
            'window_size': self.window_size,
            'clip_limit': self.clip_limit,
            'use_entropy': not self.disable_entropy,
            'disable_entropy': self.disable_entropy,
            'simplified_processing': self.use_simplified_processing,
            'max_processing_dimension': self.max_processing_dimension,
            'sharpen': True,
            'denoise': True,
            'enhance_details': True,
            
            # Adaptive enhancement parameters
            'gamma_min': 0.7,
            'gamma_max': 1.5,
            'contrast_strength': 2.0,
            'entropy_factor': 0.3,
            
            # Detail enhancement parameters
            'unsharp_kernel_size': 5,
            'unsharp_sigma': 1.0,
            'unsharp_amount': 1.0,
            'unsharp_threshold': 5,
            
            # Final adjustment parameters
            'apply_clahe': True,
            'clahe_clip_limit': 2.0,
            'clahe_tile_grid_size': (8, 8),
            'clahe_blend': 0.5,
            'apply_high_boost': True,
            'high_boost_kernel_size': 5,
            'high_boost_factor': 1.5,
            'high_boost_blend': 0.3
        }
