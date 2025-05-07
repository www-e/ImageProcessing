# Image Processing Filters Documentation

This document provides a comprehensive overview of the image processing filters implemented in the Image Processing application. It describes each filter's purpose, parameters, and typical use cases.

## Table of Contents

1. [Enhancement Filters](#enhancement-filters)
   - [Adaptive Contrast Enhancement](#adaptive-contrast-enhancement)
   - [Brightness and Contrast](#brightness-and-contrast)
   - [Exposure](#exposure)
   - [Vibrance and Saturation](#vibrance-and-saturation)
   - [Clarity](#clarity)
   - [Shadows and Highlights](#shadows-and-highlights)

2. [Morphological Filters](#morphological-filters)
   - [Dilation](#dilation)
   - [Erosion](#erosion)
   - [Opening](#opening)
   - [Closing](#closing)
   - [Top Hat](#top-hat)
   - [Black Hat](#black-hat)
   - [Morphological Gradient](#morphological-gradient)
   - [Hit-Miss Transform](#hit-miss-transform)
   - [Thinning](#thinning)
   - [Thickening](#thickening)
   - [Skeletonization](#skeletonization)

3. [Performance Optimizations](#performance-optimizations)
   - [Dual Processing Paths](#dual-processing-paths)
   - [CLAHE Fast Path](#clahe-fast-path)
   - [Reduced Precision Processing](#reduced-precision-processing)
   - [Image Caching](#image-caching)
   - [Adaptive Window Sizing](#adaptive-window-sizing)

---

## Enhancement Filters

### Adaptive Contrast Enhancement

The core enhancement algorithm of the application, which adaptively enhances local contrast based on the image content.

**Parameters:**
- `window_size` (3-31, default: 15): Size of the local window for adaptive processing. Larger values preserve more global contrast but process slower.
- `clip_limit` (0.5-5.0, default: 3.0): Limits the contrast enhancement to prevent noise amplification. Higher values allow more enhancement.
- `disable_entropy` (boolean, default: false): When true, skips entropy calculation for faster processing.

**Use Cases:**
- Enhancing details in poorly lit or foggy images
- Improving visibility in medical imaging
- Recovering details in underexposed or overexposed photographs

### Brightness and Contrast

Basic adjustments to the overall brightness and contrast of an image.

**Parameters:**
- `brightness` (-100 to 100, default: 0): Adjusts the overall brightness of the image. Positive values make the image brighter.
- `contrast` (0.5 to 3.0, default: 1.0): Adjusts the overall contrast of the image. Values above 1.0 increase contrast.

**Use Cases:**
- Basic image correction
- Preparing images for further processing
- Quick adjustments to improve visibility

### Exposure

Controls the exposure, highlights, and shadows of an image.

**Parameters:**
- `exposure` (-100 to 100, default: 0): Adjusts the overall exposure. Positive values simulate longer exposure times.
- `highlights` (-100 to 100, default: 0): Controls the brightness of highlight areas. Negative values recover detail in bright areas.
- `shadows` (-100 to 100, default: 0): Controls the brightness of shadow areas. Positive values recover detail in dark areas.

**Use Cases:**
- Recovering details in high dynamic range scenes
- Fixing improperly exposed photographs
- Balancing light in images with mixed lighting conditions

### Vibrance and Saturation

Adjusts the color intensity of an image.

**Parameters:**
- `vibrance` (-100 to 100, default: 0): Intelligently increases saturation of less-saturated colors while protecting skin tones.
- `saturation` (-100 to 100, default: 0): Uniformly adjusts the saturation of all colors in the image.

**Use Cases:**
- Enhancing color in nature photography
- Making product images more appealing
- Correcting faded or desaturated images

### Clarity

Enhances medium contrast and edge definition to make images appear sharper and more defined.

**Parameters:**
- `clarity` (0 to 100, default: 0): Controls the strength of the medium contrast enhancement.
- `edge_kernel` (3 to 7, default: 3): Size of the kernel used for edge detection. Larger values detect broader edges.
- `edge_scale` (0.5 to 2.0, default: 1.0): Scales the strength of edge enhancement.
- `apply_clahe` (boolean, default: true): When true, applies CLAHE (Contrast Limited Adaptive Histogram Equalization) for additional local contrast.
- `clahe_clip` (0.5 to 5.0, default: 2.0): Clip limit for CLAHE algorithm.
- `clahe_grid` (2 to 16, default: 8): Grid size for CLAHE algorithm.

**Use Cases:**
- Enhancing architectural details
- Improving texture visibility in product photography
- Making landscapes appear more detailed and crisp

### Shadows and Highlights

Advanced control over shadow and highlight areas with mid-tone contrast adjustment.

**Parameters:**
- `shadows_recovery` (0 to 100, default: 0): Recovers detail in shadow areas without affecting highlights.
- `highlights_recovery` (0 to 100, default: 0): Recovers detail in highlight areas without affecting shadows.
- `mid_tone_contrast` (-100 to 100, default: 0): Adjusts contrast in the mid-tones while preserving shadows and highlights.

**Use Cases:**
- Recovering details in high-contrast scenes
- Balancing indoor/outdoor lighting in architectural photography
- Enhancing details in both dark and bright areas of an image

---

## Morphological Filters

### Dilation

Expands bright regions in an image, useful for filling in small holes and connecting broken parts.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element. Larger values create more expansion.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation. More iterations create stronger effects.

**Use Cases:**
- Filling small holes in objects
- Connecting broken text or lines
- Expanding features for better visibility

### Erosion

Shrinks bright regions in an image, useful for removing small noise and separating connected objects.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element. Larger values create more shrinking.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation. More iterations create stronger effects.

**Use Cases:**
- Removing small noise particles
- Separating touching objects
- Reducing the size of features

### Opening

Erosion followed by dilation, useful for removing small bright spots while preserving the overall shape of larger objects.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation.

**Use Cases:**
- Removing small bright noise
- Smoothing object contours
- Breaking narrow connections between objects

### Closing

Dilation followed by erosion, useful for filling small holes and gaps while preserving the overall shape.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation.

**Use Cases:**
- Filling small holes in objects
- Closing small gaps in contours
- Connecting nearby objects

### Top Hat

Extracts small bright details from an image by subtracting the opened image from the original.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation.

**Use Cases:**
- Extracting small bright details
- Enhancing text against varying backgrounds
- Finding bright spots in medical images

### Black Hat

Extracts small dark details from an image by subtracting the original image from the closed image.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation.

**Use Cases:**
- Extracting small dark details
- Finding dark spots or defects
- Enhancing dark text on varying backgrounds

### Morphological Gradient

Extracts the outline of objects by subtracting the eroded image from the dilated image.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element.
- `iterations` (1 to 10, default: 1): Number of times to apply the operation.

**Use Cases:**
- Edge detection
- Finding object boundaries
- Creating outline effects

### Hit-Miss Transform

Detects specific shapes or patterns in binary images.

**Parameters:**
- `kernel_size` (3 to 21, default: 5): Size of the structuring element.
- `pattern` (string, default: "cross"): Pattern to detect (cross, square, horizontal, vertical).
- `threshold` (0 to 255, default: 128): Threshold for converting to binary image.

**Use Cases:**
- Pattern matching
- Detecting specific shapes
- Finding corners or junctions

### Thinning

Reduces objects to their skeleton while preserving their topology.

**Parameters:**
- `max_iterations` (1 to 100, default: 10): Maximum number of iterations for the thinning process.
- `threshold` (0 to 255, default: 128): Threshold for converting to binary image.
- `preserve_original` (boolean, default: false): When true, overlays the result on the original image.

**Use Cases:**
- Character recognition
- Fingerprint analysis
- Simplifying complex shapes

### Thickening

Expands the skeleton of objects while preserving their topology.

**Parameters:**
- `max_iterations` (1 to 100, default: 10): Maximum number of iterations for the thickening process.
- `threshold` (0 to 255, default: 128): Threshold for converting to binary image.
- `preserve_original` (boolean, default: false): When true, overlays the result on the original image.

**Use Cases:**
- Enhancing thin lines
- Making text more readable
- Emphasizing skeletal structures

### Skeletonization

Reduces objects to their central line or skeleton.

**Parameters:**
- `threshold` (0 to 255, default: 128): Threshold for converting to binary image.
- `preserve_original` (boolean, default: false): When true, overlays the result on the original image.

**Use Cases:**
- Shape analysis
- Path planning in robotics
- Simplifying complex structures for analysis

---

## Performance Optimizations

### Dual Processing Paths

The application implements both high-quality and high-speed processing paths:

- **High-Quality Path**: Uses full-resolution processing with entropy-based enhancement for maximum quality.
- **High-Speed Path**: Uses optimized algorithms with simplified calculations for faster processing.

The path is selected automatically based on image size and user preferences.

### CLAHE Fast Path

For large images or when speed is prioritized, the application uses Contrast Limited Adaptive Histogram Equalization (CLAHE) as a faster alternative to the full entropy-based enhancement.

**Benefits:**
- Up to 10x faster processing for large images
- Maintains good quality enhancement
- Reduces memory usage

### Reduced Precision Processing

For entropy calculations, the application can use 16-bin histograms instead of 256-bin histograms to significantly speed up processing.

**Benefits:**
- Up to 4x faster entropy calculations
- Minimal visual quality difference
- Enables processing of larger images

### Image Caching

The application implements a sophisticated image caching system:

- Frequently accessed images are stored in memory
- Processed results are cached to avoid redundant calculations
- Cache is automatically managed to prevent excessive memory usage

### Adaptive Window Sizing

Window sizes for local processing are automatically adjusted based on image size:

- Larger images use smaller windows to maintain reasonable processing times
- Smaller images use larger windows for better quality
- The algorithm balances quality and performance based on image content

---

This documentation provides an overview of the filters and optimizations implemented in the Image Processing application. For more detailed information, refer to the source code and technical documentation.
