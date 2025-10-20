from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from pathlib import Path

def create_app():
    """Create Flask app that serves Angular frontend and API endpoints only"""
    app = Flask(__name__)
    
    # Enable CORS for all origins in development
    # Enable CORS for development
    CORS(app, origins=[
        'http://localhost:4200',  # Angular dev server
        'http://127.0.0.1:4200',  # Angular dev server alternative
        'http://localhost:8000',  # Flask server
        'http://127.0.0.1:8000'   # Flask server alternative
    ])
    
    # Get paths
    project_root = Path(__file__).parent.parent
    frontend_dist = project_root / 'frontend' / 'testpoc-frontend' / 'dist' / 'validex-frontend'
    
    # Import API routes only (no template routes)
    try:
        from app.api.main_routes import main_bp
        app.register_blueprint(main_bp)
        print("✓ Main API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import main_routes: {e}")
    
    try:
        from app.api.auth import auth_bp
        app.register_blueprint(auth_bp)
        print("✓ Auth API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import auth: {e}")
    
    try:
        from app.api.routes import main_bp as routes_bp
        app.register_blueprint(routes_bp, name='routes')
        print("✓ Additional API routes loaded")
    except ImportError as e:
        print(f"Warning: Could not import routes: {e}")
    
    # API Health Check
    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy', 
            'message': 'Validex API is running',
            'frontend': 'Angular',
            'backend': 'Flask',
            'mode': 'API-only'
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
                'frontend_path': str(frontend_dist)
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("Starting Validex Server - API Only Mode")
    print("API Endpoints: http://localhost:8000/api/*")
    print("Frontend: http://localhost:8000")
    print("All UI logic migrated to Angular frontend")
    app.run(debug=True, host='0.0.0.0', port=8000)