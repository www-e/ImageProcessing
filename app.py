"""
Image Processing Application
A Flask web application for image enhancement and processing
"""
import os
import gc
from flask import Flask

# Import configuration
from config.settings import (
    DEBUG, HOST, PORT, 
    UPLOAD_FOLDER, RESULT_FOLDER, PLACEHOLDER_FOLDER, 
    HISTORY_FOLDER, COMPRESSED_FOLDER
)

# Import route blueprints
from routes.main_routes import main_bp
from routes.image_routes import image_bp
from routes.history_routes import history_bp

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(PLACEHOLDER_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

# Register blueprints with url_prefix=None to ensure routes are at the root level
app.register_blueprint(main_bp, url_prefix='')
app.register_blueprint(image_bp, url_prefix='')
app.register_blueprint(history_bp, url_prefix='')

# Import services to ensure they're initialized
from services.task_processor import process_image_task, process_morphological_task, process_enhancement_task
from services.image_processor import clear_image_cache
from services.image_optimization import normalize_image, calculate_local_statistics

# Initialize optimization services
import services.image_optimization

if __name__ == '__main__':
    # Force garbage collection before starting
    gc.collect()
    
    # Start the Flask app
    app.run(debug=DEBUG, host=HOST, port=PORT)
