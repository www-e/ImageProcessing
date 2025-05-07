/**
 * Main entry point for the image processing application
 * This file imports and initializes all the modules
 */

// Import modules
import { showError, setupSliderValueDisplay } from './modules/utils.js';
import { 
    showLoadingIndicator, 
    hideLoadingIndicator, 
    startProcessingPolling 
} from './modules/loading.js';
import { 
    defaultParams, 
    presets, 
    applyPreset, 
    updateActivePreset 
} from './modules/presets.js';
import { 
    handleFileSelect, 
    handleUpload, 
    applyEnhancement, 
    applyMorphologicalFilter, 
    applyEnhancementFilter, 
    updateEnhancedImage, 
    getCurrentImage 
} from './modules/imageHandling.js';
import { 
    clearCache, 
    analyzeImage 
} from './modules/performance.js';
import { 
    loadHistory, 
    reuseHistoryParameters, 
    deleteHistoryEntry, 
    clearHistory 
} from './modules/history.js';
import { 
    initializeUI, 
    setupTabs, 
    setupSectionToggles, 
    setupFilterButtons, 
    updateParamValue, 
    updateParams, 
    resetParameters 
} from './modules/uiControls.js';

// Execute when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Current state
    let currentImage = null;
    let currentParams = {...defaultParams};
    let currentHistoryEntry = null;
    let activePreset = null;
    
    // DOM elements - Main UI
    const uploadForm = document.getElementById('upload-form');
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    const originalImage = document.getElementById('original-image');
    const enhancedImage = document.getElementById('enhanced-image');
    const applyBtn = document.getElementById('apply-btn');
    const resetBtn = document.getElementById('reset-btn');
    const downloadBtn = document.getElementById('download-btn');
    const presetBtns = document.querySelectorAll('.preset-btn');
    
    // DOM elements - Morphological filters
    const applyMorphologicalBtn = document.getElementById('apply-morphological');
    
    // DOM elements - History tab
    const refreshHistoryBtn = document.getElementById('refresh-history-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const reuseParamsBtn = document.getElementById('reuse-params-btn');
    const deleteHistoryBtn = document.getElementById('delete-history-btn');
    
    // Initialize UI
    initializeUI();
    setupTabs();
    setupSectionToggles();
    setupFilterButtons();
    
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
    
    // Setup morphological parameter sliders
    setupSliderValueDisplay('kernel-size', 'kernel-size-value');
    setupSliderValueDisplay('iterations', 'iterations-value');
    setupSliderValueDisplay('strength', 'strength-value');
    setupSliderValueDisplay('threshold', 'threshold-value');
    setupSliderValueDisplay('max-iterations', 'max-iterations-value');
    
    // Event listeners - Main UI
    imageInput.addEventListener('change', (event) => handleFileSelect(event, () => {
        uploadForm.dispatchEvent(new Event('submit'));
    }));
    
    uploadForm.addEventListener('submit', (event) => handleUpload(event, activePreset, (presetName) => {
        applyPreset(presetName, currentParams, (updatedParams) => {
            currentParams = updatedParams;
            activePreset = presetName;
        });
    }));
    
    applyBtn.addEventListener('click', () => applyEnhancement(currentParams));
    
    resetBtn.addEventListener('click', () => {
        const updatedParams = resetParameters(currentParams, (params, preset) => {
            currentParams = params;
            activePreset = preset;
            updateActivePreset(preset);
        });
        
        // Apply enhancement with default parameters if an image is loaded
        if (getCurrentImage()) {
            applyEnhancement(updatedParams);
        }
    });
    
    // Event listeners - Preset buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const presetName = btn.getAttribute('data-preset');
            const updatedParams = applyPreset(presetName, currentParams, (params) => {
                currentParams = params;
                activePreset = presetName;
            });
            
            // Apply to current image if one is loaded
            if (getCurrentImage()) {
                applyEnhancement(updatedParams);
            }
        });
    });
    
    // Event listeners - History tab
    refreshHistoryBtn.addEventListener('click', loadHistory);
    clearHistoryBtn.addEventListener('click', clearHistory);
    reuseParamsBtn.addEventListener('click', () => {
        reuseHistoryParameters(currentParams, (params, preset) => {
            currentParams = params;
            activePreset = preset;
        });
    });
    deleteHistoryBtn.addEventListener('click', deleteHistoryEntry);
    
    // Apply morphological filter button
    if (applyMorphologicalBtn) {
        applyMorphologicalBtn.addEventListener('click', applyMorphologicalFilter);
    }
    
    // Event listeners - Apply enhancement filter button
    const applyEnhancementBtn = document.getElementById('apply-enhancement-btn');
    if (applyEnhancementBtn) {
        applyEnhancementBtn.addEventListener('click', applyEnhancementFilter);
    }
    
    // Parameter input change listeners
    document.querySelectorAll('input[type="range"]').forEach(input => {
        input.addEventListener('input', updateParamValue);
        input.addEventListener('change', () => {
            currentParams = updateParams(currentParams);
        });
    });
    
    document.querySelectorAll('input[type="checkbox"]').forEach(input => {
        input.addEventListener('change', () => {
            currentParams = updateParams(currentParams);
        });
    });
});
