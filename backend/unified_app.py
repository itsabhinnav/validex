from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
import os
from pathlib import Path

def create_unified_app():
    """Create Flask app that serves both API and Angular frontend on single port"""
    app = Flask(__name__)
    
    # Enable CORS for development
    CORS(app, origins=['http://localhost:4200', 'http://127.0.0.1:4200'])
    
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
    
    # API Routes (for Angular frontend)
    @app.route('/api/health')
    def api_health():
        return jsonify({'status': 'healthy', 'message': 'API is running'})
    
    @app.route('/api/test-cases')
    def api_test_cases():
        """API endpoint for Angular frontend"""
        from app.controllers.test_cases_controller import TestCasesController
        controller = TestCasesController()
        
        # Get parameters
        app_filter = request.args.get('app', '')
        test_type_filter = request.args.getlist('test_type')
        priority_filter = request.args.getlist('priority')
        feature_filter = request.args.getlist('feature')
        screen_id_filter = request.args.getlist('screen_id')
        test_suite_type_filter = request.args.getlist('test_suite_type')
        requirement_type_filter = request.args.getlist('requirement_type')
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort', 'Test Case ID')
        sort_order = request.args.get('order', 'asc')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Load and filter data
        test_cases_data = controller.load_test_files()
        filtered_cases = controller._filter_test_cases(
            test_cases_data, app_filter, test_type_filter, 
            priority_filter, feature_filter, screen_id_filter, 
            test_suite_type_filter, requirement_type_filter, 
            search_query, {}, []
        )
        filtered_cases = controller._sort_test_cases(filtered_cases, sort_by, sort_order)
        
        # Pagination
        total_cases = len(filtered_cases)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_cases = filtered_cases[start_idx:end_idx]
        
        # Get filter options
        enhanced_data = controller.get_enhanced_filter_data(test_cases_data)
        filter_options = enhanced_data['filter_options']
        
        return jsonify({
            'test_cases': paginated_cases,
            'filter_options': {
                'apps': sorted(filter_options.get('App', [])),
                'test_types': sorted(filter_options.get('Test Type', [])),
                'priorities': sorted(filter_options.get('Priority', [])),
                'features': sorted(filter_options.get('Feature', [])),
                'screen_ids': sorted(filter_options.get('Screen ID', [])),
                'test_suite_types': sorted(filter_options.get('TestSuite Type', [])),
                'requirement_types': sorted(filter_options.get('Requirement Type', [])),
                'regions': sorted(filter_options.get('Region', [])),
                'brands': sorted(filter_options.get('Brand', []))
            },
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_cases': total_cases,
                'total_pages': (total_cases + per_page - 1) // per_page,
                'has_prev': page > 1,
                'has_next': page < (total_cases + per_page - 1) // per_page
            }
        })
    
    @app.route('/api/filter-options')
    def api_filter_options():
        """Get available filter options"""
        from app.controllers.test_cases_controller import TestCasesController
        controller = TestCasesController()
        test_cases_data = controller.load_test_files()
        enhanced_data = controller.get_enhanced_filter_data(test_cases_data)
        filter_options = enhanced_data['filter_options']
        
        return jsonify({
            'apps': sorted(filter_options.get('App', [])),
            'test_types': sorted(filter_options.get('Test Type', [])),
            'priorities': sorted(filter_options.get('Priority', [])),
            'features': sorted(filter_options.get('Feature', [])),
            'screen_ids': sorted(filter_options.get('Screen ID', [])),
            'test_suite_types': sorted(filter_options.get('TestSuite Type', [])),
            'requirement_types': sorted(filter_options.get('Requirement Type', [])),
            'regions': sorted(filter_options.get('Region', [])),
            'brands': sorted(filter_options.get('Brand', []))
        })
    
    # Serve Angular Frontend
    @app.route('/')
    def serve_angular():
        """Serve Angular frontend"""
        if frontend_dist.exists():
            return send_from_directory(str(frontend_dist), 'index.html')
        else:
            return jsonify({
                'message': 'Angular frontend not built. Run "ng build" in frontend folder.',
                'instructions': 'cd frontend/testpoc-frontend && ng build'
            })
    
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
    app = create_unified_app()
    print("🚀 Starting Unified Flask + Angular Server")
    print("📡 API Endpoints: http://localhost:8000/api/*")
    print("🌐 Frontend: http://localhost:8000")
    print("📊 Flask Templates: http://localhost:8000/test-cases")
    app.run(debug=True, host='0.0.0.0', port=8000)
