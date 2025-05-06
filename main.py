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
    
    # Setup directories
    if not setup_directories():
        logger.error("Failed to set up directories. Exiting.")
        sys.exit(1)
    
    # Start the server
    try:
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
