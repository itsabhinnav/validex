"""
Main routes for MVC architecture - handles app selection and role management
"""

from flask import Blueprint, request, redirect, url_for, session, jsonify
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

# Export test suite page (moved from test cases page)

@main_bp.route('/export-test-suite-file')
def export_test_suite_file():
    """Export test suite file with release details"""
    return test_cases_controller._handle_export_test_suite()


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
    
    if role == 'admin':
        from config.settings import config
        if not config.is_admin_enabled():
            return redirect('/')
    
    session['current_role'] = role
    
    if role == 'admin':
        return redirect(url_for('main.admin'))
    else:
        return redirect(url_for('main.dashboard'))



@main_bp.route('/api/test-cases', methods=['GET'])
def get_test_cases():
    """Get test cases with filtering and pagination"""
    from app.controllers.test_cases_controller import TestCasesController
    from app.services.test_cases_service import TestCasesService
    
    controller = TestCasesController()
    service = TestCasesService()
    
    test_cases_data = controller.load_test_files()
    
    # Get filter parameters from request
    # App filter removed - no longer needed with standardized schema
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
        'app_filter': '',
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
    
    # Get proper filter options from service
    from app.services.test_cases_service import TestCasesService
    service = TestCasesService()
    all_filter_options = service.get_filter_options(test_cases_data)
    
    return jsonify({
        'test_cases': paginated_cases,
        'filter_options': {
            'apps': sorted(apps),
            'test_types': sorted(test_types),
            'priorities': sorted(priorities),
            'features': sorted(all_filter_options.get('Feature', [])),
            'screen_ids': sorted(all_filter_options.get('Screen ID', [])),
            'test_suite_types': sorted(all_filter_options.get('TestSuite Type', [])),
            'requirement_types': sorted(all_filter_options.get('Requirement Type', [])),
            'regions': sorted(all_filter_options.get('Region', [])),
            'brands': sorted(all_filter_options.get('Brand', []))
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
    
    # App filter removed - return all options without app filtering
    filter_options_result = controller._get_filter_options(test_cases_data)
    if len(filter_options_result) == 3:
        apps, test_types, priorities = filter_options_result
    else:
        apps, test_types = filter_options_result
        priorities = []
    enhanced_data = controller.get_enhanced_filter_data(test_cases_data)
    
    # Get proper filter options from service
    from app.services.test_cases_service import TestCasesService
    service = TestCasesService()
    all_filter_options = service.get_filter_options(test_cases_data)
    
    return jsonify({
        'apps': [],  # Empty apps array since app filter is removed
        'test_types': sorted(test_types),
        'priorities': sorted(priorities),
        'features': sorted(all_filter_options.get('Feature', [])),
        'screen_ids': sorted(all_filter_options.get('Screen ID', [])),
        'test_suite_types': sorted(all_filter_options.get('TestSuite Type', [])),
        'requirement_types': sorted(all_filter_options.get('Requirement Type', [])),
        'regions': sorted(all_filter_options.get('Region', [])),
        'brands': sorted(all_filter_options.get('Brand', [])),
        'available_columns': enhanced_data.get('available_columns', []),
        'column_mappings': enhanced_data.get('column_mappings', {}),
        'column_statistics': enhanced_data.get('column_statistics', {})
    })

@main_bp.route('/api/requirements/auto-load', methods=['POST'])
def auto_load_requirements():
    """Auto-load requirements from Excel files"""
    from app.controllers.requirements_controller import RequirementsController
    
    try:
        controller = RequirementsController()
        result = controller.auto_load_requirements()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'loaded_files': result['loaded_files'],
                'total_requirements': result['total_requirements'],
                'summary': result.get('summary', {}),
                'timestamp': result.get('timestamp'),
                'warning': result.get('warning')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/requirements/refresh', methods=['POST'])
def refresh_requirements():
    """Refresh requirements by reloading all files"""
    from app.controllers.requirements_controller import RequirementsController
    
    try:
        controller = RequirementsController()
        result = controller.refresh_requirements()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'loaded_files': result['loaded_files'],
                'total_requirements': result['total_requirements'],
                'summary': result.get('summary', {}),
                'timestamp': result.get('timestamp'),
                'warning': result.get('warning')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/requirements/columns', methods=['GET'])
def get_requirements_columns():
    """Get all available columns from loaded requirements"""
    from app.controllers.requirements_controller import RequirementsController
    
    try:
        controller = RequirementsController()
        result = controller.get_available_columns()
        
        if result['success']:
            return jsonify({
                'success': True,
                'columns': result['columns'],
                'column_values': result['column_values'],
                'total_requirements': result['total_requirements'],
                'total_columns': result['total_columns']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/auto-load', methods=['POST'])
def auto_load_designs():
    """Auto-load design specifications from Excel files"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        result = controller.auto_load_designs()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'loaded_files': result['loaded_files'],
                'total_designs': result['total_designs'],
                'summary': result.get('summary', {}),
                'timestamp': result.get('timestamp'),
                'warning': result.get('warning')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/refresh', methods=['POST'])
def refresh_designs():
    """Refresh design specifications by reloading all files"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        result = controller.refresh_designs()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'loaded_files': result['loaded_files'],
                'total_designs': result['total_designs'],
                'summary': result.get('summary', {}),
                'timestamp': result.get('timestamp'),
                'warning': result.get('warning')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/directory-info', methods=['GET'])
def get_design_directory_info():
    """Get information about the design directory"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        result = controller.get_design_directory_info()
        
        return jsonify({
            'success': True,
            'directory_info': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/columns', methods=['GET'])
def get_design_columns():
    """Get all available columns from loaded design specifications"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        result = controller.get_available_columns()
        
        if result['success']:
            return jsonify({
                'success': True,
                'columns': result['columns'],
                'column_values': result['column_values'],
                'total_designs': result['total_designs'],
                'total_columns': result['total_columns']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/filter', methods=['POST'])
def filter_designs():
    """Filter design specifications based on column values"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        filters = request.get_json() or {}
        
        result = controller.filter_designs_by_columns(filters)
        
        if result['success']:
            return jsonify({
                'success': True,
                'filtered_designs': result['filtered_designs'],
                'total_filtered': result['total_filtered'],
                'total_original': result['total_original'],
                'summary': result.get('summary', {}),
                'filters_applied': result.get('filters_applied', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/dashboard', methods=['GET'])
def get_design_dashboard():
    """Get design specifications dashboard data"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        result = controller.get_design_dashboard()
        
        if result['success']:
            return jsonify({
                'success': True,
                'summary': result['summary'],
                'recent_designs': result['recent_designs'],
                'designs_data': result['designs_data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design/browse', methods=['GET'])
def browse_designs():
    """Browse and filter design specifications"""
    from app.controllers.design_controller import DesignController
    
    try:
        controller = DesignController()
        result = controller.browse_designs()
        
        if result['success']:
            return jsonify({
                'success': True,
                'designs': result['designs'],
                'total_designs': result['total_designs'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages'],
                'has_prev': result['has_prev'],
                'has_next': result['has_next'],
                'filters': result['filters'],
                'filter_options': result['filter_options'],
                'sort_by': result['sort_by'],
                'sort_order': result['sort_order']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/auto-load', methods=['POST'])
def auto_load_design_phases():
    """Auto-load design phases from Excel files"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.auto_load_design_phases()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'loaded_files': result['loaded_files'],
                'total_phases': result['total_phases'],
                'summary': result.get('summary', {}),
                'timestamp': result.get('timestamp'),
                'warning': result.get('warning')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/refresh', methods=['POST'])
def refresh_design_phases():
    """Refresh design phases by reloading all files"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.refresh_design_phases()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'loaded_files': result['loaded_files'],
                'total_phases': result['total_phases'],
                'summary': result.get('summary', {}),
                'timestamp': result.get('timestamp'),
                'warning': result.get('warning')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/directory-info', methods=['GET'])
def get_design_phase_directory_info():
    """Get information about the design directory"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.get_design_directory_info()
        
        return jsonify({
            'success': True,
            'directory_info': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/columns', methods=['GET'])
def get_design_phase_columns():
    """Get all available columns from loaded design phases"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.get_available_columns()
        
        if result['success']:
            return jsonify({
                'success': True,
                'columns': result['columns'],
                'column_values': result['column_values'],
                'total_phases': result['total_phases'],
                'total_columns': result['total_columns']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/filter', methods=['POST'])
def filter_design_phases():
    """Filter design phases based on column values"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        filters = request.get_json() or {}
        
        result = controller.filter_design_phases_by_columns(filters)
        
        if result['success']:
            return jsonify({
                'success': True,
                'filtered_phases': result['filtered_phases'],
                'total_filtered': result['total_filtered'],
                'total_original': result['total_original'],
                'summary': result.get('summary', {}),
                'filters_applied': result.get('filters_applied', {})
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/dashboard', methods=['GET'])
def get_design_phase_dashboard():
    """Get design phase dashboard data"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.get_design_phase_dashboard()
        
        if result['success']:
            return jsonify({
                'success': True,
                'summary': result['summary'],
                'recent_phases': result['recent_phases'],
                'phases_data': result['phases_data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/browse', methods=['GET'])
def browse_design_phases():
    """Browse and filter design phases"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.browse_design_phases()
        
        if result['success']:
            return jsonify({
                'success': True,
                'phases': result['phases'],
                'total_phases': result['total_phases'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages'],
                'has_prev': result['has_prev'],
                'has_next': result['has_next'],
                'filters': result['filters'],
                'filter_options': result['filter_options'],
                'sort_by': result['sort_by'],
                'sort_order': result['sort_order']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.route('/api/design-phase/<phase_id>', methods=['GET'])
def get_design_phase_details(phase_id):
    """Get detailed information for a specific design phase"""
    from app.controllers.design_phase_controller import DesignPhaseController
    
    try:
        controller = DesignPhaseController()
        result = controller.get_design_phase_details(phase_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'phase': result['phase'],
                'related_phases': result['related_phases']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Design phase not found')
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An error occurred while processing your request'
    }), 500

