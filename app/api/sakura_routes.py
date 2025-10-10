from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.services.database_service import DatabaseService
from app.services.file_service import FileService
from app.utils.text_config import get_text
from app.controllers.requirements_controller import RequirementsController
from app.controllers.base_controller import BaseController

sakura_bp = Blueprint('sakura', __name__)

@sakura_bp.route('/sakura')
def sakura_dashboard():
    """Sakura dashboard - main entry point for Sakura app"""
    try:
        controller = RequirementsController()
        dashboard_data = controller.get_requirements_dashboard()
        
        return render_template('sakura/dashboard.html', 
                             summary=dashboard_data['summary'],
                             recent_requirements=dashboard_data['recent_requirements'],
                             success=dashboard_data['success'])
    except Exception as e:
        current_app.logger.error(f"Error in sakura dashboard: {e}")
        return render_template('sakura/dashboard.html', 
                             summary={'total': 0, 'by_status': {}, 'by_priority': {}, 'by_category': {}, 'by_assignee': {}, 'overdue': 0, 'due_soon': 0},
                             recent_requirements=[],
                             success=False,
                             error=str(e))

@sakura_bp.route('/sakura/browse-requirements')
def browse_requirements():
    """Browse and manage requirements"""
    try:
        controller = RequirementsController()
        browse_data = controller.browse_requirements()
        
        return render_template('sakura/browse_requirements.html',
                             requirements=browse_data['requirements'],
                             total_requirements=browse_data['total_requirements'],
                             page=browse_data['page'],
                             per_page=browse_data['per_page'],
                             total_pages=browse_data['total_pages'],
                             has_prev=browse_data['has_prev'],
                             has_next=browse_data['has_next'],
                             filters=browse_data['filters'],
                             filter_options=browse_data['filter_options'],
                             sort_by=browse_data['sort_by'],
                             sort_order=browse_data['sort_order'],
                             success=browse_data['success'])
    except Exception as e:
        current_app.logger.error(f"Error in browse requirements: {e}")
        return render_template('sakura/browse_requirements.html',
                             requirements=[],
                             total_requirements=0,
                             page=1,
                             per_page=25,
                             total_pages=0,
                             has_prev=False,
                             has_next=False,
                             filters={},
                             filter_options={},
                             sort_by='requirement_id',
                             sort_order='asc',
                             success=False,
                             error=str(e))

@sakura_bp.route('/sakura/requirement/<requirement_id>')
def requirement_details(requirement_id):
    """View requirement details"""
    try:
        controller = RequirementsController()
        details_data = controller.get_requirement_details(requirement_id)
        
        if not details_data['success']:
            flash(details_data['error'], 'error')
            return redirect(url_for('sakura.browse_requirements'))
        
        return render_template('sakura/requirement_details.html',
                             requirement=details_data['requirement'],
                             traceability=details_data['traceability'],
                             related_requirements=details_data['related_requirements'],
                             success=details_data['success'])
    except Exception as e:
        current_app.logger.error(f"Error in requirement details: {e}")
        flash(f"Error loading requirement details: {e}", 'error')
        return redirect(url_for('sakura.browse_requirements'))

@sakura_bp.route('/sakura/add-requirement')
def add_requirement():
    """Add new requirement page"""
    return render_template('sakura/add_requirement.html')

@sakura_bp.route('/sakura/create-requirement', methods=['POST'])
def create_requirement():
    """Create new requirement"""
    try:
        controller = RequirementsController()
        result = controller.create_requirement()
        
        if result['success']:
            flash('Requirement created successfully!', 'success')
            return redirect(url_for('sakura.requirement_details', requirement_id=result['requirement']['requirement_id']))
        else:
            for error in result['errors']:
                flash(error, 'error')
            return redirect(url_for('sakura.add_requirement'))
    except Exception as e:
        current_app.logger.error(f"Error creating requirement: {e}")
        flash(f"Error creating requirement: {e}", 'error')
        return redirect(url_for('sakura.add_requirement'))

@sakura_bp.route('/sakura/edit-requirement/<requirement_id>')
def edit_requirement(requirement_id):
    """Edit requirement page"""
    try:
        controller = RequirementsController()
        details_data = controller.get_requirement_details(requirement_id)
        
        if not details_data['success']:
            flash(details_data['error'], 'error')
            return redirect(url_for('sakura.browse_requirements'))
        
        return render_template('sakura/edit_requirement.html',
                             requirement=details_data['requirement'],
                             success=details_data['success'])
    except Exception as e:
        current_app.logger.error(f"Error in edit requirement: {e}")
        flash(f"Error loading requirement for editing: {e}", 'error')
        return redirect(url_for('sakura.browse_requirements'))

@sakura_bp.route('/sakura/update-requirement/<requirement_id>', methods=['POST'])
def update_requirement(requirement_id):
    """Update requirement"""
    try:
        controller = RequirementsController()
        result = controller.update_requirement(requirement_id)
        
        if result['success']:
            flash('Requirement updated successfully!', 'success')
            return redirect(url_for('sakura.requirement_details', requirement_id=requirement_id))
        else:
            for error in result['errors']:
                flash(error, 'error')
            return redirect(url_for('sakura.edit_requirement', requirement_id=requirement_id))
    except Exception as e:
        current_app.logger.error(f"Error updating requirement: {e}")
        flash(f"Error updating requirement: {e}", 'error')
        return redirect(url_for('sakura.edit_requirement', requirement_id=requirement_id))

@sakura_bp.route('/sakura/delete-requirement/<requirement_id>', methods=['POST'])
def delete_requirement(requirement_id):
    """Delete requirement"""
    try:
        controller = RequirementsController()
        result = controller.delete_requirement(requirement_id)
        
        if result['success']:
            flash('Requirement deleted successfully!', 'success')
        else:
            flash(result['error'], 'error')
    except Exception as e:
        current_app.logger.error(f"Error deleting requirement: {e}")
        flash(f"Error deleting requirement: {e}", 'error')
    
    return redirect(url_for('sakura.browse_requirements'))

@sakura_bp.route('/sakura/export-requirements')
def export_requirements():
    """Export requirements"""
    try:
        controller = RequirementsController()
        result = controller.export_requirements()
        
        if result['success']:
            flash(f'Requirements exported successfully! {result["count"]} requirements exported to {result["filename"]}', 'success')
        else:
            flash(result['error'], 'error')
    except Exception as e:
        current_app.logger.error(f"Error exporting requirements: {e}")
        flash(f"Error exporting requirements: {e}", 'error')
    
    return redirect(url_for('sakura.browse_requirements'))

@sakura_bp.route('/sakura/import-requirements', methods=['POST'])
def import_requirements():
    """Import requirements"""
    try:
        controller = RequirementsController()
        result = controller.import_requirements()
        
        if result['success']:
            flash(f'Requirements imported successfully! {result["imported_count"]} requirements imported.', 'success')
            if result['error_count'] > 0:
                flash(f'{result["error_count"]} requirements had errors during import.', 'warning')
        else:
            flash(result['error'], 'error')
    except Exception as e:
        current_app.logger.error(f"Error importing requirements: {e}")
        flash(f"Error importing requirements: {e}", 'error')
    
    return redirect(url_for('sakura.browse_requirements'))

# API endpoints for AJAX calls
@sakura_bp.route('/api/sakura/requirements/summary')
def api_requirements_summary():
    """API endpoint for requirements summary"""
    try:
        controller = RequirementsController()
        dashboard_data = controller.get_requirements_dashboard()
        return jsonify(dashboard_data)
    except Exception as e:
        current_app.logger.error(f"Error in API requirements summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sakura_bp.route('/api/sakura/requirements/filter-options')
def api_filter_options():
    """API endpoint for filter options"""
    try:
        controller = RequirementsController()
        requirements_data = controller.requirements_service.load_requirements_from_files()
        filter_options = controller._get_filter_options(requirements_data)
        return jsonify(filter_options)
    except Exception as e:
        current_app.logger.error(f"Error in API filter options: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@sakura_bp.route('/api/sakura/requirements/<requirement_id>')
def api_requirement_details(requirement_id):
    """API endpoint for requirement details"""
    try:
        controller = RequirementsController()
        details_data = controller.get_requirement_details(requirement_id)
        return jsonify(details_data)
    except Exception as e:
        current_app.logger.error(f"Error in API requirement details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Legacy routes for backward compatibility
@sakura_bp.route('/sakura/automation')
def automation():
    """Test automation management"""
    return render_template('sakura/automation.html')

@sakura_bp.route('/sakura/orchestration')
def orchestration():
    """Test orchestration and scheduling"""
    return render_template('sakura/orchestration.html')

@sakura_bp.route('/sakura/monitoring')
def monitoring():
    """Real-time test monitoring"""
    return render_template('sakura/monitoring.html')

@sakura_bp.route('/sakura/insights')
def insights():
    """AI-powered insights and analytics"""
    return render_template('sakura/insights.html')