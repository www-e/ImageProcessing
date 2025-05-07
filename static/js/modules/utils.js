/**
 * Utility functions for the image processing application
 */

// Error handling function
export function showError(message) {
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
export function isValidImageType(file) {
    const validTypes = ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff'];
    return validTypes.includes(file.type);
}

// Helper function to update slider value displays
export function setupSliderValueDisplay(sliderId, valueId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById(valueId);
    if (slider && valueDisplay) {
        slider.addEventListener('input', () => {
            valueDisplay.textContent = slider.value;
        });
    }
}

// Format parameter name (snake_case to Title Case)
export function formatParameterName(name) {
    // Convert snake_case to Title Case with spaces
    return name.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Format parameter value based on type
export function formatParameterValue(value) {
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

// Format preset name (snake_case to Title Case)
export function formatPresetName(presetName) {
    // Convert snake_case to Title Case with spaces
    return presetName.split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
