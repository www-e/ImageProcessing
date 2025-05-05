# Adaptive Contrast Enhancement

A high-performance web application for enhancing image contrast using adaptive algorithms with an emphasis on speed, usability, and mobile responsiveness.

## Features

### Core Functionality
- Upload and process images with intelligent compression
- Apply adaptive contrast enhancement with real-time feedback
- Fine-tune enhancement parameters with intuitive controls
- View before/after comparison in real-time
- Save and download enhanced images
- Track processing history with parameter reuse

### Performance Optimizations
- Intelligent image compression to reduce processing time
- Asynchronous processing with background tasks
- Real-time progress tracking with estimated completion time
- Smart caching system to avoid redundant processing
- Memory management to prevent leaks during processing
- Adaptive algorithm selection based on image characteristics

### User Experience
- Modern, intuitive interface with responsive design
- Mobile-friendly layout that works on all device sizes
- Real-time loading indicators with progress tracking
- Preset system for quick enhancement application
- Detailed history tracking with parameter reuse
- Performance insights for problematic images
- **Modular Architecture**: Well-structured codebase with separate modules for different functionalities

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/imageprocessing.git
cd imageprocessing
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

### Development Mode

1. Run the application in development mode:
```
python main.py
```

2. The web interface will automatically open in your default browser at `http://localhost:5000`

3. Upload an image, adjust parameters, and apply the enhancement

4. Download the enhanced image

### Production Mode

For production deployment, use the included production server (Waitress):

```
python production.py
```

This will start a production-ready WSGI server. You can specify host and port:

```
python production.py --host 0.0.0.0 --port 8080
```

## Project Structure

```
imageprocessing/
├── filters/                  # Filter implementations
│   ├── adaptive_enhancement.py  # Core adaptive enhancement algorithm
│   ├── advanced_filters.py   # Advanced filter implementations
│   └── basic_filters.py      # Basic filter implementations
├── static/                   # Static web assets
│   ├── css/                  # CSS styles
│   ├── js/                   # JavaScript files
│   ├── img/                  # Static images
│   ├── uploads/              # User uploaded images
│   └── results/              # Enhanced images
├── templates/                # HTML templates
│   └── index.html            # Main page template
├── utils/                    # Utility functions
│   └── image_utils.py        # Image processing utilities
├── app.py                    # Flask application
├── main.py                   # Main entry point
└── requirements.txt          # Project dependencies
```

## Parameters Guide

### General Parameters

- **Window Size**: Size of the local window for calculating statistics (larger values = smoother results)
- **Use Entropy**: Whether to use local entropy for enhancement (helps preserve details in complex regions)

### Noise Reduction Parameters

- **Apply Noise Reduction**: Enable/disable noise reduction
- **Bilateral Strength**: Strength of the bilateral filter (higher = more smoothing)
- **Bilateral Diameter**: Diameter of each pixel neighborhood for bilateral filter
- **Denoise Blend Factor**: How much of the denoised image to blend with the original

### Contrast Enhancement Parameters

- **Gamma Min**: Minimum gamma value for adaptive gamma correction
- **Gamma Max**: Maximum gamma value for adaptive gamma correction
- **Contrast Strength**: Strength of local contrast enhancement
- **Entropy Factor**: How much local entropy influences enhancement

### Detail Enhancement Parameters

- **Enhance Details**: Enable/disable detail enhancement
- **Unsharp Kernel Size**: Size of the kernel for unsharp masking
- **Unsharp Sigma**: Standard deviation of the Gaussian kernel for unsharp masking
- **Unsharp Amount**: Strength of the sharpening effect

### Final Adjustment Parameters

- **Apply CLAHE**: Enable/disable Contrast Limited Adaptive Histogram Equalization
- **CLAHE Clip Limit**: Threshold for contrast limiting in CLAHE
- **CLAHE Blend**: How much of the CLAHE result to blend with the enhanced image
- **Apply High Boost**: Enable/disable high-boost filtering
- **High Boost Factor**: Factor to boost high frequencies
- **High Boost Blend**: How much of the high-boost result to blend with the enhanced image

## Presets

- **Dark Image**: Optimized for very dark images, increases brightness and contrast
- **Bright Image**: Optimized for very bright images, reduces highlights and improves details
- **Sharp Edges**: Enhances edges while preserving details
- **Blurry Image**: Increases sharpness and detail for blurry images
- **High Detail**: Optimized for images with strong visible detail
- **Low Contrast**: Enhances contrast in flat, low-contrast images

## Algorithm Details

### Adaptive Enhancement Process

1. **Local Statistics Calculation**:
   - Calculate local mean, standard deviation, and entropy for each pixel
   - These statistics guide the adaptive enhancement process

2. **Noise Reduction**:
   - Apply bilateral filtering with adaptive parameters
   - Smooth flat regions more aggressively while preserving edges

3. **Adaptive Enhancement**:
   - Apply adaptive gamma correction based on local brightness
   - Enhance contrast based on local standard deviation
   - Use entropy to further adjust enhancement in complex regions

4. **Detail Enhancement**:
   - Apply unsharp masking with adaptive amount
   - Enhance details more in high-contrast regions

5. **Final Adjustments**:
   - Apply CLAHE for additional contrast enhancement
   - Use high-boost filtering to enhance high-frequency details

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenCV for image processing functions
- Flask for the web framework
- Scikit-image for additional image processing algorithms
