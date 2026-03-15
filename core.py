"""
CARA Application Factory Module

This module contains the application factory pattern implementation for the CARA Flask app.
The create_app() function initializes and configures the Flask application with all extensions,
blueprints, and configuration settings.

Key Components:
- Flask app creation and configuration
- Database initialization (SQLAlchemy)
- Template filters registration
- Error handlers registration
- Blueprint registration
- Scheduler initialization
- API key management setup

This refactor separates app creation logic from route definitions for better modularity.
"""

import os
import logging
import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging for the application factory
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database base class - shared across the application
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy without app context (will be initialized in create_app)
db = SQLAlchemy(model_class=Base)


def create_app(config_overrides=None):
    """
    Application factory function that creates and configures the Flask application.
    
    This function:
    1. Creates the Flask app instance
    2. Configures the app with environment variables and database settings
    3. Initializes all extensions (SQLAlchemy, etc.)
    4. Registers blueprints with routes
    5. Sets up template filters and error handlers
    6. Initializes background services (scheduler)
    
    Args:
        config_overrides (dict, optional): Configuration overrides for testing
        
    Returns:
        Flask: Configured Flask application instance
    """
    
    # Create Flask app instance
    app = Flask(__name__)
    
    # Add ProxyFix for proper HTTPS URL generation behind reverse proxies  
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Load environment variables if using python-dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded environment variables from .env file")
    except ImportError:
        logger.info("python-dotenv not installed, using system environment variables")
    
    # App configuration from environment variables with validation
    app.secret_key = os.environ.get("SESSION_SECRET")
    if not app.secret_key:
        logger.critical("SESSION_SECRET environment variable is required for secure operation")
        raise ValueError("SESSION_SECRET environment variable must be set")
    
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        logger.critical("DATABASE_URL environment variable is required")
        raise ValueError("DATABASE_URL environment variable must be set")
    
    # Configure Flask URL scheme - only set SERVER_NAME in development
    # In production (Render), ProxyFix handles URL generation correctly
    app.config["APPLICATION_ROOT"] = "/"
    if os.environ.get("FLASK_ENV") == "development" or os.environ.get("REPLIT_DEV_DOMAIN"):
        # Only set SERVER_NAME in development - it breaks production deployments
        app.config["SERVER_NAME"] = "localhost:5000"
        app.config["PREFERRED_URL_SCHEME"] = "http"
    else:
        # Production: Let ProxyFix handle scheme/host from headers
        app.config["PREFERRED_URL_SCHEME"] = "https"
    
    # Database configuration with connection pooling for production use
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,      # Recycle connections after 5 minutes
        "pool_pre_ping": True,    # Verify connections before using
        "pool_size": 10,          # Number of connections to maintain
        "max_overflow": 20,       # Additional connections allowed
        "pool_timeout": 30        # Timeout waiting for connection
    }
    
    # Apply any configuration overrides (useful for testing)
    if config_overrides:
        app.config.update(config_overrides)
    
    # Initialize database with app context
    db.init_app(app)
    
    # Import models to ensure all tables are created
    with app.app_context():
        import models  # Import all models for table creation
        db.create_all()  # Create all database tables
    
    # Register template filters (moved from app.py)
    register_template_filters(app)
    
    # Register error handlers (moved from app.py)
    register_error_handlers(app)
    
    # Register blueprints with routes (routes moved from app.py to blueprints)
    register_blueprints(app)
    
    # Initialize background services (scheduler, etc.)
    initialize_background_services(app)
    
    # Start export job worker in background - only in development or when explicitly enabled
    # In production with Gunicorn, multiple workers would start multiple schedulers causing conflicts
    # Use ENABLE_EXPORT_WORKER=true to enable in production if running single-worker mode
    enable_worker = (
        os.environ.get("ENABLE_EXPORT_WORKER", "").lower() == "true" or
        os.environ.get("REPLIT_DEV_DOMAIN") is not None or
        os.environ.get("FLASK_ENV") == "development"
    )
    
    if enable_worker:
        def start_export_worker_delayed():
            """Start export worker after a brief delay to avoid blocking app startup"""
            try:
                import time
                time.sleep(2)  # Brief delay to let app finish starting
                from utils.export_job_worker import ExportJobWorker
                with app.app_context():
                    worker = ExportJobWorker(app)
                    worker.start_worker()
                    logger.info("Export job worker started successfully")
            except Exception as e:
                logger.error(f"Failed to start export job worker: {e}")
                logger.exception("Export worker startup error details:")
        
        # Start worker in background thread to avoid blocking app startup
        import threading
        worker_thread = threading.Thread(target=start_export_worker_delayed, daemon=True)
        worker_thread.start()
        logger.info("Export job worker startup initiated")
    else:
        logger.info("Export job worker disabled (set ENABLE_EXPORT_WORKER=true to enable)")
    
    logger.info("Flask application created and configured successfully")
    return app


def register_template_filters(app):
    """
    Register custom Jinja2 template filters.
    
    These filters were previously defined directly on the app object in app.py.
    Now they're organized in a dedicated function for better maintainability.
    """
    
    @app.template_filter('format_risk_type')
    def format_risk_type(value):
        """
        Transform risk types with underscores to properly formatted strings.
        Example: winter_storm -> Winter Storm
        """
        if value and isinstance(value, str):
            # Replace underscores with spaces and apply title case
            return value.replace('_', ' ').title()
        return value
    
    @app.template_filter('format_datetime')
    def format_datetime(value):
        """
        Format datetime objects for display in templates.
        """
        if value:
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return ''
    
    logger.info("Registered custom template filters")


def register_error_handlers(app):
    """
    Register comprehensive production error handlers for the application.
    
    Includes detailed logging, JSON API responses, and user-friendly error pages.
    """
    from utils.error_handlers import (
        register_comprehensive_error_handlers, 
        setup_api_error_handlers
    )
    
    # Register the comprehensive error handling system
    register_comprehensive_error_handlers(app)
    
    # Setup API-specific error handlers
    setup_api_error_handlers(app)
    
    logger.info("Registered comprehensive error handlers")


def register_blueprints(app):
    """
    Register all application blueprints.
    
    This function imports and registers all blueprints that contain the application routes.
    Routes are now organized in blueprints instead of being defined directly on the app object.
    """
    # Import all blueprints from the routes package
    from routes.public import public_bp
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp
    from routes.herc import herc_bp
    from routes.gis_export import gis_export_bp
    
    # Register all blueprints with the app
    app.register_blueprint(public_bp)      # Routes: /, /methodology, /docs/*
    app.register_blueprint(dashboard_bp)   # Routes: /dashboard/*, /print-summary/*, etc.
    app.register_blueprint(api_bp)         # Routes: /api/*
    app.register_blueprint(herc_bp)        # Routes: /herc-dashboard/*, /herc-kp-hva-export/*
    app.register_blueprint(gis_export_bp)  # Routes: /api/gis/*, GIS export functionality
    
    # Setup monitoring and health check endpoints
    from utils.api_monitoring import setup_monitoring_endpoints, track_request_metrics
    setup_monitoring_endpoints(app)
    track_request_metrics(app)
    
    logger.info("Registered application blueprints")


def initialize_background_services(app):
    """
    Initialize background services and production logging.
    
    Sets up:
    - Data refresh scheduler
    - Production logging system
    - External monitoring (Sentry)
    - Performance monitoring
    - Security features (rate limiting, API authentication)
    """
    from utils.logging_config import (
        setup_production_logging, 
        setup_sentry_integration, 
        log_performance_metrics
    )
    from utils.security_manager import setup_security
    
    # Setup comprehensive production logging (non-blocking)
    try:
        logger.debug("Setting up production logging...")
        setup_production_logging(app)
        logger.debug("✓ Production logging setup complete")
    except Exception as e:
        logger.error(f"Failed to setup production logging: {e}")
    
    # Setup external monitoring (Sentry) if configured (non-blocking)
    try:
        logger.debug("Setting up Sentry integration...")
        setup_sentry_integration(app)
        logger.debug("✓ Sentry integration setup complete")
    except Exception as e:
        logger.error(f"Failed to setup Sentry integration: {e}")
    
    # Setup performance monitoring (non-blocking)
    try:
        logger.debug("Setting up performance monitoring...")
        log_performance_metrics(app)
        logger.debug("✓ Performance monitoring setup complete")
    except Exception as e:
        logger.error(f"Failed to setup performance monitoring: {e}")
    
    # Setup security features (rate limiting, API auth, headers) (non-blocking)
    try:
        logger.debug("Setting up security features...")
        setup_security(app)
        logger.debug("✓ Security features setup complete")
    except Exception as e:
        logger.error(f"Failed to setup security features: {e}")
    
    logger.info("Background services initialization complete")
    
    def init_scheduler(app):
        """Initialize the data refresh scheduler in the background"""
        with app.app_context():
            try:
                from utils.scheduler_init import start_scheduler_with_delay
                # Start the scheduler with a 10-second delay to allow the app to fully initialize
                start_scheduler_with_delay(delay_seconds=10)
                logger.info("Scheduled data refresh initialization with 10-second delay")
            except Exception as e:
                logger.error(f"Failed to initialize data refresh scheduler: {str(e)}")
    
    # Start scheduler in a separate thread to avoid blocking app startup
    scheduler_thread = threading.Thread(target=init_scheduler, args=(app,), daemon=True)
    scheduler_thread.start()
    
    
    logger.info("Initialized background services")


# Export the db instance so it can be imported by models and other modules
__all__ = ['create_app', 'db']