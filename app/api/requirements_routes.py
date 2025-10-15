"""
Requirements API Routes for Sakura Requirements Management System
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from app.controllers.requirements_controller import RequirementsController
from datetime import datetime

requirements_api_bp = Blueprint('requirements_api', __name__, url_prefix='/api/requirements')

# Initialize controller
requirements_controller = RequirementsController()

@requirements_api_bp.route('/auto-load', methods=['POST'])
def auto_load_requirements():
    """Auto-load requirements from Excel files in requirements directory"""
    try:
        result = requirements_controller.auto_load_requirements()
        
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

@requirements_api_bp.route('/refresh', methods=['POST'])
def refresh_requirements():
    """Refresh requirements by reloading all files"""
    try:
        result = requirements_controller.refresh_requirements()
        
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

@requirements_api_bp.route('/directory-info', methods=['GET'])
def get_directory_info():
    """Get information about the requirements directory"""
    try:
        result = requirements_controller.get_requirements_directory_info()
        
        return jsonify({
            'success': True,
            'directory_info': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@requirements_api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Get requirements dashboard data"""
    try:
        result = requirements_controller.get_requirements_dashboard()
        
        if result['success']:
            return jsonify({
                'success': True,
                'summary': result['summary'],
                'recent_requirements': result['recent_requirements'],
                'requirements_data': result['requirements_data']
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

@requirements_api_bp.route('/browse', methods=['GET'])
def browse_requirements():
    """Browse and filter requirements"""
    try:
        result = requirements_controller.browse_requirements()
        
        if result['success']:
            return jsonify({
                'success': True,
                'requirements': result['requirements'],
                'total_requirements': result['total_requirements'],
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

@requirements_api_bp.route('/<requirement_id>', methods=['GET'])
def get_requirement_details(requirement_id):
    """Get detailed information for a specific requirement"""
    try:
        result = requirements_controller.get_requirement_details(requirement_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'requirement': result['requirement'],
                'traceability': result['traceability'],
                'related_requirements': result['related_requirements']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Requirement not found')
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@requirements_api_bp.route('/', methods=['POST'])
def create_requirement():
    """Create a new requirement"""
    try:
        result = requirements_controller.create_requirement()
        
        if result['success']:
            return jsonify({
                'success': True,
                'requirement': result['requirement']
            })
        else:
            return jsonify({
                'success': False,
                'errors': result.get('errors', [result.get('error', 'Unknown error')])
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@requirements_api_bp.route('/<requirement_id>', methods=['PUT'])
def update_requirement(requirement_id):
    """Update an existing requirement"""
    try:
        result = requirements_controller.update_requirement(requirement_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'requirement': result['requirement']
            })
        else:
            return jsonify({
                'success': False,
                'errors': result.get('errors', [result.get('error', 'Unknown error')])
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@requirements_api_bp.route('/<requirement_id>', methods=['DELETE'])
def delete_requirement(requirement_id):
    """Delete a requirement"""
    try:
        result = requirements_controller.delete_requirement(requirement_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
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

@requirements_api_bp.route('/export', methods=['GET'])
def export_requirements():
    """Export requirements to file"""
    try:
        result = requirements_controller.export_requirements()
        
        if result['success']:
            return jsonify({
                'success': True,
                'filename': result['filename'],
                'count': result['count']
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

@requirements_api_bp.route('/import', methods=['POST'])
def import_requirements():
    """Import requirements from file"""
    try:
        result = requirements_controller.import_requirements()
        
        if result['success']:
            return jsonify({
                'success': True,
                'imported_count': result['imported_count'],
                'error_count': result['error_count'],
                'errors': result.get('errors', [])
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@requirements_api_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'API endpoint not found'
    }), 404

@requirements_api_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


