"""
Main routes for MVC architecture - handles app selection and role management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from app.controllers.dashboard_controller import DashboardController
from app.controllers.test_cases_controller import TestCasesController
from app.controllers.admin_controller import AdminController
from app.controllers.reports_controller import ReportsController

main_bp = Blueprint('main', __name__)

dashboard_controller = DashboardController()
test_cases_controller = TestCasesController()
admin_controller = AdminController()
reports_controller = ReportsController()

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return dashboard_controller._handle_dashboard()

@main_bp.route('/test-cases')
def test_cases():
    """Test cases page"""
    return test_cases_controller._handle_test_cases()

@main_bp.route('/admin')
def admin():
    """Admin page"""
    return admin_controller._handle_admin()

@main_bp.route('/reports')
def reports():
    """Reports page"""
    return reports_controller._handle_reports()

@main_bp.route('/execute-test')
def execute_test():
    """Execute test page"""
    return test_cases_controller._handle_execute_test()

@main_bp.route('/execute-test', methods=['POST'])
def submit_test_execution():
    """Handle test execution submission"""
    return test_cases_controller._handle_submit_test_execution()

@main_bp.route('/test-case-details/<test_id>')
def test_case_details(test_id):
    """Test case details page"""
    return test_cases_controller._handle_test_case_details(test_id)

@main_bp.route('/export-test-cases')
def export_test_cases():
    """Export test cases to file"""
    return test_cases_controller._handle_export_test_cases()

@main_bp.route('/export-test-cases-csv')
def export_test_cases_csv():
    """Export test cases to CSV"""
    return test_cases_controller._handle_export_test_cases_csv()

# Prepare test suite functionality merged into test cases page

@main_bp.route('/export-test-suite')
def export_test_suite():
    """Export test suite with release details"""
    return test_cases_controller._handle_export_test_suite()

@main_bp.route('/setup')
def setup():
    """Setup page"""
    return render_template('auth/setup.html')

@main_bp.route('/jfrog-config')
def jfrog_config():
    """JFrog configuration page"""
    return admin_controller._handle_jfrog_config()

@main_bp.route('/sync-dashboard')
def sync_dashboard():
    """Sync management dashboard"""
    return admin_controller._handle_sync_dashboard()

@main_bp.context_processor
def inject_current_role():
    """Inject current_role into all templates"""
    role = session.get('current_role')
    return dict(current_role=role, min=min, max=max)

test_cases_data = {}

@main_bp.route('/')
def index():
    """Main application selector page"""
    return render_template('common/app_selector.html')

@main_bp.route('/app-selector')
def app_selector():
    """Application selector page"""
    return render_template('common/app_selector.html')

@main_bp.route('/select-app', methods=['POST'])
def select_app():
    """Handle app selection and redirect to appropriate landing page"""
    selected_app = request.form.get('selected_app')
    
    session['current_app'] = selected_app
    
    if selected_app == 'validex':
        return redirect(url_for('main.landing', app='validex'))
    elif selected_app == 'sakura':
        # Check if Sakura is enabled
        from config.settings import config
        if config.is_sakura_enabled():
            return redirect(url_for('sakura.sakura_dashboard'))
        else:
            # Sakura is disabled, redirect to app selector with error message
            return redirect(url_for('main.index'))
    else:
        session['current_app'] = 'validex'
        return redirect(url_for('main.landing', app='validex'))

@main_bp.route('/landing')
def landing():
    """Landing page with role selection"""
    app_name = request.args.get('app', 'validex')
    return render_template('common/landing.html', app_name=app_name)

@main_bp.route('/app')
def app_entry():
    """Application entry point - redirects based on role"""
    role = session.get('current_role')
    if role:
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.role_selection'))

@main_bp.route('/role-selection')
def role_selection():
    """Role selection page"""
    from app.controllers.base_controller import BaseController
    base_controller = BaseController('temp')
    test_cases_data = base_controller.load_test_files()
    
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    
    from config.settings import config
    admin_enabled = config.is_admin_enabled()
    
    return render_template('auth/role_selection.html', 
                         file_count=file_count, 
                         total_cases=total_cases,
                         admin_enabled=admin_enabled)

@main_bp.route('/set-role', methods=['POST'])
def set_role():
    """Set user role"""
    role = request.form.get('role')
    
    if role == 'admin':
        from config.settings import config
        if not config.is_admin_enabled():
            return redirect(url_for('main.role_selection'))
    
    session['current_role'] = role
    
    if role == 'admin':
        return redirect(url_for('main.admin'))
    else:
        return redirect(url_for('main.dashboard'))

@main_bp.route('/logout')
def logout():
    """Logout and return to role selection"""
    session.pop('current_role', None)
    return redirect(url_for('main.role_selection'))


@main_bp.route('/api/filter-test-cases', methods=['POST'])
def filter_test_cases_api():
    """Filter test cases using dynamic criteria"""
    from app.controllers.test_cases_controller import TestCasesController
    from app.services.test_cases_service import TestCasesService
    
    controller = TestCasesController()
    service = TestCasesService()
    
    test_cases_data = controller.load_test_files()
    filters = request.get_json() or {}
    
    # Apply filters
    filtered_cases = service.filter_test_cases(test_cases_data, filters)
    
    # Apply sorting if specified
    sort_by = filters.get('sort_by', 'TC ID')
    sort_order = filters.get('sort_order', 'asc')
    filtered_cases = service.sort_test_cases(filtered_cases, sort_by, sort_order)
    
    # Apply pagination if specified
    page = int(filters.get('page', 1))
    per_page = int(filters.get('per_page', 50))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_cases = filtered_cases[start_idx:end_idx]
    
    return jsonify({
        'test_cases': paginated_cases,
        'total_count': len(filtered_cases),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(filtered_cases) + per_page - 1) // per_page
    })

@main_bp.route('/api/analyze-excel-files', methods=['POST'])
def analyze_excel_files():
    """Analyze Excel files and update configuration dynamically"""
    from app.services.dynamic_config_service import DynamicConfigService
    
    try:
        service = DynamicConfigService()
        results = service.run_full_analysis()
        
        return jsonify({
            'success': results['success'],
            'message': 'Excel files analyzed and configuration updated successfully',
            'analysis_results': results['analysis_results'],
            'timestamp': results['timestamp']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error analyzing Excel files: {str(e)}',
            'error': str(e)
        }), 500

@main_bp.route('/api/app-status')
def get_app_status():
    """Get status of all applications"""
    from app.services.dynamic_config_service import DynamicConfigService
    
    try:
        service = DynamicConfigService()
        status = service.get_app_status()
        
        return jsonify({
            'success': True,
            'app_status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting app status: {str(e)}',
            'error': str(e)
        }), 500

@main_bp.route('/api/auto-refresh-test')
def auto_refresh_test():
    """Test endpoint for auto-refresh functionality"""
    return jsonify({
        'success': True,
        'message': 'Auto-refresh test endpoint',
        'timestamp': datetime.now().isoformat(),
        'auto_refresh_working': True
    })

@main_bp.route('/auto-refresh-test')
def auto_refresh_test_page():
    """Auto-refresh test page"""
    return render_template('validex/auto_refresh_test.html')

@main_bp.route('/prepare-test-suite')
def prepare_test_suite():
    """Redirect to test cases page (merged functionality)"""
    return redirect(url_for('main.test_cases'))

@main_bp.route('/api/filter-options')
def get_filter_options():
    """Get dynamic filter options based on selected app"""
    from app.controllers.test_cases_controller import TestCasesController
    
    controller = TestCasesController()
    test_cases_data = controller.load_test_files()
    
    selected_apps = request.args.getlist('apps')
    if not selected_apps or selected_apps == ['']:
        # Return all options if no app is selected
        apps, test_types, priorities = controller._get_filter_options(test_cases_data)
        enhanced_data = controller.get_enhanced_filter_data(test_cases_data)
        return jsonify({
            'apps': sorted(apps),
            'test_types': sorted(test_types),
            'priorities': sorted(priorities),
            'available_columns': enhanced_data.get('available_columns', []),
            'column_mappings': enhanced_data.get('column_mappings', {}),
            'column_statistics': enhanced_data.get('column_statistics', {})
        })
    
    # Filter data based on selected apps
    filtered_data = {}
    for file_name, file_data in test_cases_data.items():
        for case in file_data:
            if case.get('App', '') in selected_apps:
                if file_name not in filtered_data:
                    filtered_data[file_name] = []
                filtered_data[file_name].append(case)
    
    # Get options from filtered data
    apps, test_types, priorities = controller._get_filter_options(filtered_data)
    enhanced_data = controller.get_enhanced_filter_data(filtered_data)
    
    return jsonify({
        'apps': sorted(apps),
        'test_types': sorted(test_types),
        'priorities': sorted(priorities),
        'available_columns': enhanced_data.get('available_columns', []),
        'column_mappings': enhanced_data.get('column_mappings', {}),
        'column_statistics': enhanced_data.get('column_statistics', {})
    })

@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('errors/500.html'), 500

