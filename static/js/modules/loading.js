/**
 * Loading indicator and progress tracking functionality
 */

import { showError } from './utils.js';

let processingInterval = null;

// Show loading indicator
export function showLoadingIndicator() {
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
    const enhancedImage = document.getElementById('enhanced-image');
    if (enhancedImage) {
        enhancedImage.src = "/static/img/loading.png";
    }
}

// Hide loading indicator
export function hideLoadingIndicator() {
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

// Update progress bar and text
export function updateProgress(progress, text) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const loadingText = document.getElementById('loading-text');
    
    if (progressBar) progressBar.style.width = `${progress}%`;
    if (progressText) progressText.textContent = `${progress}%`;
    if (loadingText && text) loadingText.textContent = text;
}

// Show estimated processing time
export function showEstimatedTime(seconds) {
    const loadingText = document.getElementById('loading-text');
    if (loadingText) {
        const timeStr = seconds < 60 
            ? `${Math.round(seconds)} seconds` 
            : `${Math.floor(seconds / 60)} min ${Math.round(seconds % 60)} sec`;
        loadingText.textContent = `Estimated processing time: ${timeStr}`;
    }
}

// Start polling for task status
export function startProcessingPolling(taskId, estimatedTime, updateEnhancedImageCallback) {
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
                        updateEnhancedImageCallback(data.result);
                        document.getElementById('apply-btn').disabled = false;
                        hideLoadingIndicator();
                        
                        // Show success message
                        showError('Enhancement completed successfully');
                    } else if (data.status === 'failed') {
                        // Task failed
                        clearInterval(processingInterval);
                        processingInterval = null;
                        
                        showError('Error enhancing image: ' + data.error);
                        document.getElementById('apply-btn').disabled = false;
                        hideLoadingIndicator();
                    }
                    // Otherwise continue polling
                } else {
                    // Error getting task status
                    clearInterval(processingInterval);
                    processingInterval = null;
                    
                    showError('Error checking task status: ' + data.error);
                    document.getElementById('apply-btn').disabled = false;
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
                    document.getElementById('apply-btn').disabled = false;
                    hideLoadingIndicator();
                }
            });
    }, 1000); // Poll every second
}

// Get progress message based on data
export function getProgressMessage(data) {
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
