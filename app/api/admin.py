"""
Admin routes for Test Case Management System
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app

# Create blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-panel')
def admin_panel():
    """Admin panel for managing test cases"""
    # Check if user is admin (implement proper auth)
    # if not is_admin():
    #     return redirect(url_for('main.dashboard'))
    
    # Get services
    services = current_app.config.get('services', {})
    db_service = services.get('db_service')
    
    if not db_service:
        return render_template('admin.html', test_cases_data={})
    
    # Get statistics
    stats = db_service.get_statistics()
    
    return render_template('admin.html', stats=stats)

@admin_bp.route('/admin/upload', methods=['POST'])
def upload_file():
    """Upload Excel file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    # Validate file
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'message': 'Invalid file type'})
    
    try:
        # Save file
        file_path = f"data/excel_files/{file.filename}"
        file.save(file_path)
        
        # Process file
        services = current_app.config.get('services', {})
        file_service = services.get('file_service')
        db_service = services.get('db_service')
        
        if file_service and db_service:
            test_cases = file_service.process_excel_file(file_path)
            
            # Store in database
            for test_case in test_cases:
                db_service.insert_test_case(test_case)
            
            return jsonify({
                'success': True,
                'message': f'File uploaded and processed: {len(test_cases)} test cases'
            })
        else:
            return jsonify({'success': False, 'message': 'Services not available'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@admin_bp.route('/admin/sync')
def sync_files():
    """Sync files with database"""
    try:
        services = current_app.config.get('services', {})
        sync_service = services.get('sync_service')
        
        if not sync_service:
            return jsonify({'success': False, 'message': 'Sync service not available'})
        
        result = sync_service.incremental_sync()
        
        return jsonify({
            'success': True,
            'message': result.get('message', 'Sync completed'),
            'changes_processed': result.get('changes_processed', 0)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Sync failed: {str(e)}'})

@admin_bp.route('/admin/statistics')
def get_statistics():
    """Get system statistics"""
    try:
        services = current_app.config.get('services', {})
        db_service = services.get('db_service')
        
        if not db_service:
            return jsonify({'success': False, 'message': 'Database service not available'})
        
        stats = db_service.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to get statistics: {str(e)}'})

