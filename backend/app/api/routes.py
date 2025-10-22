from flask import Blueprint, request, redirect, url_for, jsonify, current_app, session
import os
import pandas as pd
from datetime import datetime
from app import get_services

# Create blueprint
main_bp = Blueprint('main', __name__)

# Global variable to store test cases data
test_cases_data = {}

def load_test_files():
    """Load test files from the data directory"""
    global test_cases_data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return
    
    test_cases_data = {}
    total_files = 0
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.xlsx'):
            file_path = os.path.join(data_dir, filename)
            try:
                df = pd.read_excel(file_path)
                print(f"Columns in {filename}: {list(df.columns)}")
                
                # Convert DataFrame to list of dictionaries
                cases = df.to_dict('records')
                test_cases_data[filename] = cases
                total_files += 1
                print(f"Loaded {len(cases)} test cases from {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    print(f"Total files loaded: {len(test_cases_data)}")

def check_database_availability():
    """Check if database is available"""
    try:
        services = get_services()
        db_service = services.get('db_service')
        if db_service and db_service.is_available():
            return {'available': True, 'message': 'Database connected'}
        else:
            return {'available': False, 'message': 'Database not available'}
    except Exception as e:
        return {'available': False, 'message': f'Database error: {str(e)}'}

def get_database_stats():
    """Get database statistics"""
    try:
        services = get_services()
        db_service = services.get('db_service')
        if db_service:
            return db_service.get_safe_statistics()
    except Exception as e:
        print(f"Error getting database stats: {e}")
    return {}

# Load test files on startup
load_test_files()

# Removed root route to avoid conflicts with Angular frontend serving

@main_bp.route('/app')
def app_entry():
    """Application entry point - redirects based on role"""
    role = session.get('current_role')
    if role:
        return redirect(url_for('main.dashboard'))
    else:
        return jsonify({'redirect': '/landing'})

@main_bp.route('/set-role', methods=['POST'])
def set_role():
    """Set user role"""
    role = request.form.get('role')
    
    if role in ['admin', 'tester']:
        session['current_role'] = role
        return redirect(url_for('main.dashboard'))
    else:
            return redirect('/')
    
# API Routes for Angular frontend
@main_bp.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """Get test cases with filtering and pagination"""
    from app.controllers.test_cases_controller import TestCasesController
    from app.services.test_cases_service import TestCasesService
    
    controller = TestCasesController()
    service = TestCasesService()
    
    test_cases_data = controller.load_test_files()
    
    # Get filter parameters from request
    app_filter = request.args.get('app', '')
    test_types = request.args.getlist('test_type')
    priorities = request.args.getlist('priority')
    features = request.args.getlist('feature')
    screen_ids = request.args.getlist('screen_id')
    test_suite_types = request.args.getlist('test_suite_type')
    requirement_types = request.args.getlist('requirement_type')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'TC ID')
    sort_order = request.args.get('order', 'asc')
    
    # Create filter object
    filters = {
        'app_filter': app_filter,
        'test_type_filter': test_types,
        'priority_filter': priorities,
        'feature_filter': features,
        'screen_id_filter': screen_ids,
        'test_suite_type_filter': test_suite_types,
        'requirement_type_filter': requirement_types,
        'search_query': search_query,
        'sort_by': sort_by,
        'sort_order': sort_order
    }
    
    # Apply filters
    filtered_cases = service.filter_test_cases(test_cases_data, filters)
    
    # Apply sorting
    filtered_cases = service.sort_test_cases(filtered_cases, sort_by, sort_order)
    
    # Apply pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_cases = filtered_cases[start_idx:end_idx]
    
    # Get filter options
    filter_options_result = controller._get_filter_options(test_cases_data)
    if len(filter_options_result) == 3:
        apps, test_types, priorities = filter_options_result
    else:
        apps, test_types = filter_options_result
        priorities = []
    enhanced_data = controller.get_enhanced_filter_data(test_cases_data)
    
    return jsonify({
        'test_cases': paginated_cases,
        'filter_options': {
            'apps': sorted(apps),
            'test_types': sorted(test_types),
            'priorities': sorted(priorities),
            'features': enhanced_data.get('available_columns', []),
            'screen_ids': enhanced_data.get('available_columns', []),
            'test_suite_types': enhanced_data.get('available_columns', []),
            'requirement_types': enhanced_data.get('available_columns', []),
            'regions': enhanced_data.get('available_columns', []),
            'brands': enhanced_data.get('available_columns', [])
        },
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_cases': len(filtered_cases),
            'total_pages': (len(filtered_cases) + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page < (len(filtered_cases) + per_page - 1) // per_page
        }
    })

@main_bp.route('/api/test-case-details', methods=['GET'])
def get_test_case_details():
    """Get detailed information for a specific test case"""
    test_case_id = request.args.get('test_case_id')
    if not test_case_id:
        return jsonify({'error': 'test_case_id parameter is required'}), 400
    
    from app.controllers.test_cases_controller import TestCasesController
    
    controller = TestCasesController()
    test_cases_data = controller.load_test_files()
    
    # Find the test case
    for file_name, file_data in test_cases_data.items():
        for case in file_data:
            if case.get('TC ID') == test_case_id:
                return jsonify(case)
    
    return jsonify({'error': 'Test case not found'}), 404

# Export routes
@main_bp.route('/export-test-cases')
def export_test_cases():
    """Export test cases to Excel"""
    from app.controllers.test_cases_controller import TestCasesController
    test_cases_controller = TestCasesController()
    return test_cases_controller._handle_export_test_cases()

@main_bp.route('/export-test-cases-csv')
def export_test_cases_csv():
    """Export test cases to CSV"""
    from app.controllers.test_cases_controller import TestCasesController
    test_cases_controller = TestCasesController()
    return test_cases_controller._handle_export_test_cases_csv()

@main_bp.route('/export-test-suite-file')
def export_test_suite_file():
    """Export test suite file with release details"""
    from app.controllers.test_cases_controller import TestCasesController
    test_cases_controller = TestCasesController()
    return test_cases_controller._handle_export_test_suite()

# Error handlers
@main_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An error occurred while processing your request'
    }), 500