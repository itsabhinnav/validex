#!/usr/bin/env python3
"""
Validex Test Case Management System - Main Entry Point
Consolidated Flask application serving both API and Angular frontend
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_app():
    """Create Flask app that serves both API and Angular frontend"""
    app = Flask(__name__)
    
    # Configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
        app.config['DEBUG'] = False
        debug_mode = False
    else:
        app.config['SECRET_KEY'] = 'dev-secret-key'
        app.config['DEBUG'] = True
        debug_mode = True
    
    # Enable CORS for development
    CORS(app, origins=[
        'http://localhost:4200',  # Angular dev server
        'http://127.0.0.1:4200',  # Angular dev server alternative
        'http://localhost:4201',  # Angular dev server alternative port
        'http://127.0.0.1:4201',  # Angular dev server alternative port
        'http://localhost:8000',  # Flask server
        'http://127.0.0.1:8000'   # Flask server alternative
    ])
    
    # Get paths
    frontend_dist = project_root.parent / 'frontend' / 'testpoc-frontend' / 'dist' / 'testpoc-frontend'
    
    # Import and register API blueprints - High-Performance as Default
    try:
        from app.controllers.high_performance_test_cases_controller import high_performance_test_cases_controller
        app.register_blueprint(high_performance_test_cases_controller.blueprint, url_prefix='/api')
        print("[OK] High-Performance API routes loaded as default")
    except ImportError as e:
        print(f"Warning: Could not import high-performance routes: {e}")
    
    # Legacy API routes (kept for backward compatibility)
    try:
        from app.api.main_routes import main_bp
        app.register_blueprint(main_bp, url_prefix='/api/legacy')
        print("[OK] Legacy API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import main_routes: {e}")
    
    try:
        from app.api.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("[OK] Auth API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import auth: {e}")
    
    try:
        from app.api.routes import main_bp as routes_bp
        app.register_blueprint(routes_bp, name='routes', url_prefix='/api/legacy')
        print("[OK] Additional legacy API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import routes: {e}")
    
    try:
        from app.api.requirements_routes import requirements_bp
        app.register_blueprint(requirements_bp, url_prefix='/api/legacy')
        print("[OK] Legacy requirements API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import requirements_routes: {e}")
    
    try:
        from app.api.sync_routes import sync_bp
        app.register_blueprint(sync_bp, url_prefix='/api/legacy')
        print("[OK] Legacy sync API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import sync_routes: {e}")
    
    try:
        from app.api.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        print("[OK] Admin API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import admin: {e}")
    
    # API Health Check
    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy', 
            'message': 'Validex High-Performance API is running',
            'frontend': 'Angular',
            'backend': 'Flask',
            'mode': 'high-performance',
            'environment': config_name,
            'features': [
                'sub-second search',
                'advanced filtering',
                'bulk operations',
                'performance monitoring',
                'database optimization'
            ]
        })
    
    # Serve Angular Frontend
    @app.route('/')
    def serve_angular():
        """Serve Angular frontend"""
        if frontend_dist.exists():
            return send_from_directory(str(frontend_dist), 'index.html')
        else:
            return jsonify({
                'error': 'Angular frontend not found',
                'message': 'Please run: ng build in frontend directory',
                'frontend_path': str(frontend_dist),
                'instructions': 'cd frontend/testpoc-frontend && ng build'
            }), 404
    
    @app.route('/<path:path>')
    def serve_angular_assets(path):
        """Serve Angular static assets"""
        if frontend_dist.exists():
            # Check if it's an API route
            if path.startswith('api/'):
                return jsonify({'error': 'API route not found'}), 404
            
            # Check if file exists
            file_path = frontend_dist / path
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(frontend_dist), path)
            else:
                # For Angular routing, serve index.html
                return send_from_directory(str(frontend_dist), 'index.html')
        else:
            return jsonify({'error': 'Frontend not found'}), 404
    
    # Context processors for template support (if needed)
    @app.context_processor
    def inject_config():
        try:
            from config.settings import config
            return {
                'admin_enabled': config.is_admin_enabled(),
                'auto_launch_browser': config.is_auto_launch_browser_enabled(),
                'startup_delay': config.get_startup_delay()
            }
        except ImportError:
            return {
                'admin_enabled': True,
                'auto_launch_browser': False,
                'startup_delay': 2
            }
    
    return app

def launch_browser(url, delay=2):
    """Launch browser after a delay"""
    def _launch():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"Browser launched: {url}")
        except Exception as e:
            print(f"Failed to launch browser: {e}")
    
    thread = threading.Thread(target=_launch, daemon=True)
    thread.start()

def main():
    """Main application entry point"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = create_app()
    
    # Server configuration
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', str(config_name == 'development')).lower() == 'true'
    
    if config_name == 'production':
        host = '0.0.0.0'
        debug = False
    
    url = f"http://{host}:{port}"
    
    print("=" * 60)
    print("Validex Test Case Management System")
    print("=" * 60)
    print(f"Environment: {config_name}")
    print(f"Server: {url}")
    print(f"Debug: {debug}")
    print(f"Working Directory: {project_root}")
    print(f"Frontend: Angular (served from Flask)")
    print(f"API Endpoints: {url}/api/*")
    print("=" * 60)
    
    # Auto-launch browser if enabled
    try:
        from config.settings import config
        if config.is_auto_launch_browser_enabled():
            startup_delay = config.get_startup_delay()
            print(f"Auto-launching browser in {startup_delay} seconds...")
            launch_browser(url, startup_delay)
        else:
            print("Auto-launch browser is disabled")
    except ImportError:
        print("Config not available, skipping auto-launch")
    
    print("Server starting...")
    print("=" * 60)
    
    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == '__main__':
    main()