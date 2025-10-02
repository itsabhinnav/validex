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
from app.utils.text_config import inject_text_config

# Global service instances
db_service = None
file_service = None
sync_service = None
column_manager = None

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
    global db_service, file_service, sync_service, column_manager
    
    try:
        db_service = DatabaseService()
        file_service = FileService()
        sync_service = SyncService()
        column_manager = ColumnManager()
        
        # Initialize database
        with app.app_context():
            db_service.initialize()
    except Exception as e:
        print(f"Warning: Some services failed to initialize: {e}")
        # Continue without services for now
    
    # Register text configuration context processor
    app.context_processor(inject_text_config)
    
    # Register blueprints
    from app.api.routes import main_bp
    app.register_blueprint(main_bp)
    
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

def get_services():
    """Get service instances"""
    return {
        'db_service': db_service,
        'file_service': file_service,
        'sync_service': sync_service,
        'column_manager': column_manager
    }
