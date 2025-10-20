from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
from pathlib import Path

def create_production_app():
    """Create production Flask app serving Angular on single port"""
    app = Flask(__name__)
    
    # Production configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['DEBUG'] = False
    
    # Get paths
    project_root = Path(__file__).parent.parent
    frontend_dist = project_root / 'frontend' / 'testpoc-frontend' / 'dist' / 'testpoc-frontend'
    
    # Import existing routes
    from app.api.main_routes import main_bp
    from app.api.auth import auth_bp
    from app.api.routes import routes_bp
    from app.api.requirements_routes import requirements_bp
    from app.api.sync_routes import sync_bp
    from app.api.admin import admin_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)
    app.register_blueprint(requirements_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(admin_bp)
    
    # Serve Angular Frontend
    @app.route('/')
    def serve_angular():
        """Serve Angular frontend"""
        if frontend_dist.exists():
            return send_from_directory(str(frontend_dist), 'index.html')
        else:
            return jsonify({
                'error': 'Frontend not built',
                'message': 'Run: cd frontend/testpoc-frontend && ng build --configuration production'
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
    
    # Context processors
    @app.context_processor
    def inject_admin_config():
        from config.settings import config
        return {
            'admin_enabled': config.is_admin_enabled(),
            'auto_launch_browser': config.is_auto_launch_browser_enabled(),
            'startup_delay': config.get_startup_delay()
        }
    
    return app

if __name__ == '__main__':
    app = create_production_app()
    print("🚀 Starting Production Flask + Angular Server")
    print("🌐 Single Port: http://localhost:8000")
    print("📡 API: http://localhost:8000/api/*")
    print("🎯 Frontend: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000)
