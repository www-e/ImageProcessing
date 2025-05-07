#!/usr/bin/env python
"""
Adaptive Contrast Enhancement Application

This is the main entry point for the application.
It handles initialization, directory setup, and server startup.
"""

import os
import sys
import argparse
import logging
import webbrowser
import shutil
from threading import Timer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('adaptive_enhancement')

# Application directories
APP_DIRS = {
    'uploads': os.path.join('static', 'uploads'),
    'results': os.path.join('static', 'results'),
    'images': os.path.join('static', 'img'),
    'history': os.path.join('static', 'history'),
    'compressed': os.path.join('static', 'compressed')
}

def cleanup_pycache():
    """
    Clean up all __pycache__ directories and .pyc files in the project for a clean run.
    """
    try:
        # Track statistics
        pycache_count = 0
        pyc_count = 0
        
        # Walk through all directories in the project
        for root, dirs, files in os.walk('.'):
            # Remove __pycache__ directories
            if '__pycache__' in dirs:
                pycache_dir = os.path.join(root, '__pycache__')
                shutil.rmtree(pycache_dir)
                logger.info(f"Removed __pycache__ directory: {pycache_dir}")
                pycache_count += 1
            
            # Remove .pyc files
            for file in files:
                if file.endswith('.pyc'):
                    pyc_file = os.path.join(root, file)
                    os.remove(pyc_file)
                    logger.info(f"Removed .pyc file: {pyc_file}")
                    pyc_count += 1
        
        # Check specific directories that might be missed
        specific_dirs = [
            'routes', 'services', 'models', 'utils', 'config', 'filters',
            os.path.join('routes', '__pycache__'),
            os.path.join('services', '__pycache__'),
            os.path.join('models', '__pycache__'),
            os.path.join('utils', '__pycache__'),
            os.path.join('config', '__pycache__'),
            os.path.join('filters', '__pycache__')
        ]
        
        for dir_path in specific_dirs:
            if dir_path.endswith('__pycache__') and os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                logger.info(f"Removed specific __pycache__ directory: {dir_path}")
                pycache_count += 1
        
        logger.info(f"Cleaned up {pycache_count} __pycache__ directories and {pyc_count} .pyc files")
        return True
    except Exception as e:
        logger.error(f"Error cleaning up __pycache__ directories: {str(e)}")
        return False

def setup_directories():
    """
    Create all required directories for the application.
    
    Returns:
        bool: True if all directories were created successfully
    """
    try:
        for dir_name, dir_path in APP_DIRS.items():
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Directory '{dir_name}' setup complete at {dir_path}")
        return True
    except Exception as e:
        logger.error(f"Error setting up directories: {str(e)}")
        return False

def open_browser(url):
    """
    Open the browser to the specified URL after a delay.
    
    Args:
        url (str): The URL to open in the browser
    """
    try:
        webbrowser.open(url)
        logger.info(f"Browser opened at {url}")
    except Exception as e:
        logger.error(f"Error opening browser: {str(e)}")

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Adaptive Contrast Enhancement Application')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    return parser.parse_args()

def start_server(host, port, debug, open_browser_flag):
    """
    Start the Flask server.
    
    Args:
        host (str): Host to run the server on
        port (int): Port to run the server on
        debug (bool): Whether to run in debug mode
        open_browser_flag (bool): Whether to open the browser automatically
    """
    from app import app
    
    # Construct the URL
    protocol = 'http'
    if host == '0.0.0.0':
        url = f"{protocol}://localhost:{port}"
    else:
        url = f"{protocol}://{host}:{port}"
    
    # Open browser after a short delay if requested
    if open_browser_flag:
        Timer(1.5, open_browser, args=[url]).start()
        logger.info(f"Browser will open at {url} after server starts")
    
    # Start the Flask app
    logger.info(f"Starting server at {url}")
    app.run(debug=debug, host=host, port=port)

def main():
    """
    Main entry point for the application.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Clean up __pycache__ directories for a clean run
    cleanup_pycache()
    
    # Setup directories
    if not setup_directories():
        logger.error("Failed to set up directories. Exiting.")
        sys.exit(1)
    
    # Start the server
    try:
        # Make sure filters modules are properly imported
        try:
            # Verify imports work correctly
            from filters import enhancement, morphological
            logger.info("Filter modules successfully imported")
        except ImportError as e:
            logger.error(f"Error importing filter modules: {str(e)}")
            logger.info("Please make sure filters/enhancement.py and filters/morphological.py exist")
            sys.exit(1)
            
        start_server(
            host=args.host,
            port=args.port,
            debug=args.debug,
            open_browser_flag=not args.no_browser
        )
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
