"""
CARA Application Launcher - Refactored with Application Factory Pattern

This file now uses the application factory pattern to create the Flask app.
Previously it imported 'app' directly from app.py. Now it calls create_app() 
from core.py to get a properly configured Flask application instance.

Key Changes:
- Import create_app from core.py instead of app from app.py
- Call create_app() to get the Flask application instance
- Maintain the same run configuration (host, port, debug)
- App must still run via 'python main.py' as required

The application factory pattern provides better:
- Modularity and separation of concerns
- Testability (can create app instances with different configs)
- Scalability (easier to add new blueprints and extensions)
"""

import os

from core import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG", "0") == "1")