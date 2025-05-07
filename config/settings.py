"""
Configuration settings for the Image Processing application
"""
import os

# Configure upload and result folders
UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')
PLACEHOLDER_FOLDER = os.path.join('static', 'img')
HISTORY_FOLDER = os.path.join('static', 'history')
COMPRESSED_FOLDER = os.path.join('static', 'compressed')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(PLACEHOLDER_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Configure allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'}

# Server settings
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Maximum number of files to keep in each folder
MAX_UPLOAD_FILES = 50
MAX_RESULT_FILES = 100
MAX_COMPRESSED_FILES = 50

# Performance settings
DEFAULT_MAX_PROCESSING_DIMENSION = 800
ENABLE_PERFORMANCE_OPTIMIZATIONS = True
