"""
Sync Management API Routes
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.background_sync_service import get_background_sync_service
import json

sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')

@sync_bp.route('/status')
def get_sync_status():
    """Get current sync status"""
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'error': 'Background sync service not available'}), 500
        
        status = background_sync.get_sync_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sync_bp.route('/statistics')
def get_sync_statistics():
    """Get sync statistics"""
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'error': 'Background sync service not available'}), 500
        
        stats = background_sync.get_sync_statistics()
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sync_bp.route('/force', methods=['POST'])
def force_sync():
    """Force immediate sync"""
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'error': 'Background sync service not available'}), 500
        
        result = background_sync.force_sync()
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sync_bp.route('/start', methods=['POST'])
def start_sync():
    """Start background sync"""
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'error': 'Background sync service not available'}), 500
        
        background_sync.start_background_sync()
        return jsonify({'success': True, 'message': 'Background sync started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sync_bp.route('/stop', methods=['POST'])
def stop_sync():
    """Stop background sync"""
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'error': 'Background sync service not available'}), 500
        
        background_sync.stop_background_sync()
        return jsonify({'success': True, 'message': 'Background sync stopped'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sync_bp.route('/configure', methods=['POST'])
def configure_sync():
    """Configure sync settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No configuration data provided'}), 400
        
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'error': 'Background sync service not available'}), 500
        
        sync_interval = data.get('sync_interval_seconds', 300)
        change_detection = data.get('change_detection_enabled', True)
        
        background_sync.configure_sync(
            sync_interval=sync_interval,
            enable_change_detection=change_detection
        )
        
        from app.utils.path_resolver import path_resolver
        config = path_resolver.load_config()
        
        config.setdefault('sync', {})
        config['sync'].update({
            'sync_interval_seconds': sync_interval,
            'change_detection_enabled': change_detection
        })
        
        path_resolver.save_config(config)
        
        return jsonify({'success': True, 'message': 'Sync configuration updated'})
        
    except Exception as e:
        print(f"Warning: Could not update configuration file: {e}")
        return jsonify({'error': str(e)}), 500

@sync_bp.route('/health')
def sync_health():
    """Check sync service health"""
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            return jsonify({'status': 'unhealthy', 'error': 'Service not available'}), 500
        
        status = background_sync.get_sync_status()
        is_healthy = status.get('running', False)
        
        return jsonify({
            'status': 'healthy' if is_healthy else 'unhealthy',
            'details': status
        })
        
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

