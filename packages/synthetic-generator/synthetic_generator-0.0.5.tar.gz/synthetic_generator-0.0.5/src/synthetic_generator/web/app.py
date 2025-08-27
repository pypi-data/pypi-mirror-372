"""
Flask application for Synthetic Generator Web UI.
"""

import os
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import json
from datetime import datetime
# Import these functions directly to avoid circular imports
from ..schemas import DataSchema, ColumnSchema, DataType, DistributionType
from .. import __version__ as PACKAGE_VERSION
from .api import api_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Enable CORS
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Routes
    @app.route('/')
    def index():
        """Main dashboard page."""
        return render_template('index.html', package_version=PACKAGE_VERSION)
    
    @app.route('/generator')
    def generator():
        """Data generator page."""
        return render_template('generator.html', package_version=PACKAGE_VERSION)
    
    @app.route('/templates')
    def templates():
        """Templates page."""
        return render_template('templates.html', package_version=PACKAGE_VERSION)
    
    @app.route('/inference')
    def inference():
        """Schema inference page."""
        return render_template('inference.html', package_version=PACKAGE_VERSION)
    
    @app.route('/validation')
    def validation():
        """Data validation page."""
        return render_template('validation.html', package_version=PACKAGE_VERSION)
    
    # Removed export page; exporting is handled within the generator page
    
    @app.route('/about')
    def about():
        """About page."""
        return render_template('about.html', package_version=PACKAGE_VERSION)
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html', package_version=PACKAGE_VERSION), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html', package_version=PACKAGE_VERSION), 500
    
    return app


def run_app(host='0.0.0.0', port=5000, debug=True):
    """Run the Flask application."""
    app = create_app()
    print(f"🚀 Starting Synthetic Generator Web UI...")
    print(f"📊 Dashboard: http://{host}:{port}")
    print(f"🔧 API: http://{host}:{port}/api")
    print(f"📚 Documentation: http://{host}:{port}/about")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_app()
