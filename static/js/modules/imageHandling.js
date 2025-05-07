/**
 * Image handling functionality - upload, enhancement, and processing
 */

import { showError, isValidImageType } from './utils.js';
import { showLoadingIndicator, hideLoadingIndicator, startProcessingPolling } from './loading.js';
import { clearCache, analyzeImage } from './performance.js';

// State variables
let currentImage = null;
let currentTaskId = null;

// Update enhanced image with result
export function updateEnhancedImage(resultFilename) {
    const enhancedImage = document.getElementById('enhanced-image');
    const downloadBtn = document.getElementById('download-btn');
    
    // Add timestamp to prevent browser caching
    const timestamp = new Date().getTime();
    enhancedImage.src = `/static/results/${resultFilename}?t=${timestamp}`;
    downloadBtn.href = `/static/results/${resultFilename}`;
    downloadBtn.download = `enhanced_${currentImage}`;
}

// Handle file selection
export function handleFileSelect(event, uploadCallback) {
    const file = event.target.files[0];
    const fileNameSpan = document.getElementById('file-name');
    const imageInput = document.getElementById('image-input');
    const originalImage = document.getElementById('original-image');
    const enhancedImage = document.getElementById('enhanced-image');
    const applyBtn = document.getElementById('apply-btn');
    
    if (file) {
        // Validate file type
        if (!isValidImageType(file)) {
            showError('Unsupported file type. Please upload a JPEG, PNG, BMP, or TIFF image.');
            imageInput.value = ''; // Clear the file input
            fileNameSpan.textContent = 'No file chosen';
            return;
        }
        
        fileNameSpan.textContent = file.name;
        
        // Create a preview of the original image
        const reader = new FileReader();
        reader.onload = function(e) {
            originalImage.src = e.target.result;
            enhancedImage.src = "/static/img/placeholder.png";
            applyBtn.disabled = false;
            
            // Reset current image to force a new upload
            currentImage = null;
            
            // Call upload callback if provided
            if (uploadCallback) {
                uploadCallback();
            }
        };
        reader.readAsDataURL(file);
    }
}

// Handle image upload
export function handleUpload(event, activePreset, applyPresetCallback) {
    event.preventDefault();
    
    const imageInput = document.getElementById('image-input');
    const originalImage = document.getElementById('original-image');
    const enhancedImage = document.getElementById('enhanced-image');
    const applyBtn = document.getElementById('apply-btn');
    
    if (!imageInput.files || imageInput.files.length === 0) {
        showError('Please select an image to upload.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', imageInput.files[0]);
    
    // Show loading state
    originalImage.src = "/static/img/loading.png";
    enhancedImage.src = "/static/img/placeholder.png";
    
    // Clear cache if needed (for large files)
    if (imageInput.files[0].size > 1024 * 1024 * 2) { // If larger than 2MB
        clearCache();
    }
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentImage = data.filename;
            // Add timestamp to prevent browser caching
            const timestamp = new Date().getTime();
            originalImage.src = `/static/uploads/${currentImage}?t=${timestamp}`;
            applyBtn.disabled = false;
            
            // If we have an estimated time, show it
            if (data.estimated_time) {
                import('./loading.js').then(module => {
                    module.showEstimatedTime(data.estimated_time);
                    
                    // If estimated time is very long, analyze the image
                    if (data.estimated_time > 8.0) {
                        analyzeImage(currentImage);
                    }
                });
            }
            
            // If active preset exists, apply it automatically
            if (activePreset && applyPresetCallback) {
                applyPresetCallback(activePreset);
            }
        } else {
            showError('Error uploading file: ' + data.error);
            originalImage.src = "/static/img/placeholder.png";
            applyBtn.disabled = true;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error uploading file. Please try again.');
        originalImage.src = "/static/img/placeholder.png";
        applyBtn.disabled = true;
    });
}

// Apply enhancement to current image
export function applyEnhancement(currentParams) {
    if (!currentImage) {
        showError('Please upload an image first.');
        return;
    }
    
    // Show loading state
    showLoadingIndicator();
    document.getElementById('apply-btn').disabled = true;
    
    // Check if we're using a preset
    const requestData = {
        filename: currentImage,
        params: currentParams
    };
    
    // If we have a preset name, include it
    if (currentParams.preset) {
        requestData.preset = currentParams.preset;
    }
    
    // Send parameters to server
    fetch('/enhance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.task_id) {
                // Async processing - start polling for status
                currentTaskId = data.task_id;
                startProcessingPolling(data.task_id, data.estimated_time, updateEnhancedImage);
            } else {
                // Legacy synchronous response
                updateEnhancedImage(data.result);
                document.getElementById('apply-btn').disabled = false;
                hideLoadingIndicator();
            }
        } else {
            showError('Error enhancing image: ' + data.error);
            document.getElementById('apply-btn').disabled = false;
            hideLoadingIndicator();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error enhancing image. Please try again.');
        document.getElementById('apply-btn').disabled = false;
        hideLoadingIndicator();
    });
}

// Apply morphological filter
export function applyMorphologicalFilter() {
    const activeMorphologicalFilter = document.querySelector('.morphological-btn.active')?.dataset.filter;
    const kernelSizeInput = document.getElementById('kernel-size');
    const iterationsInput = document.getElementById('iterations');
    const strengthInput = document.getElementById('strength');
    const patternSelect = document.getElementById('pattern');
    const thresholdInput = document.getElementById('threshold');
    const preserveOriginalCheckbox = document.getElementById('preserve-original');
    const maxIterationsInput = document.getElementById('max-iterations');
    
    if (!activeMorphologicalFilter) {
        showError('Please select a morphological filter first');
        return;
    }
    
    if (!currentImage) {
        showError('Please upload an image first');
        return;
    }
    
    // Show loading indicator
    showLoadingIndicator();
    
    // Get parameters
    const params = {
        filter_type: activeMorphologicalFilter,
        kernel_size: parseInt(kernelSizeInput.value),
        iterations: parseInt(iterationsInput.value)
    };
    
    // Add conditional parameters based on filter type
    switch(activeMorphologicalFilter) {
        case 'white_tophat':
        case 'black_tophat':
            params.strength = parseFloat(strengthInput.value);
            break;
        case 'morphological_gradient':
            params.strength = parseFloat(strengthInput.value);
            params.preserve_original = preserveOriginalCheckbox.checked;
            break;
        case 'hit_miss_transform':
            params.pattern = patternSelect.value;
            break;
        case 'thinning':
        case 'thickening':
            params.max_iterations = parseInt(maxIterationsInput.value);
            params.threshold = parseInt(thresholdInput.value);
            break;
        case 'skeletonization':
            params.threshold = parseInt(thresholdInput.value);
            break;
    }
    
    // Show loading spinner
    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'flex';
    }
    
    // Send request to server
    fetch('/apply_morphological', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            // Start polling for task status
            if (data.task_id) {
                startProcessingPolling(data.task_id, data.estimated_time, updateEnhancedImage);
            } else {
                showError('No task ID returned from server');
            }
        }
    })
    .catch(error => {
        showError('Error applying filter: ' + error.message);
    })
    .finally(() => {
        // Hide loading spinner
        if (loadingSpinner) {
            loadingSpinner.style.display = 'none';
        }
    });
}

// Apply enhancement filter
export function applyEnhancementFilter() {
    const activeEnhancementFilter = document.querySelector('.enhancement-btn.active')?.dataset.filter;
    
    if (!activeEnhancementFilter) {
        showError('Please select an enhancement filter first');
        return;
    }
    
    if (!currentImage) {
        showError('Please upload an image first');
        return;
    }
    
    // Get parameters based on the active enhancement filter
    const params = {
        filter_type: activeEnhancementFilter
    };
    
    // Add conditional parameters based on filter type
    switch(activeEnhancementFilter) {
        case 'brightness_contrast':
            params.brightness = parseFloat(document.getElementById('brightness').value);
            params.contrast = parseFloat(document.getElementById('contrast').value);
            break;
        case 'exposure':
            params.exposure = parseFloat(document.getElementById('exposure').value);
            params.highlights = parseFloat(document.getElementById('highlights').value);
            params.shadows = parseFloat(document.getElementById('shadows').value);
            break;
        case 'vibrance':
            params.vibrance = parseFloat(document.getElementById('vibrance').value);
            params.saturation = parseFloat(document.getElementById('saturation').value);
            break;
        case 'clarity':
            params.clarity = parseFloat(document.getElementById('clarity').value);
            params.edge_kernel = parseInt(document.getElementById('edge-kernel').value);
            params.edge_scale = parseFloat(document.getElementById('edge-scale').value);
            
            // Advanced options if available
            if (document.getElementById('apply-clahe')) {
                params.apply_clahe = document.getElementById('apply-clahe').checked;
            }
            if (document.getElementById('clahe-clip')) {
                params.clahe_clip = parseFloat(document.getElementById('clahe-clip').value);
            }
            if (document.getElementById('clahe-grid')) {
                params.clahe_grid = parseInt(document.getElementById('clahe-grid').value);
            }
            break;
        case 'shadows_highlights':
            params.shadows_recovery = parseFloat(document.getElementById('shadows-recovery').value);
            params.highlights_recovery = parseFloat(document.getElementById('highlights-recovery').value);
            params.mid_tone_contrast = parseFloat(document.getElementById('mid-tone-contrast').value);
            break;
    }
    
    // Show loading spinner
    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.style.display = 'flex';
    }
    
    // Send request to server
    fetch('/apply_enhancement', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showError(data.error);
        } else {
            // Update result image
            const resultImg = document.getElementById('result-image');
            resultImg.src = data.result_image + '?t=' + new Date().getTime(); // Add timestamp to prevent caching
            resultImg.style.display = 'block';
            
            // Show result section
            document.getElementById('result-section').style.display = 'block';
            
            // Scroll to result
            document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(error => {
        showError('Error applying enhancement: ' + error.message);
    })
    .finally(() => {
        // Hide loading spinner
        document.getElementById('loading-spinner').style.display = 'none';
    });
}

// Get current image filename
export function getCurrentImage() {
    return currentImage;
}

// Set current image filename
export function setCurrentImage(filename) {
    currentImage = filename;
}
