"""
RBAC Access Control Service
Main application entry point
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from src.config import Config
from src.database.connection import DatabaseConnection
from src.routes import register_routes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize database connection
    db_connection = DatabaseConnection()
    db_connection.initialize()
    
    # Store database connection in app context
    app.db_connection = db_connection
    
    # Register all routes
    register_routes(app)
    
    logger.info("RBAC Service initialized successfully")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Run the application
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"Starting RBAC Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

