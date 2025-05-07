"""
Task processing service for the Image Processing application
"""
import os
import gc
import time
from datetime import datetime

from config.settings import RESULT_FOLDER, ENABLE_PERFORMANCE_OPTIMIZATIONS
from services.task_manager import task_manager
from services.history_manager import HistoryManager

# Import optimized image processing functions
from services.image_processor import (
    load_image, save_image, clear_image_cache, 
    compress_image, analyze_image, estimate_processing_time
)
from services.image_optimization import (
    normalize_image, calculate_local_statistics, 
    calculate_local_entropy, clip_and_normalize
)

# Import image processing functions
from filters.enhancement import (
    apply_brightness_contrast, apply_exposure, apply_vibrance,
    apply_clarity, apply_shadows_highlights
)
from filters.morphological import (
    apply_dilation, apply_erosion, apply_opening, apply_closing,
    apply_tophat, apply_black_tophat, apply_morphological_gradient,
    apply_hit_miss_transform, apply_thinning, apply_thickening,
    apply_skeletonization
)

# Create a history manager instance
history_manager = HistoryManager()

def process_image_task(task_id, image_path, filename, params, use_compressed, data):
    """Process an image enhancement task in the background"""
    # Get the task from the processing_tasks dictionary
    task = task_manager.get_task(task_id)
    if not task:
        return
    
    try:
        # Update progress
        task_manager.update_task_progress(task_id, 10)
        
        # Load the image
        try:
            image = load_image(image_path)
            task_manager.update_task_progress(task_id, 20)
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error loading image: {str(e)}')
            return
        
        # Apply adaptive contrast enhancement
        try:
            from filters.adaptive_enhancement import AdaptiveContrastEnhancement
            
            # Get parameters from request
            window_size = params.get('window_size', 15)
            clip_limit = params.get('clip_limit', 3.0)
            
            # Apply performance optimizations
            image_size = image.shape[0] * image.shape[1]
            
            # Determine if we should use performance optimizations
            use_optimizations = ENABLE_PERFORMANCE_OPTIMIZATIONS or image_size > 1000000  # 1 megapixel
            
            # Configure optimization parameters based on image size
            use_simplified_processing = False
            max_processing_dimension = 1200  # Default max dimension
            
            if use_optimizations:
                # Clear cache to ensure maximum memory availability
                clear_image_cache()
                
                # Reduce window size for large images
                window_size = min(window_size, 7)  
                
                # Disable entropy calculation for large images
                params['disable_entropy'] = True
                
                # For very large images, use simplified processing path
                if image_size > 2000000:  # 2 megapixels
                    use_simplified_processing = True
                    max_processing_dimension = 800  # More aggressive downscaling
                    print(f"Using simplified processing for very large image: {image_size} pixels")
                elif image_size > 1000000:  # 1 megapixel
                    max_processing_dimension = 1000  # Moderate downscaling
                
                # Log optimization info
                print(f"Using performance optimizations for image size: {image_size} pixels")
                print(f"Window size: {window_size}, Max dimension: {max_processing_dimension}")
            else:
                print(f"Using high-quality processing for image size: {image_size} pixels")
            
            # Create enhancement object with optimized parameters
            ace = AdaptiveContrastEnhancement(
                window_size=window_size,
                clip_limit=clip_limit,
                disable_entropy=params.get('disable_entropy', False),
                use_simplified_processing=use_simplified_processing,
                max_processing_dimension=max_processing_dimension
            )
            
            # Update progress callback
            def progress_callback(progress):
                task_manager.update_task_progress(task_id, 20 + int(progress * 0.6))
            
            # Apply enhancement with optimized functions
            ace.set_progress_callback(progress_callback)
            
            # Use optimized enhancement if available
            enhanced = ace.enhance(image)
            
            task_manager.update_task_progress(task_id, 80)
            
            # Free memory aggressively
            del image
            del ace
            gc.collect()
        except Exception as e:
            print(f"Error enhancing image: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error enhancing image: {str(e)}')
            return
        
        # Apply additional filters if specified
        try:
            # Check if multiple filters are specified
            filter_types = params.get('filter_types', [])
            
            # If filter_types is provided, apply each filter in sequence
            if filter_types:
                print(f"Applying multiple enhancement filters: {filter_types}")
                
                # Apply each enhancement filter in sequence
                for filter_type in filter_types:
                    print(f"Applying filter: {filter_type}")
                    
                    if filter_type == 'brightness_contrast':
                        bc_params = {
                            'brightness': params.get('brightness', 0.0),
                            'contrast': params.get('contrast', 1.0)
                        }
                        enhanced = apply_brightness_contrast(enhanced, bc_params)
                        
                    elif filter_type == 'exposure':
                        exposure_params = {
                            'exposure': params.get('exposure', 0.0),
                            'highlights': params.get('highlights', 0.0),
                            'shadows': params.get('shadows', 0.0)
                        }
                        enhanced = apply_exposure(enhanced, exposure_params)
                        
                    elif filter_type == 'vibrance':
                        vibrance_params = {
                            'vibrance': params.get('vibrance', 0.5),
                            'saturation': params.get('saturation', 0.0)
                        }
                        enhanced = apply_vibrance(enhanced, vibrance_params)
                        
                    elif filter_type == 'clarity':
                        clarity_params = {
                            'clarity': params.get('clarity', 0.5),
                            'edge_kernel': params.get('edge_kernel', 3),
                            'edge_scale': params.get('edge_scale', 1.0)
                        }
                        enhanced = apply_clarity(enhanced, clarity_params)
                        
                    elif filter_type == 'shadows_highlights':
                        sh_params = {
                            'shadows_recovery': params.get('shadows_recovery', 0.5),
                            'highlights_recovery': params.get('highlights_recovery', 0.5),
                            'mid_tone_contrast': params.get('mid_tone_contrast', 0.0)
                        }
                        enhanced = apply_shadows_highlights(enhanced, sh_params)
            
            # For backward compatibility, also handle individual filter flags
            # Apply morphological filters if specified
            if params.get('apply_morphological'):
                morph_type = params.get('morphological_type')
                kernel_size = params.get('kernel_size', 3)
                iterations = params.get('iterations', 1)
                
                morph_params = {
                    'kernel_size': kernel_size,
                    'iterations': iterations
                }
                
                if morph_type == 'dilation':
                    enhanced = apply_dilation(enhanced, morph_params)
                elif morph_type == 'erosion':
                    enhanced = apply_erosion(enhanced, morph_params)
                elif morph_type == 'opening':
                    enhanced = apply_opening(enhanced, morph_params)
                elif morph_type == 'closing':
                    enhanced = apply_closing(enhanced, morph_params)
            
            task_manager.update_task_progress(task_id, 85)
        except Exception as e:
            print(f"Error applying additional filters: {str(e)}")
            # Continue even if additional filters fail
        
        # Save the result with a unique timestamp to prevent overwriting
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        result_filename = f"enhanced_{timestamp}_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        
        try:
            save_image(enhanced, result_path)
            task_manager.update_task_progress(task_id, 90)
            
            # Free memory
            del enhanced
            gc.collect()
        except Exception as e:
            print(f"Error saving result: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error saving result: {str(e)}')
            return
        
        # Add to history
        try:
            history_id = history_manager.add_entry(filename, result_filename, params)
            task_manager.update_task_progress(task_id, 95)
        except Exception as e:
            print(f"Error adding to history: {str(e)}")
            # Continue even if history fails
        
        # Update task status
        task_manager.mark_task_completed(task_id, result_filename, history_id)
    except Exception as e:
        print(f"Unexpected error in process_image_task: {str(e)}")
        task_manager.mark_task_failed(task_id, f'Server error: {str(e)}')
    finally:
        # Make sure to clean up memory
        gc.collect()

def process_morphological_task(task_id, image_path, filename, params, use_compressed, data):
    """Process a morphological filter task in the background"""
    # Get the task from the processing_tasks dictionary
    task = task_manager.get_task(task_id)
    if not task:
        return
    
    try:
        # Update progress
        task_manager.update_task_progress(task_id, 10)
        
        # Load the image
        try:
            image = load_image(image_path)
            task_manager.update_task_progress(task_id, 20)
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error loading image: {str(e)}')
            return
        
        # Apply morphological filter
        try:
            filter_type = params.get('filter_type')
            
            # Apply performance optimizations
            image_size = image.shape[0] * image.shape[1]
            
            # Determine if we should use performance optimizations
            use_optimizations = ENABLE_PERFORMANCE_OPTIMIZATIONS or image_size > 1000000  # 1 megapixel
            
            if use_optimizations:
                # Clear cache to ensure maximum memory availability
                clear_image_cache()
                
                # Reduce kernel size for large images if not explicitly set
                if 'kernel_size' not in params:
                    params['kernel_size'] = 3  # Smaller kernel for better performance
                
                # Limit iterations for large images if not explicitly set
                if 'iterations' not in params:
                    params['iterations'] = 1  # Fewer iterations for better performance
                
                # Log optimization info
                print(f"Using performance optimizations for morphological filter on image size: {image_size} pixels")
            else:
                print(f"Using high-quality processing for morphological filter on image size: {image_size} pixels")
            
            # Select the appropriate filter function
            if filter_type == 'dilation':
                enhanced = apply_dilation(image, params)
            elif filter_type == 'erosion':
                enhanced = apply_erosion(image, params)
            elif filter_type == 'opening':
                enhanced = apply_opening(image, params)
            elif filter_type == 'closing':
                enhanced = apply_closing(image, params)
            elif filter_type == 'tophat':
                enhanced = apply_tophat(image, params)
            elif filter_type == 'blackhat':
                enhanced = apply_black_tophat(image, params)
            elif filter_type == 'gradient':
                enhanced = apply_morphological_gradient(image, params)
            elif filter_type == 'hitmiss':
                enhanced = apply_hit_miss_transform(image, params)
            elif filter_type == 'thinning':
                enhanced = apply_thinning(image, params)
            elif filter_type == 'thickening':
                enhanced = apply_thickening(image, params)
            elif filter_type == 'skeleton':
                enhanced = apply_skeletonization(image, params)
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")
            
            task_manager.update_task_progress(task_id, 80)
            
            # Free memory aggressively
            del image
            gc.collect()
        except Exception as e:
            print(f"Error applying morphological filter: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error applying filter: {str(e)}')
            return
        
        # Save the result with a unique timestamp to prevent overwriting
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        result_filename = f"morph_{filter_type}_{timestamp}_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        
        try:
            save_image(enhanced, result_path)
            task_manager.update_task_progress(task_id, 90)
            
            # Free memory
            del enhanced
            gc.collect()
        except Exception as e:
            print(f"Error saving result: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error saving result: {str(e)}')
            return
        
        # Add to history
        try:
            # Add filter type to params
            params['filter_type'] = filter_type
            params['is_morphological'] = True
                
            history_id = history_manager.add_entry(filename, result_filename, params)
            task.history_id = history_id
            task_manager.update_task_progress(task_id, 95)
        except Exception as e:
            print(f"Error adding to history: {str(e)}")
            # Continue even if history fails
        
        # Update task status
        task_manager.mark_task_completed(task_id, result_filename, history_id)
    except Exception as e:
        print(f"Unexpected error in process_morphological_task: {str(e)}")
        task_manager.mark_task_failed(task_id, f'Server error: {str(e)}')
    finally:
        # Make sure to clean up memory
        gc.collect()

def process_enhancement_task(task_id, image_path, filename, params, use_compressed, data):
    """Process an enhancement filter task in the background"""
    task = task_manager.get_task(task_id)
    if not task:
        return
    
    try:
        # Update progress
        task_manager.update_task_progress(task_id, 10)
        
        # Load the image
        try:
            image = load_image(image_path)
            task_manager.update_task_progress(task_id, 20)
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error loading image: {str(e)}')
            return
        
        # Apply enhancement filter
        try:
            filter_type = params.get('filter_type')
            
            # Apply performance optimizations
            image_size = image.shape[0] * image.shape[1]
            
            # Determine if we should use performance optimizations
            use_optimizations = ENABLE_PERFORMANCE_OPTIMIZATIONS or image_size > 1000000  # 1 megapixel
            
            if use_optimizations:
                # Clear cache to ensure maximum memory availability
                clear_image_cache()
                
                # Adjust parameters for better performance
                if filter_type == 'clarity' and 'edge_kernel' not in params:
                    params['edge_kernel'] = 3  # Smaller kernel for better performance
                
                # For shadows_highlights, use faster algorithm
                if filter_type == 'shadows_highlights':
                    params['fast_mode'] = True
                
                # Log optimization info
                print(f"Using performance optimizations for enhancement filter '{filter_type}' on image size: {image_size} pixels")
            else:
                print(f"Using high-quality processing for enhancement filter '{filter_type}' on image size: {image_size} pixels")
            
            # Select the appropriate filter function
            if filter_type == 'brightness_contrast':
                enhanced = apply_brightness_contrast(image, params)
            elif filter_type == 'exposure':
                enhanced = apply_exposure(image, params)
            elif filter_type == 'vibrance':
                enhanced = apply_vibrance(image, params)
            elif filter_type == 'clarity':
                enhanced = apply_clarity(image, params)
            elif filter_type == 'shadows_highlights':
                enhanced = apply_shadows_highlights(image, params)
            else:
                raise ValueError(f"Unknown enhancement filter type: {filter_type}")
            
            task_manager.update_task_progress(task_id, 80)
            
            # Free memory aggressively
            del image
            gc.collect()
        except Exception as e:
            print(f"Error applying enhancement filter: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error applying filter: {str(e)}')
            return
        
        # Save the result with a unique timestamp to prevent overwriting
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        result_filename = f"enhance_{filter_type}_{timestamp}_{filename}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        
        try:
            save_image(enhanced, result_path)
            task_manager.update_task_progress(task_id, 90)
            
            # Free memory
            del enhanced
            gc.collect()
        except Exception as e:
            print(f"Error saving result: {str(e)}")
            task_manager.mark_task_failed(task_id, f'Error saving result: {str(e)}')
            return
        
        # Add to history
        try:
            # Add filter type to params
            params['filter_type'] = filter_type
            params['is_enhancement'] = True
                
            history_id = history_manager.add_entry(filename, result_filename, params)
            task.history_id = history_id
            task_manager.update_task_progress(task_id, 95)
        except Exception as e:
            print(f"Error adding to history: {str(e)}")
            # Continue even if history fails
        
        # Update task status
        task_manager.mark_task_completed(task_id, result_filename, history_id)
    except Exception as e:
        print(f"Unexpected error in process_enhancement_task: {str(e)}")
        task_manager.mark_task_failed(task_id, f'Server error: {str(e)}')
    finally:
        # Make sure to clean up memory
        gc.collect()
