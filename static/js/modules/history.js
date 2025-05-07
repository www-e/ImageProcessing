/**
 * History functionality for tracking and managing enhancement history
 */

import { showError, formatParameterName, formatParameterValue, formatPresetName } from './utils.js';
import { updateActivePreset } from './presets.js';
import { applyEnhancement } from './imageHandling.js';

// State variables
let currentHistoryEntry = null;

// Load history from server
export function loadHistory() {
    const historyList = document.getElementById('history-list');
    
    // Clear current history list
    historyList.innerHTML = '';
    
    // Show loading state
    historyList.innerHTML = '<div class="history-loading">Loading history...</div>';
    
    // Reset history detail view
    hideHistoryDetail();
    
    // Fetch history from server
    console.log('Fetching history from server...');
    fetch('/history')
        .then(response => {
            console.log('History response status:', response.status);
            return response.json();
        })
        .then(data => {
            // Clear loading state
            historyList.innerHTML = '';
            
            console.log('History data received:', data);
            
            if (data.success && data.history && data.history.length > 0) {
                console.log(`Rendering ${data.history.length} history entries`);
                // Sort history entries by timestamp (newest first)
                const sortedHistory = [...data.history].sort((a, b) => {
                    return new Date(b.timestamp) - new Date(a.timestamp);
                });
                
                // Render history entries
                sortedHistory.forEach(entry => {
                    console.log('Creating entry element for:', entry.id);
                    const historyEntry = createHistoryEntryElement(entry);
                    historyList.appendChild(historyEntry);
                });
                
                // Show the first entry by default
                if (sortedHistory.length > 0) {
                    const firstEntry = document.querySelector('.history-entry');
                    if (firstEntry) {
                        firstEntry.classList.add('active');
                        showHistoryDetail(sortedHistory[0]);
                    }
                }
            } else {
                console.log('No history entries found or success=false');
                // Show empty state
                historyList.innerHTML = '<div class="history-empty">No history entries yet</div>';
            }
        })
        .catch(error => {
            console.error('Error loading history:', error);
            historyList.innerHTML = '<div class="history-empty">Error loading history</div>';
        });
}

// Create history entry element
export function createHistoryEntryElement(entry) {
    console.log('Creating history entry element with data:', entry);
    
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
    const thumbnailUrl = `/static/results/${entry.result_filename}`;
    console.log('Setting thumbnail image src to:', thumbnailUrl);
    thumbnail.src = thumbnailUrl;
    thumbnail.alt = 'Enhanced image';
    
    // Add error handling for thumbnail
    thumbnail.onerror = () => {
        console.error('Failed to load thumbnail image:', thumbnailUrl);
        thumbnail.src = '/static/images/placeholder.png';
        thumbnail.alt = 'Image not found';
    };
    
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

// Show history detail
export function showHistoryDetail(entry) {
    console.log('Showing history detail for entry:', entry);
    
    const historyDetailEmpty = document.querySelector('.history-detail-empty');
    const historyDetailContent = document.querySelector('.history-detail-content');
    const historyDetailTitle = document.getElementById('history-detail-title');
    const historyOriginalImage = document.getElementById('history-original-image');
    const historyEnhancedImage = document.getElementById('history-enhanced-image');
    const historyDownloadBtn = document.getElementById('history-download-btn');
    
    if (!historyDetailEmpty || !historyDetailContent || !historyDetailTitle || 
        !historyOriginalImage || !historyEnhancedImage || !historyDownloadBtn) {
        console.error('One or more history detail elements not found in the DOM');
        console.log('historyDetailEmpty:', historyDetailEmpty);
        console.log('historyDetailContent:', historyDetailContent);
        console.log('historyDetailTitle:', historyDetailTitle);
        console.log('historyOriginalImage:', historyOriginalImage);
        console.log('historyEnhancedImage:', historyEnhancedImage);
        console.log('historyDownloadBtn:', historyDownloadBtn);
        return;
    }
    
    // Store current history entry
    currentHistoryEntry = entry;
    
    // Hide empty state
    historyDetailEmpty.style.display = 'none';
    
    // Show detail content
    historyDetailContent.style.display = 'block';
    
    // Set title
    historyDetailTitle.textContent = entry.descriptive_name || 'Enhancement Details';
    
    // Set images
    const originalImageUrl = `/static/uploads/${entry.original_filename}`;
    const enhancedImageUrl = `/static/results/${entry.result_filename}`;
    
    console.log('Setting original image src to:', originalImageUrl);
    console.log('Setting enhanced image src to:', enhancedImageUrl);
    
    historyOriginalImage.src = originalImageUrl;
    historyEnhancedImage.src = enhancedImageUrl;
    
    // Add error handling for images
    historyOriginalImage.onerror = () => {
        console.error('Failed to load original image:', originalImageUrl);
        historyOriginalImage.src = '/static/images/placeholder.png';
        historyOriginalImage.alt = 'Original image not found';
    };
    
    historyEnhancedImage.onerror = () => {
        console.error('Failed to load enhanced image:', enhancedImageUrl);
        historyEnhancedImage.src = '/static/images/placeholder.png';
        historyEnhancedImage.alt = 'Enhanced image not found';
    };
    
    // Set download link
    historyDownloadBtn.href = enhancedImageUrl;
    historyDownloadBtn.download = `enhanced_${entry.original_filename}`;
    
    // Render parameters
    renderHistoryParameters(entry.params);
}

// Hide history detail
export function hideHistoryDetail() {
    const historyDetailEmpty = document.querySelector('.history-detail-empty');
    const historyDetailContent = document.querySelector('.history-detail-content');
    
    // Clear current history entry
    currentHistoryEntry = null;
    
    // Show empty state
    historyDetailEmpty.style.display = 'block';
    
    // Hide detail content
    historyDetailContent.style.display = 'none';
}

// Render history parameters
export function renderHistoryParameters(params) {
    const historyParametersList = document.getElementById('history-parameters-list');
    
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

// Reuse history parameters
export function reuseHistoryParameters(currentParams, updateParamsCallback) {
    if (!currentHistoryEntry) return;
    
    // Copy parameters from history entry
    const updatedParams = {...currentHistoryEntry.params};
    
    // Update UI to reflect parameters
    document.querySelectorAll('input[type="range"]').forEach(input => {
        const paramName = input.name;
        if (updatedParams.hasOwnProperty(paramName)) {
            input.value = updatedParams[paramName];
            const valueSpan = document.getElementById(`${input.id}-value`);
            if (valueSpan) {
                valueSpan.textContent = updatedParams[paramName];
            }
        }
    });
    
    document.querySelectorAll('input[type="checkbox"]').forEach(input => {
        const paramName = input.name;
        if (updatedParams.hasOwnProperty(paramName)) {
            input.checked = updatedParams[paramName];
        }
    });
    
    // Update active preset if present in parameters
    let activePreset = null;
    if (updatedParams.preset) {
        updateActivePreset(updatedParams.preset);
        activePreset = updatedParams.preset;
    } else {
        updateActivePreset(null);
    }
    
    // Call the callback to update parameters in parent component
    if (updateParamsCallback) {
        updateParamsCallback(updatedParams, activePreset);
    }
    
    // Switch to enhance tab
    document.querySelector('.main-tab[data-tab="enhance"]').click();
    
    // Apply to current image if one is loaded
    import('./imageHandling.js').then(module => {
        if (module.getCurrentImage()) {
            applyEnhancement(updatedParams);
        } else {
            showError('Parameters loaded from history. Upload an image to apply them.');
        }
    });
}

// Delete history entry
export function deleteHistoryEntry() {
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

// Clear all history
export function clearHistory() {
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

// Get current history entry
export function getCurrentHistoryEntry() {
    return currentHistoryEntry;
}
