
from flask import Flask
from config.settings import DevelopmentConfig, ProductionConfig, TestingConfig
from app.services.database_service import DatabaseService
from app.services.file_service import FileService
from app.services.sync_service import SyncService
from app.services.column_service import ColumnManager
from app.services.background_sync_service import initialize_background_sync
from app.services.network_security_service import network_security_service
from app.utils.text_config import inject_text_config

db_service = None
file_service = None
sync_service = None
column_manager = None
background_sync_service = None

def create_mvc_app(config_name='development'):
    app = Flask(__name__)
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    global db_service, file_service, sync_service, column_manager, background_sync_service
    
    try:
        print("Initializing database service...")
        db_service = DatabaseService()
        if db_service.initialize():
            print("Database service initialized successfully")
        else:
            print("Database service initialization failed, continuing with limited functionality")
        
        print("Initializing file service...")
        file_service = FileService()
        print("File service initialized successfully")
        
        print("Initializing sync service...")
        sync_service = SyncService()
        print("Sync service initialized successfully")
        
        print("Initializing column manager...")
        column_manager = ColumnManager()
        print("Column manager initialized successfully")
        
        print("Initializing background sync service...")
        try:
            background_sync_service = initialize_background_sync(db_service, file_service, sync_service)
            if background_sync_service:
                _configure_background_sync(background_sync_service)
                print("Background sync service initialized successfully")
            else:
                print("Background sync service not available")
        except Exception as e:
            print(f"Background sync service initialization failed: {e}")
            background_sync_service = None
        
        print("Initializing network security service...")
        network_security_service.initialize()
        print("Network security service initialized successfully")
        
        print("All services initialized successfully")
            
    except Exception as e:
        print(f"Service initialization error: {e}")
        print("Continuing with limited functionality")
        db_service = None
        file_service = None
        sync_service = None
        column_manager = None
        background_sync_service = None
    
    app.context_processor(inject_text_config)
    
    @app.context_processor
    def inject_admin_config():
        from config.settings import config
        return {
            'admin_enabled': config.is_admin_enabled(),
            'auto_launch_browser': config.is_auto_launch_browser_enabled(),
            'startup_delay': config.get_startup_delay()
        }
    
    from app.api.main_routes import main_bp
    app.register_blueprint(main_bp)
    
    try:
        from app.api.sync_routes import sync_bp
        app.register_blueprint(sync_bp)
    except ImportError:
        print("Sync API blueprint not available")
    
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
        if background_sync_service:
            background_sync_service.configure_sync_settings()
            
            if background_sync_service.is_sync_enabled():
                background_sync_service.start_background_sync()
                print("Background sync started")
            else:
                print("Background sync is disabled")
    except Exception as e:
        print(f"Error configuring background sync: {e}")

def get_services():
    """Get application services"""
    return {
        'db_service': db_service,
        'file_service': file_service,
        'sync_service': sync_service,
        'column_manager': column_manager,
        'background_sync_service': background_sync_service
    }
