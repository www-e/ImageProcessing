/**
 * Presets and default parameters for image enhancement
 */

// Default parameters
export const defaultParams = {
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
export const presets = {
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

// Apply preset to form inputs and update parameters
export function applyPreset(presetName, currentParams, updateCallback) {
    if (!presets[presetName]) {
        console.error('Invalid preset:', presetName);
        return null;
    }
    
    const preset = presets[presetName];
    const updatedParams = { ...currentParams };
    
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
        
        // Update the params object
        updatedParams[key] = value;
    }
    
    // Add preset name to params
    updatedParams.preset = presetName;
    
    // Update UI if callback provided
    if (updateCallback) {
        updateCallback(updatedParams);
    }
    
    return updatedParams;
}

// Update active preset button in UI
export function updateActivePreset(presetName) {
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
