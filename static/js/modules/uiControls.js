/**
 * UI control functionality - tabs, toggles, and parameter updates
 */

import { showError } from './utils.js';
import { defaultParams } from './presets.js';
import { loadHistory } from './history.js';

// Update conditional parameters based on filter type
export function updateConditionalParams(filterType) {
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

// Initialize UI elements with default values
export function initializeUI() {
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
    const imageInput = document.getElementById('image-input');
    const fileNameSpan = document.getElementById('file-name');
    if (imageInput) {
        imageInput.value = '';
        fileNameSpan.textContent = 'No file chosen';
    }
}

// Setup tab functionality
export function setupTabs() {
    // Main tabs
    const mainTabs = document.querySelectorAll('.main-tab');
    const mainTabContents = document.querySelectorAll('.main-tab-content');
    
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
    
    // Parameter tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
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
}

// Setup section toggles
export function setupSectionToggles() {
    // Morphological section toggle
    const morphologicalHeader = document.querySelector('.morphological-section h3');
    const morphologicalContent = document.querySelector('.morphological-content');
    const morphologicalToggle = document.querySelector('.morphological-toggle');
    
    if (morphologicalHeader) {
        morphologicalHeader.addEventListener('click', () => {
            morphologicalContent.classList.toggle('expanded');
            morphologicalToggle.classList.toggle('expanded');
        });
    }
    
    // Enhancement section toggle
    const enhancementHeader = document.querySelector('.enhancement-section h3');
    const enhancementContent = document.querySelector('.enhancement-content');
    const enhancementToggle = document.querySelector('.enhancement-toggle');
    
    if (enhancementHeader) {
        enhancementHeader.addEventListener('click', () => {
            enhancementContent.classList.toggle('expanded');
            enhancementToggle.classList.toggle('expanded');
        });
    }
    
    // Advanced options toggles
    const morphAdvancedToggle = document.querySelector('.morphological-section .advanced-toggle');
    const morphAdvancedOptions = document.querySelector('.morphological-section .advanced-options');
    
    if (morphAdvancedToggle) {
        morphAdvancedToggle.addEventListener('click', () => {
            morphAdvancedOptions.classList.toggle('expanded');
            morphAdvancedToggle.textContent = morphAdvancedOptions.classList.contains('expanded') ? 
                'Hide Advanced Options' : 'Show Advanced Options';
        });
    }
    
    const enhAdvancedToggle = document.querySelector('.enhancement-section .advanced-toggle');
    const enhAdvancedOptions = document.querySelector('.enhancement-section .advanced-options');
    
    if (enhAdvancedToggle) {
        enhAdvancedToggle.addEventListener('click', () => {
            enhAdvancedOptions.classList.toggle('expanded');
            enhAdvancedToggle.textContent = enhAdvancedOptions.classList.contains('expanded') ? 
                'Hide Advanced Options' : 'Show Advanced Options';
        });
    }
}

// Setup filter buttons
export function setupFilterButtons() {
    // Morphological filter buttons
    const morphologicalBtns = document.querySelectorAll('.morphological-btn');
    const morphologicalParams = document.querySelector('.morphological-params');
    
    morphologicalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons
            morphologicalBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            
            // Set active filter
            const activeMorphologicalFilter = btn.dataset.filter;
            
            // Show parameters
            morphologicalParams.classList.add('active');
            
            // Show/hide conditional parameters based on filter type
            updateConditionalParams(activeMorphologicalFilter);
        });
    });
    
    // Enhancement filter buttons
    const enhancementBtns = document.querySelectorAll('.enhancement-btn');
    const enhancementParams = document.querySelector('.enhancement-params');
    
    // Add counter for selected filters
    let selectedFiltersCount = 0;
    const MAX_FILTERS = 4;
    
    enhancementBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Toggle active class on clicked button
            if (btn.classList.contains('active')) {
                // If already active, deactivate it
                btn.classList.remove('active');
                selectedFiltersCount--;
            } else {
                // If not active and we haven't reached the limit, activate it
                if (selectedFiltersCount < MAX_FILTERS) {
                    btn.classList.add('active');
                    selectedFiltersCount++;
                } else {
                    // If we've reached the limit, show an error message
                    showError(`You can only select up to ${MAX_FILTERS} enhancement filters at once`);
                    return;
                }
            }
            
            // Show parameters if at least one filter is selected
            if (selectedFiltersCount > 0) {
                enhancementParams.classList.add('visible');
            } else {
                enhancementParams.classList.remove('visible');
            }
            
            // Show/hide conditional parameters based on selected filters
            document.querySelectorAll('.enhancement-param-group').forEach(group => {
                group.style.display = 'none';
            });
            
            // Get the clicked filter type
            const clickedFilterType = btn.dataset.filter;
            
            // Show specific parameters based on filter type
            switch(clickedFilterType) {
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
}

// Update parameter value in UI
export function updateParamValue(event) {
    const input = event.target;
    const valueSpan = document.getElementById(`${input.id}-value`);
    if (valueSpan) {
        valueSpan.textContent = input.value;
    }
}

// Update parameters object from UI inputs
export function updateParams(currentParams) {
    const updatedParams = { ...currentParams };
    
    // Update currentParams object with values from all inputs
    document.querySelectorAll('input[type="range"], input[type="checkbox"]').forEach(input => {
        const paramName = input.name;
        if (input.type === 'checkbox') {
            updatedParams[paramName] = input.checked;
        } else {
            updatedParams[paramName] = parseFloat(input.value);
        }
    });
    
    // Special handling for parameters that need to be integers
    const intParams = ['window_size', 'bilateral_diameter', 'unsharp_kernel_size'];
    intParams.forEach(param => {
        if (updatedParams.hasOwnProperty(param)) {
            updatedParams[param] = Math.round(updatedParams[param]);
        }
    });
    
    // Special handling for tile_grid_size
    updatedParams.clahe_tile_grid_size = [8, 8];
    
    return updatedParams;
}

// Reset parameters to default values
export function resetParameters(currentParams, updateCallback) {
    // Reset to default parameters
    const updatedParams = {...defaultParams};
    
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
    
    // Call the callback to update parameters in parent component
    if (updateCallback) {
        updateCallback(updatedParams, null);
    }
    
    return updatedParams;
}
