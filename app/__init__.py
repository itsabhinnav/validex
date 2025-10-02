"""
Test Case Management System - Flask Application Factory

Copyright 2025 Validex Project

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from flask import Flask
from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig
from core.database.manager import DatabaseManager
from app.services.database_service import DatabaseService
from app.services.file_service import FileService
from app.services.sync_service import SyncService
from app.services.column_service import ColumnManager
from app.services.background_sync_service import initialize_background_sync
from app.utils.text_config import inject_text_config

# Global service instances
db_service = None
file_service = None
sync_service = None
column_manager = None
background_sync_service = None

def create_app(config_name='development'):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    # Initialize services
    global db_service, file_service, sync_service, column_manager, background_sync_service
    
    try:
        # Initialize database service first
        print("🔧 Initializing database service...")
        db_service = DatabaseService()
        
        # Initialize database with proper error handling
        with app.app_context():
            db_initialized = db_service.initialize()
            if not db_initialized:
                print("⚠️ Database initialization failed, but continuing with limited functionality")
                print("ℹ️ App will work with Excel files only (no database features)")
        
        # Initialize other services
        print("🔧 Initializing file service...")
        file_service = FileService()
        
        print("🔧 Initializing sync service...")
        sync_service = SyncService(db_service, file_service) if db_service else None
        
        print("🔧 Initializing column manager...")
        column_manager = ColumnManager()
        
        # Initialize background sync service only if database is available
        if db_service and db_service.is_initialized():
            print("🔧 Initializing background sync service...")
            background_sync_service = initialize_background_sync(db_service, file_service, sync_service)
            
            # Configure and start background sync if enabled
            with app.app_context():
                _configure_background_sync(background_sync_service)
        else:
            print("⚠️ Skipping background sync service (database not available)")
            background_sync_service = None
            
        print("✅ All services initialized successfully")
            
    except Exception as e:
        print(f"❌ Service initialization error: {e}")
        print("⚠️ Continuing with limited functionality")
        # Set services to None to prevent errors
        db_service = None
        file_service = None
        sync_service = None
        column_manager = None
        background_sync_service = None
    
    # Register text configuration context processor
    app.context_processor(inject_text_config)
    
    # Register admin configuration context processor
    @app.context_processor
    def inject_admin_config():
        from config.settings import config
        return {'admin_enabled': config.is_admin_enabled()}
    
    # Register blueprints
    from app.api.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register sync API blueprint
    try:
        from app.api.sync_routes import sync_bp
        app.register_blueprint(sync_bp)
    except ImportError:
        print("Sync API blueprint not available")
    
    # Register optional blueprints if they exist
    try:
        from app.api.auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        print("Auth blueprint not available")
    
    try:
        from app.api.admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        print("Admin blueprint not available")
    
    return app

def _configure_background_sync(background_sync_service):
    """Configure and start background sync service"""
    try:
        import json
        import os
        
        # Load configuration
        config_path = 'config/validex_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            sync_config = config.get('sync', {})
            
            # Configure background sync
            if sync_config.get('background_sync_enabled', False):
                sync_interval = sync_config.get('sync_interval_seconds', 300)
                change_detection = sync_config.get('change_detection_enabled', True)
                
                background_sync_service.configure_sync(
                    sync_interval=sync_interval,
                    enable_change_detection=change_detection
                )
                
                # Start background sync
                background_sync_service.start_background_sync()
                print("🔄 Background sync enabled and started")
            else:
                print("⏸️ Background sync disabled in configuration")
        else:
            print("⚠️ Configuration file not found, using default settings")
            
    except Exception as e:
        print(f"❌ Error configuring background sync: {e}")

def get_services():
    """Get service instances"""
    return {
        'db_service': db_service,
        'file_service': file_service,
        'sync_service': sync_service,
        'column_manager': column_manager,
        'background_sync_service': background_sync_service
    }
