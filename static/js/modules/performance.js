/**
 * Performance optimization functions
 */

import { showError } from './utils.js';

// Clear cache to improve performance
export function clearCache() {
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

// Analyze image for performance insights
export function analyzeImage(filename) {
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
