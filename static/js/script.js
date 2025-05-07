document.addEventListener('DOMContentLoaded', function() {
    // Morphological filters functionality
    // Variables for morphological filters
    let activeMorphologicalFilter = null;
    const morphologicalSection = document.querySelector('.morphological-section');
    const morphologicalHeader = document.querySelector('.morphological-section h3');
    const morphologicalToggle = document.querySelector('.morphological-toggle');
    const morphologicalContent = document.querySelector('.morphological-content');
    const morphologicalBtns = document.querySelectorAll('.morphological-btn');
    const morphologicalParams = document.querySelector('.morphological-params');
    const kernelSizeInput = document.getElementById('kernel-size');
    const kernelSizeValue = document.getElementById('kernel-size-value');
    const iterationsInput = document.getElementById('iterations');
    const iterationsValue = document.getElementById('iterations-value');
    const strengthInput = document.getElementById('strength');
    const strengthValue = document.getElementById('strength-value');
    const patternSelect = document.getElementById('pattern');
    const thresholdInput = document.getElementById('threshold');
    const thresholdValue = document.getElementById('threshold-value');
    const preserveOriginalCheckbox = document.getElementById('preserve-original');
    const maxIterationsInput = document.getElementById('max-iterations');
    const maxIterationsValue = document.getElementById('max-iterations-value');
    
    // Variables for enhancement filters
    let activeEnhancementFilter = null;
    const enhancementSection = document.querySelector('.enhancement-section');
    const enhancementHeader = document.querySelector('.enhancement-section h3');
    const enhancementToggle = document.querySelector('.enhancement-toggle');
    const enhancementContent = document.querySelector('.enhancement-content');
    const enhancementBtns = document.querySelectorAll('.enhancement-btn');
    const enhancementParams = document.querySelector('.enhancement-params');
    
    // Advanced options toggles
    const morphAdvancedToggle = document.querySelector('.morphological-section .advanced-toggle');
    const morphAdvancedOptions = document.querySelector('.morphological-section .advanced-options');
    const enhAdvancedToggle = document.querySelector('.enhancement-section .advanced-toggle');
    const enhAdvancedOptions = document.querySelector('.enhancement-section .advanced-options');
    const applyMorphologicalBtn = document.getElementById('apply-morphological');
    // Error handling function
    function showError(message) {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';
        errorContainer.textContent = message;
        
        // Add close button
        const closeBtn = document.createElement('span');
        closeBtn.className = 'close-error';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function() {
            document.body.removeChild(errorContainer);
        };
        
        errorContainer.appendChild(closeBtn);
        document.body.appendChild(errorContainer);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (document.body.contains(errorContainer)) {
                document.body.removeChild(errorContainer);
            }
        }, 5000);
    }
    
    // Check file type before upload
    function isValidImageType(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'];
        return validTypes.includes(file.type);
    }
    
    // DOM elements - Main UI
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    const originalImage = document.getElementById('original-image');
    const enhancedImage = document.getElementById('enhanced-image');
    const applyBtn = document.getElementById('apply-btn');
    const resetBtn = document.getElementById('reset-btn');
    const downloadBtn = document.getElementById('download-btn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const presetBtns = document.querySelectorAll('.preset-btn');
    
    // DOM elements - Main tabs
    const mainTabs = document.querySelectorAll('.main-tab');
    const mainTabContents = document.querySelectorAll('.main-tab-content');
    
    // DOM elements - History tab
    const historyList = document.getElementById('history-list');
    const historyDetail = document.getElementById('history-detail');
    const historyDetailContent = document.querySelector('.history-detail-content');
    const historyDetailEmpty = document.querySelector('.history-detail-empty');
    const historyDetailTitle = document.getElementById('history-detail-title');
    const historyOriginalImage = document.getElementById('history-original-image');
    const historyEnhancedImage = document.getElementById('history-enhanced-image');
    const historyDownloadBtn = document.getElementById('history-download-btn');
    const historyParametersList = document.getElementById('history-parameters-list');
    const refreshHistoryBtn = document.getElementById('refresh-history-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const reuseParamsBtn = document.getElementById('reuse-params-btn');
    const deleteHistoryBtn = document.getElementById('delete-history-btn');
    
    // Default parameters
    const defaultParams = {
        // General parameters
        window_size: 15,
        use_entropy: true,
        
        // Noise reduction parameters
        denoise: true,
        bilateral_strength: 1.0,
        bilateral_diameter: 9,
        denoise_blend_factor: 0.7,
        
        // Adaptive enhancement parameters
        gamma_min: 0.7,
        gamma_max: 1.5,
        contrast_strength: 2.0,
        entropy_factor: 0.3,
        
        // Detail enhancement parameters
        enhance_details: true,
        unsharp_kernel_size: 5,
        unsharp_sigma: 1.0,
        unsharp_amount: 1.0,
        
        // Final adjustment parameters
        apply_clahe: true,
        clahe_clip_limit: 2.0,
        clahe_blend: 0.5,
        apply_high_boost: true,
        high_boost_factor: 1.5,
        high_boost_blend: 0.3
    };
    
    // Preset parameters - Enhanced for better performance
    const presets = {
        dark_image: {
            // Optimized for recovering details in dark areas
            gamma_min: 0.4,            // Lower gamma min to brighten dark areas more
            gamma_max: 2.2,            // Higher gamma max for better contrast
            contrast_strength: 2.8,     // Increased contrast strength
            entropy_factor: 0.5,        // Higher entropy factor for better local adaptation
            clahe_clip_limit: 3.5,      // Higher clip limit for more aggressive histogram equalization
            clahe_blend: 0.8,           // Stronger CLAHE blend
            denoise: true,              // Enable denoising to reduce noise in dark areas
            bilateral_strength: 0.7,    // Lower bilateral strength to preserve details
            bilateral_diameter: 7,      // Smaller diameter for finer detail preservation
            denoise_blend_factor: 0.6,  // Lower blend factor to preserve details
            high_boost_factor: 1.8      // Higher boost factor for better detail enhancement
        },
        bright_image: {
            // Optimized for recovering details in bright/overexposed areas
            gamma_min: 0.9,             // Higher gamma min to preserve shadows
            gamma_max: 1.1,             // Lower gamma max to reduce highlights
            contrast_strength: 1.2,      // Lower contrast strength to prevent clipping
            entropy_factor: 0.2,         // Lower entropy factor for smoother transitions
            bilateral_strength: 1.4,     // Higher bilateral strength for smoother transitions
            bilateral_diameter: 11,      // Larger diameter for more smoothing
            denoise_blend_factor: 0.8,   // Higher blend factor for smoother results
            high_boost_factor: 1.0,      // Lower boost factor to prevent highlight clipping
            high_boost_blend: 0.2,       // Lower blend to prevent oversharpening
            clahe_clip_limit: 1.5,       // Lower clip limit to prevent artifacts
            clahe_blend: 0.4             // Lower blend for subtler effect
        },
        sharp_edges: {
            // Optimized for enhancing edge definition
            window_size: 9,              // Smaller window for finer detail detection
            bilateral_strength: 0.6,      // Lower bilateral strength to preserve edges
            bilateral_diameter: 5,        // Smaller diameter for edge preservation
            unsharp_amount: 2.0,          // Higher unsharp amount for stronger edge enhancement
            unsharp_sigma: 0.8,           // Lower sigma for finer edge detection
            high_boost_factor: 2.5,       // Higher boost factor for stronger edge enhancement
            high_boost_blend: 0.6,        // Higher blend for stronger effect
            entropy_factor: 0.5,          // Higher entropy factor for better local adaptation
            contrast_strength: 2.5,       // Higher contrast strength for better edge definition
            enhance_details: true          // Enable detail enhancement
        },
        blurry_image: {
            // Optimized for improving focus and reducing blur
            window_size: 7,               // Smaller window for finer detail detection
            bilateral_strength: 0.4,       // Lower bilateral strength to preserve details
            bilateral_diameter: 5,         // Smaller diameter for detail preservation
            unsharp_amount: 2.5,           // Higher unsharp amount for stronger sharpening
            unsharp_sigma: 1.0,            // Balanced sigma for good detail enhancement
            unsharp_kernel_size: 3,        // Smaller kernel for finer detail enhancement
            high_boost_factor: 2.8,        // Higher boost factor for stronger sharpening
            high_boost_blend: 0.7,         // Higher blend for stronger effect
            enhance_details: true,          // Enable detail enhancement
            clahe_clip_limit: 2.5,         // Higher clip limit for better local contrast
            clahe_blend: 0.6,              // Higher blend for stronger effect
            high_boost_blend: 0.6          // Higher blend for stronger effect
        },
        high_detail: {
            window_size: 5,
            bilateral_strength: 0.4,
            contrast_strength: 1.8,
            entropy_factor: 0.6,
            unsharp_amount: 1.8,
            high_boost_factor: 2.2,
            clahe_clip_limit: 3.0,
            clahe_blend: 0.7,
            high_boost_blend: 0.8,
            enhance_details: true
        },
        low_contrast: {
            contrast_strength: 3.0,
            gamma_min: 0.6,
            gamma_max: 1.8,
            clahe_clip_limit: 4.0,
            clahe_blend: 0.8,
            entropy_factor: 0.5,
            bilateral_diameter: 15,
            bilateral_strength: 1.2,
            unsharp_amount: 1.2,
            unsharp_sigma: 1.5,
            high_boost_factor: 1.8,
            high_boost_blend: 0.5
        }
    };
    
    // Current state
    let currentImage = null;
    let currentParams = {...defaultParams};
    let currentHistoryEntry = null;
    let currentTaskId = null;
    let processingInterval = null;
    let activePreset = null;
    
    // Initialize UI
    initializeUI();
    
    // Event listeners - Main UI
    imageInput.addEventListener('change', handleFileSelect);
    uploadForm.addEventListener('submit', handleUpload);
    applyBtn.addEventListener('click', applyEnhancement);
    resetBtn.addEventListener('click', resetParameters);
    
    // Event listeners for morphological filters section toggle
    if (morphologicalHeader) {
        morphologicalHeader.addEventListener('click', () => {
            morphologicalContent.classList.toggle('expanded');
            morphologicalToggle.classList.toggle('expanded');
        });
    }
    
    // Event listeners for enhancement section toggle
    if (enhancementHeader) {
        enhancementHeader.addEventListener('click', () => {
            enhancementContent.classList.toggle('expanded');
            enhancementToggle.classList.toggle('expanded');
        });
    }
    
    // Event listener for morphological advanced options toggle
    if (morphAdvancedToggle) {
        morphAdvancedToggle.addEventListener('click', () => {
            morphAdvancedOptions.classList.toggle('expanded');
            morphAdvancedToggle.textContent = morphAdvancedOptions.classList.contains('expanded') ? 
                'Hide Advanced Options' : 'Show Advanced Options';
        });
    }
    
    // Event listener for enhancement advanced options toggle
    if (enhAdvancedToggle) {
        enhAdvancedToggle.addEventListener('click', () => {
            enhAdvancedOptions.classList.toggle('expanded');
            enhAdvancedToggle.textContent = enhAdvancedOptions.classList.contains('expanded') ? 
                'Hide Advanced Options' : 'Show Advanced Options';
        });
    }
    
    // Event listeners for morphological filters
    morphologicalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            morphologicalBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Set active filter
            activeMorphologicalFilter = btn.dataset.filter;
            
            // Show parameters
            morphologicalParams.classList.add('active');
            
            // Show/hide conditional parameters based on filter type
            updateConditionalParams(activeMorphologicalFilter);
        });
    });
    
    // Function to update conditional parameters based on filter type
    function updateConditionalParams(filterType) {
        // Hide all conditional params first
        document.querySelectorAll('.conditional-param').forEach(param => {
            param.classList.remove('visible');
        });
        
        // Show relevant parameters based on filter type
        switch (filterType) {
            case 'tophat':
            case 'blackhat':
            case 'gradient':
                document.getElementById('strength-group').classList.add('visible');
                break;
            case 'hitmiss':
                document.getElementById('pattern-group').classList.add('visible');
                break;
            case 'thinning':
            case 'thickening':
            case 'skeleton':
                document.getElementById('threshold-group').classList.add('visible');
                document.getElementById('preserve-original-group').classList.add('visible');
                if (filterType === 'skeleton' || filterType === 'thinning') {
                    document.getElementById('max-iterations-group').classList.add('visible');
                }
                break;
        }
    }
    
    // Event listeners for enhancement filters
    enhancementBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            enhancementBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Set active filter
            activeEnhancementFilter = btn.dataset.filter;
            
            // Show parameters
            enhancementParams.classList.add('visible');
            
            // Show/hide conditional parameters based on filter type
            document.querySelectorAll('.enhancement-param-group').forEach(group => {
                group.style.display = 'none';
            });
            
            // Show specific parameters based on filter type
            switch(activeEnhancementFilter) {
                case 'brightness_contrast':
                    document.getElementById('brightness-group').style.display = 'flex';
                    document.getElementById('contrast-group').style.display = 'flex';
                    break;
                case 'exposure':
                    document.getElementById('exposure-group').style.display = 'flex';
                    document.getElementById('highlights-group').style.display = 'flex';
                    document.getElementById('shadows-group').style.display = 'flex';
                    break;
                case 'vibrance':
                    document.getElementById('vibrance-group').style.display = 'flex';
                    document.getElementById('saturation-group').style.display = 'flex';
                    break;
                case 'clarity':
                    document.getElementById('clarity-group').style.display = 'flex';
                    document.getElementById('edge-kernel-group').style.display = 'flex';
                    document.getElementById('edge-scale-group').style.display = 'flex';
                    break;
                case 'shadows_highlights':
                    document.getElementById('shadows-recovery-group').style.display = 'flex';
                    document.getElementById('highlights-recovery-group').style.display = 'flex';
                    document.getElementById('mid-tone-contrast-group').style.display = 'flex';
                    break;
            }
        });
    });
    
    // Event listeners - Morphological parameters
    if (kernelSizeInput) {
        kernelSizeInput.addEventListener('input', () => {
            kernelSizeValue.textContent = kernelSizeInput.value;
        });
    }
    
    if (iterationsInput) {
        iterationsInput.addEventListener('input', () => {
            iterationsValue.textContent = iterationsInput.value;
        });
    }
    
    if (strengthInput) {
        strengthInput.addEventListener('input', () => {
            strengthValue.textContent = strengthInput.value;
        });
    }
    
    if (thresholdInput) {
        thresholdInput.addEventListener('input', () => {
            thresholdValue.textContent = thresholdInput.value;
        });
    }
    
    if (maxIterationsInput) {
        maxIterationsInput.addEventListener('input', () => {
            maxIterationsValue.textContent = maxIterationsInput.value;
        });
    }
    
    // Event listeners - Enhancement parameters
    // Helper function to update slider value displays
    function setupSliderValueDisplay(sliderId, valueId) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);
        if (slider && valueDisplay) {
            slider.addEventListener('input', () => {
                valueDisplay.textContent = slider.value;
            });
        }
    }
    
    // Setup all enhancement sliders
    setupSliderValueDisplay('brightness', 'brightness-value');
    setupSliderValueDisplay('contrast', 'contrast-value');
    setupSliderValueDisplay('exposure', 'exposure-value');
    setupSliderValueDisplay('highlights', 'highlights-value');
    setupSliderValueDisplay('shadows', 'shadows-value');
    setupSliderValueDisplay('vibrance', 'vibrance-value');
    setupSliderValueDisplay('saturation', 'saturation-value');
    setupSliderValueDisplay('clarity', 'clarity-value');
    setupSliderValueDisplay('edge-kernel', 'edge-kernel-value');
    setupSliderValueDisplay('edge-scale', 'edge-scale-value');
    setupSliderValueDisplay('shadows-recovery', 'shadows-recovery-value');
    setupSliderValueDisplay('highlights-recovery', 'highlights-recovery-value');
    setupSliderValueDisplay('mid-tone-contrast', 'mid-tone-contrast-value');
    setupSliderValueDisplay('clahe-clip', 'clahe-clip-value');
    setupSliderValueDisplay('clahe-grid', 'clahe-grid-value');
    
    // Apply morphological filter button
    if (applyMorphologicalBtn) {
        applyMorphologicalBtn.addEventListener('click', applyMorphologicalFilter);
    }
    
    // Apply enhancement filter button
    const applyEnhancementBtn = document.getElementById('apply-btn');
    if (applyEnhancementBtn) {
        applyEnhancementBtn.addEventListener('click', applyEnhancementFilter);
    }
    
    // Function to apply morphological filter
    function applyMorphologicalFilter() {
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
                    startProcessingPolling(data.task_id, data.estimated_time);
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
    
    // Function to apply enhancement filter
    function applyEnhancementFilter() {
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
    
    // Event listeners - Main tabs
    mainTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and content
            mainTabs.forEach(t => t.classList.remove('active'));
            mainTabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
            
            // Load history if history tab is clicked
            if (tabId === 'history') {
                loadHistory();
            }
        });
    });
    
    // Event listeners - Parameter tabs
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');
        });
    });
    
    // Event listeners - Preset buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const presetName = btn.getAttribute('data-preset');
            applyPreset(presetName);
        });
    });
    
    // Event listeners - History tab
    refreshHistoryBtn.addEventListener('click', loadHistory);
    clearHistoryBtn.addEventListener('click', clearHistory);
    reuseParamsBtn.addEventListener('click', reuseHistoryParameters);
    deleteHistoryBtn.addEventListener('click', deleteHistoryEntry);
    
    // Parameter input change listeners
    document.querySelectorAll('input[type="range"]').forEach(input => {
        input.addEventListener('input', updateParamValue);
        input.addEventListener('change', updateParams);
    });
    
    document.querySelectorAll('input[type="checkbox"]').forEach(input => {
        input.addEventListener('change', updateParams);
    });
    
    // Loading indicator functions
    function showLoadingIndicator() {
        // Clear any existing polling
        if (processingInterval) {
            clearInterval(processingInterval);
            processingInterval = null;
        }
        
        // Create loading overlay if it doesn't exist
        let loadingOverlay = document.getElementById('loading-overlay');
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            document.body.appendChild(loadingOverlay);
            
            const loadingContent = document.createElement('div');
            loadingContent.className = 'loading-content';
            loadingOverlay.appendChild(loadingContent);
            
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            loadingContent.appendChild(spinner);
            
            const loadingText = document.createElement('div');
            loadingText.className = 'loading-text';
            loadingText.id = 'loading-text';
            loadingText.textContent = 'Processing image...';
            loadingContent.appendChild(loadingText);
            
            const progressContainer = document.createElement('div');
            progressContainer.className = 'progress-container';
            loadingContent.appendChild(progressContainer);
            
            const progressBar = document.createElement('div');
            progressBar.className = 'progress-bar';
            progressBar.id = 'progress-bar';
            progressContainer.appendChild(progressBar);
            
            const progressText = document.createElement('div');
            progressText.className = 'progress-text';
            progressText.id = 'progress-text';
            progressText.textContent = '0%';
            progressContainer.appendChild(progressText);
        }
        
        // Reset progress
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const loadingText = document.getElementById('loading-text');
        
        if (progressBar) progressBar.style.width = '0%';
        if (progressText) progressText.textContent = '0%';
        if (loadingText) loadingText.textContent = 'Processing image...';
        
        // Show the overlay
        loadingOverlay.style.display = 'flex';
        
        // Set enhanced image to loading state
        enhancedImage.src = "/static/img/loading.png";
    }
    
    function hideLoadingIndicator() {
        // Clear any existing polling
        if (processingInterval) {
            clearInterval(processingInterval);
            processingInterval = null;
        }
        
        // Hide the overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    function updateProgress(progress, text) {
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const loadingText = document.getElementById('loading-text');
        
        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${progress}%`;
        if (loadingText && text) loadingText.textContent = text;
    }
    
    function showEstimatedTime(seconds) {
        const loadingText = document.getElementById('loading-text');
        if (loadingText) {
            const timeStr = seconds < 60 
                ? `${Math.round(seconds)} seconds` 
                : `${Math.floor(seconds / 60)} min ${Math.round(seconds % 60)} sec`;
            loadingText.textContent = `Estimated processing time: ${timeStr}`;
        }
    }
    
    function startProcessingPolling(taskId, estimatedTime) {
        // Clear any existing polling
        if (processingInterval) {
            clearInterval(processingInterval);
        }
        
        // Show initial estimated time
        if (estimatedTime) {
            showEstimatedTime(estimatedTime);
            updateProgress(5, 'Starting processing...');
        }
        
        let startTime = Date.now();
        
        // Start polling for task status
        processingInterval = setInterval(() => {
            fetch(`/task/${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update progress
                        updateProgress(data.progress, getProgressMessage(data));
                        
                        if (data.status === 'completed') {
                            // Task completed
                            clearInterval(processingInterval);
                            processingInterval = null;
                            
                            // Update UI with result
                            updateEnhancedImage(data.result);
                            applyBtn.disabled = false;
                            hideLoadingIndicator();
                            
                            // Show success message
                            showError('Enhancement completed successfully');
                        } else if (data.status === 'failed') {
                            // Task failed
                            clearInterval(processingInterval);
                            processingInterval = null;
                            
                            showError('Error enhancing image: ' + data.error);
                            applyBtn.disabled = false;
                            hideLoadingIndicator();
                        }
                        // Otherwise continue polling
                    } else {
                        // Error getting task status
                        clearInterval(processingInterval);
                        processingInterval = null;
                        
                        showError('Error checking task status: ' + data.error);
                        applyBtn.disabled = false;
                        hideLoadingIndicator();
                    }
                })
                .catch(error => {
                    console.error('Error polling task status:', error);
                    
                    // After 30 seconds of errors, stop polling
                    if (Date.now() - startTime > 30000) {
                        clearInterval(processingInterval);
                        processingInterval = null;
                        
                        showError('Error checking task status. Please try again.');
                        applyBtn.disabled = false;
                        hideLoadingIndicator();
                    }
                });
        }, 1000); // Poll every second
    }
    
    function getProgressMessage(data) {
        if (data.status === 'processing') {
            if (data.progress < 20) {
                return 'Loading image...';
            } else if (data.progress < 50) {
                return 'Applying enhancement...';
            } else if (data.progress < 80) {
                return 'Processing details...';
            } else if (data.progress < 90) {
                return 'Saving result...';
            } else {
                return 'Finalizing...';
            }
        } else if (data.status === 'completed') {
            return 'Enhancement completed!';
        } else {
            return 'Processing image...';
        }
    }
    
    function updateEnhancedImage(resultFilename) {
        // Add timestamp to prevent browser caching
        const timestamp = new Date().getTime();
        enhancedImage.src = `/static/results/${resultFilename}?t=${timestamp}`;
        downloadBtn.href = `/static/results/${resultFilename}`;
        downloadBtn.download = `enhanced_${currentImage}`;
    }
    
    function updateActivePreset(presetName) {
        // Remove active class from all preset buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to selected preset button
        if (presetName) {
            const presetBtn = document.querySelector(`.preset-btn[data-preset="${presetName}"]`);
            if (presetBtn) {
                presetBtn.classList.add('active');
            }
        }
    }
    
    // Performance optimization functions
    function clearCache() {
        console.log('Clearing cache to improve performance');
        fetch('/clear_cache', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Cache cleared:', data.message);
            } else {
                console.error('Error clearing cache:', data.error);
            }
        })
        .catch(error => {
            console.error('Error clearing cache:', error);
        });
    }
    
    function analyzeImage(filename) {
        console.log('Analyzing image for performance insights:', filename);
        fetch(`/analyze/${filename}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Image analysis:', data.analysis);
                
                // Show performance insights if it's a potentially slow image
                const analysis = data.analysis;
                if (analysis.estimated_processing_time > 10.0 || 
                    analysis.file_size_kb > 2000 || 
                    analysis.pixel_count > 2000000) {
                    
                    // Create a performance tip message
                    let tipMessage = 'Performance Tip: ';
                    
                    if (analysis.has_exif) {
                        tipMessage += 'This image contains EXIF data which may slow processing. ';
                    }
                    
                    if (analysis.file_size_kb > 2000) {
                        tipMessage += 'This is a large file which may take longer to process. ';
                    }
                    
                    if (analysis.pixel_count > 2000000) {
                        tipMessage += 'This image has high resolution which increases processing time. ';
                    }
                    
                    if (analysis.format === 'bmp') {
                        tipMessage += 'BMP format is uncompressed and may be slower to process. ';
                    }
                    
                    // Add recommendation
                    tipMessage += 'Consider using a smaller or compressed image for faster processing.';
                    
                    // Show the tip
                    showError(tipMessage);
                }
            } else {
                console.error('Error analyzing image:', data.error);
            }
        })
        .catch(error => {
            console.error('Error analyzing image:', error);
        });
    }
    
    // History functions
    function loadHistory() {
        // Clear current history list
        historyList.innerHTML = '';
        
        // Show loading state
        historyList.innerHTML = '<div class="history-loading">Loading history...</div>';
        
        // Reset history detail view
        hideHistoryDetail();
        
        // Fetch history from server
        fetch('/history')
            .then(response => response.json())
            .then(data => {
                // Clear loading state
                historyList.innerHTML = '';
                
                if (data.success && data.history && data.history.length > 0) {
                    // Render history entries
                    data.history.forEach(entry => {
                        const historyEntry = createHistoryEntryElement(entry);
                        historyList.appendChild(historyEntry);
                    });
                } else {
                    // Show empty state
                    historyList.innerHTML = '<div class="history-empty">No history entries yet</div>';
                }
            })
            .catch(error => {
                console.error('Error loading history:', error);
                historyList.innerHTML = '<div class="history-empty">Error loading history</div>';
            });
    }
    
    function createHistoryEntryElement(entry) {
        const historyEntry = document.createElement('div');
        historyEntry.className = 'history-entry';
        historyEntry.dataset.id = entry.id;
        
        // Create info section
        const infoSection = document.createElement('div');
        infoSection.className = 'history-entry-info';
        
        // Create title
        const title = document.createElement('div');
        title.className = 'history-entry-title';
        title.textContent = entry.descriptive_name || 'Enhancement';
        infoSection.appendChild(title);
        
        // Create date
        const date = document.createElement('div');
        date.className = 'history-entry-date';
        date.textContent = entry.timestamp;
        infoSection.appendChild(date);
        
        historyEntry.appendChild(infoSection);
        
        // Create thumbnail
        const thumbnail = document.createElement('img');
        thumbnail.className = 'history-entry-thumbnail';
        thumbnail.src = `/static/results/${entry.result_filename}`;
        thumbnail.alt = 'Enhanced image';
        historyEntry.appendChild(thumbnail);
        
        // Add click event
        historyEntry.addEventListener('click', () => {
            // Remove active class from all entries
            document.querySelectorAll('.history-entry').forEach(e => e.classList.remove('active'));
            
            // Add active class to clicked entry
            historyEntry.classList.add('active');
            
            // Show history detail
            showHistoryDetail(entry);
        });
        
        return historyEntry;
    }
    
    function showHistoryDetail(entry) {
        // Store current history entry
        currentHistoryEntry = entry;
        
        // Hide empty state
        historyDetailEmpty.style.display = 'none';
        
        // Show detail content
        historyDetailContent.style.display = 'block';
        
        // Set title
        historyDetailTitle.textContent = entry.descriptive_name || 'Enhancement Details';
        
        // Set images
        historyOriginalImage.src = `/static/uploads/${entry.original_filename}`;
        historyEnhancedImage.src = `/static/results/${entry.result_filename}`;
        
        // Set download link
        historyDownloadBtn.href = `/static/results/${entry.result_filename}`;
        historyDownloadBtn.download = `enhanced_${entry.original_filename}`;
        
        // Render parameters
        renderHistoryParameters(entry.params);
    }
    
    function hideHistoryDetail() {
        // Clear current history entry
        currentHistoryEntry = null;
        
        // Show empty state
        historyDetailEmpty.style.display = 'block';
        
        // Hide detail content
        historyDetailContent.style.display = 'none';
    }
    
    function renderHistoryParameters(params) {
        // Clear parameters list
        historyParametersList.innerHTML = '';
        
        // Render each parameter
        Object.keys(params).forEach(key => {
            // Skip some internal parameters
            if (key === 'preset') return;
            
            const paramItem = document.createElement('div');
            paramItem.className = 'parameter-item';
            
            const paramName = document.createElement('div');
            paramName.className = 'parameter-name';
            paramName.textContent = formatParameterName(key);
            paramItem.appendChild(paramName);
            
            const paramValue = document.createElement('div');
            paramValue.className = 'parameter-value';
            paramValue.textContent = formatParameterValue(params[key]);
            paramItem.appendChild(paramValue);
            
            historyParametersList.appendChild(paramItem);
        });
        
        // Add preset info if available
        if (params.preset) {
            const presetItem = document.createElement('div');
            presetItem.className = 'parameter-item preset';
            
            const presetName = document.createElement('div');
            presetName.className = 'parameter-name';
            presetName.textContent = 'Preset';
            presetItem.appendChild(presetName);
            
            const presetValue = document.createElement('div');
            presetValue.className = 'parameter-value';
            presetValue.textContent = formatPresetName(params.preset);
            presetItem.appendChild(presetValue);
            
            historyParametersList.appendChild(presetItem);
        }
    }
    
    function formatParameterName(name) {
        // Convert snake_case to Title Case with spaces
        return name.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    function formatParameterValue(value) {
        if (typeof value === 'boolean') {
            return value ? 'Yes' : 'No';
        } else if (typeof value === 'number') {
            return value.toString();
        } else if (Array.isArray(value)) {
            return value.join(', ');
        } else {
            return value.toString();
        }
    }
    
    function formatPresetName(presetName) {
        // Convert snake_case to Title Case with spaces
        return presetName.split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    function reuseHistoryParameters() {
        if (!currentHistoryEntry) return;
        
        // Copy parameters from history entry
        currentParams = {...currentHistoryEntry.params};
        
        // Update UI to reflect parameters
        document.querySelectorAll('input[type="range"]').forEach(input => {
            const paramName = input.name;
            if (currentParams.hasOwnProperty(paramName)) {
                input.value = currentParams[paramName];
                const valueSpan = document.getElementById(`${input.id}-value`);
                if (valueSpan) {
                    valueSpan.textContent = currentParams[paramName];
                }
            }
        });
        
        document.querySelectorAll('input[type="checkbox"]').forEach(input => {
            const paramName = input.name;
            if (currentParams.hasOwnProperty(paramName)) {
                input.checked = currentParams[paramName];
            }
        });
        
        // Update active preset if present in parameters
        if (currentParams.preset) {
            updateActivePreset(currentParams.preset);
            activePreset = currentParams.preset;
        } else {
            updateActivePreset(null);
            activePreset = null;
        }
        
        // Switch to enhance tab
        document.querySelector('.main-tab[data-tab="enhance"]').click();
        
        // Apply to current image if one is loaded
        if (currentImage) {
            applyEnhancement();
        } else {
            showError('Parameters loaded from history. Upload an image to apply them.');
        }
    }
    
    function deleteHistoryEntry() {
        if (!currentHistoryEntry) return;
        
        // Confirm deletion
        if (!confirm('Are you sure you want to delete this history entry?')) return;
        
        // Delete history entry
        fetch(`/history/${currentHistoryEntry.id}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload history
                    loadHistory();
                    
                    // Show success message
                    showError('History entry deleted');
                } else {
                    showError('Error deleting history entry: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error deleting history entry:', error);
                showError('Error deleting history entry');
            });
    }
    
    function clearHistory() {
        // Confirm clearing
        if (!confirm('Are you sure you want to clear all history entries?')) return;
        
        // Clear history
        fetch('/history', {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload history
                    loadHistory();
                    
                    // Show success message
                    showError(`Cleared ${data.count} history entries`);
                } else {
                    showError('Error clearing history: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error clearing history:', error);
                showError('Error clearing history');
            });
    }
    
    // Functions
    function initializeUI() {
        // Set initial values for range inputs
        document.querySelectorAll('input[type="range"]').forEach(input => {
            const paramName = input.name;
            if (defaultParams.hasOwnProperty(paramName)) {
                input.value = defaultParams[paramName];
                const valueSpan = document.getElementById(`${input.id}-value`);
                if (valueSpan) {
                    valueSpan.textContent = defaultParams[paramName];
                }
            }
        });
        
        // Set initial values for checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(input => {
            const paramName = input.name;
            if (defaultParams.hasOwnProperty(paramName)) {
                input.checked = defaultParams[paramName];
            }
        });
        
        // Create placeholder image directory
        fetch('/create_placeholder');
        
        // Clear any previous file input
        if (imageInput) {
            imageInput.value = '';
            fileNameSpan.textContent = 'No file chosen';
        }
    }
    
    function handleFileSelect(event) {
        const file = event.target.files[0];
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
                
                // Submit the form to upload the image
                uploadForm.dispatchEvent(new Event('submit'));
            };
            reader.readAsDataURL(file);
        }
    }
    
    function handleUpload(event) {
        event.preventDefault();
        
        if (!imageInput.files || imageInput.files.length === 0) {
            showError('Please select an image to upload.');
            return;
        }
        
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        
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
                    showEstimatedTime(data.estimated_time);
                    
                    // If estimated time is very long, analyze the image
                    if (data.estimated_time > 8.0) {
                        analyzeImage(currentImage);
                    }
                }
                
                // If active preset exists, apply it automatically
                if (activePreset) {
                    applyPreset(activePreset);
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
    
    function applyEnhancement() {
        if (!currentImage) {
            showError('Please upload an image first.');
            return;
        }
        
        // Show loading state
        showLoadingIndicator();
        applyBtn.disabled = true;
        
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
                    startProcessingPolling(data.task_id, data.estimated_time);
                } else {
                    // Legacy synchronous response
                    updateEnhancedImage(data.result);
                    applyBtn.disabled = false;
                    hideLoadingIndicator();
                }
            } else {
                showError('Error enhancing image: ' + data.error);
                applyBtn.disabled = false;
                hideLoadingIndicator();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Error enhancing image. Please try again.');
            applyBtn.disabled = false;
            hideLoadingIndicator();
        });
    }
    
    function updateParamValue(event) {
        const input = event.target;
        const valueSpan = document.getElementById(`${input.id}-value`);
        if (valueSpan) {
            valueSpan.textContent = input.value;
        }
    }
    
    function updateParams() {
        // Update currentParams object with values from all inputs
        document.querySelectorAll('input[type="range"], input[type="checkbox"]').forEach(input => {
            const paramName = input.name;
            if (input.type === 'checkbox') {
                currentParams[paramName] = input.checked;
            } else {
                currentParams[paramName] = parseFloat(input.value);
            }
        });
        
        // Special handling for parameters that need to be integers
        const intParams = ['window_size', 'bilateral_diameter', 'unsharp_kernel_size'];
        intParams.forEach(param => {
            if (currentParams.hasOwnProperty(param)) {
                currentParams[param] = Math.round(currentParams[param]);
            }
        });
        
        // Special handling for tile_grid_size
        currentParams.clahe_tile_grid_size = [8, 8];
    }
    
    function resetParameters() {
        // Reset to default parameters
        currentParams = {...defaultParams};
        
        // Update UI to reflect default values
        document.querySelectorAll('input[type="range"]').forEach(input => {
            const paramName = input.name;
            if (defaultParams.hasOwnProperty(paramName)) {
                input.value = defaultParams[paramName];
                const valueSpan = document.getElementById(`${input.id}-value`);
                if (valueSpan) {
                    valueSpan.textContent = defaultParams[paramName];
                }
            }
        });
        
        document.querySelectorAll('input[type="checkbox"]').forEach(input => {
            const paramName = input.name;
            if (defaultParams.hasOwnProperty(paramName)) {
                input.checked = defaultParams[paramName];
            }
        });
        
        // Clear active preset
        updateActivePreset(null);
        activePreset = null;
        
        // Apply enhancement with default parameters if an image is loaded
        if (currentImage) {
            applyEnhancement();
        }
    }
    
    function applyPreset(presetName) {
        if (!presets[presetName]) {
            showError('Invalid preset');
            return;
        }
        
        const preset = presets[presetName];
        
        // Apply preset parameters to the form
        for (const [key, value] of Object.entries(preset)) {
            // Skip comments (properties that start with '//')
            if (typeof value === 'string' && value.startsWith('//')) continue;
            
            // Skip function values or other non-primitive types
            if (typeof value === 'function' || (typeof value === 'object' && value !== null)) continue;
            
            const input = document.getElementById(key.replace(/_/g, '-'));
            if (input) {
                if (typeof value === 'boolean') {
                    // Handle checkboxes
                    input.checked = value;
                } else {
                    // Handle numeric inputs
                    input.value = value;
                    // Trigger input event to update displayed values
                    const event = new Event('input');
                    input.dispatchEvent(event);
                }
            }
        }
        
        // Show success message
        const successMsg = document.createElement('div');
        successMsg.className = 'success-message';
        successMsg.textContent = `Applied ${presetName.replace('_', ' ')} preset`;
        document.body.appendChild(successMsg);
        
        // Remove after 3 seconds
        setTimeout(() => {
            successMsg.remove();
        }, 3000);
        
        document.querySelectorAll('input[type="checkbox"]').forEach(input => {
            const paramName = input.name;
            if (currentParams.hasOwnProperty(paramName)) {
                input.checked = currentParams[paramName];
            }
        });
        
        // Apply enhancement with preset parameters if an image is loaded
        if (currentImage) {
            applyEnhancement();
        }
    }
});
