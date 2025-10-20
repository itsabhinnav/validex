import os
import json
from pathlib import Path
from .config_manager import config_manager

class Config:
    """Configuration management for Validex application - now using centralized config"""
    
    def __init__(self):
        self.config = config_manager.config
    
    def load_config(self):
        """Load configuration from centralized config"""
        return config_manager.config
    
    def save_config(self, config=None):
        """Save configuration using centralized config"""
        if config is not None:
            config_manager.config = config
        config_manager._save_config()
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation"""
        return config_manager.get(key_path, default)
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        config_manager.set(key_path, value)
    
    def update_jfrog_config(self, base_url=None, repository=None, root_path=None, 
                          access_token=None, enabled=None):
        """Update JFrog configuration"""
        jfrog_updates = {}
        if base_url is not None:
            jfrog_updates['base_url'] = base_url
        if repository is not None:
            jfrog_updates['repository'] = repository
        if root_path is not None:
            jfrog_updates['root_path'] = root_path
        if access_token is not None:
            jfrog_updates['access_token'] = access_token
        if enabled is not None:
            jfrog_updates['enabled'] = enabled
        
        config_manager.update_jfrog_config(**jfrog_updates)
    
    def get_jfrog_config(self):
        """Get complete JFrog configuration"""
        return config_manager.get_jfrog_config()
    
    def is_jfrog_enabled(self):
        """Check if JFrog integration is enabled"""
        return config_manager.is_jfrog_enabled()
    
    def is_admin_enabled(self):
        """Check if admin section is enabled"""
        return config_manager.is_admin_enabled()
    
    def is_auto_launch_browser_enabled(self):
        """Check if auto-launch browser is enabled"""
        return config_manager.is_auto_launch_browser_enabled()
    
    def get_startup_delay(self):
        """Get startup delay in seconds"""
        return config_manager.get_startup_delay()
    
    def get_test_cases_per_page(self):
        """Get the default number of test cases per page"""
        return config_manager.get_test_cases_per_page()
    
    def get_network_security_config(self):
        """Get network security configuration"""
        return config_manager.get_section('network_security')
    
    def is_network_restricted(self):
        """Check if network access is restricted"""
        return config_manager.is_network_restricted()
    
    def get_allowed_domains(self):
        """Get list of allowed domains"""
        return config_manager.get_allowed_domains()
    
    def get_allowed_ips(self):
        """Get list of allowed IPs"""
        return config_manager.get_allowed_ips()
    
    def get_blocked_domains(self):
        """Get list of blocked domains"""
        return config_manager.get_blocked_domains()
    
    def get_jfrog_file_url(self, filename):
        """Get full JFrog URL for a file"""
        jfrog_config = config_manager.get_jfrog_config()
        base_url = jfrog_config.get('base_url', '').rstrip('/')
        repository = jfrog_config.get('repository', '')
        root_path = jfrog_config.get('root_path', '').strip('/')
        
        if root_path:
            return f"{base_url}/{repository}/{root_path}/{filename}"
        else:
            return f"{base_url}/{repository}/{filename}"

class DevelopmentConfig:
    """Development configuration using centralized config"""
    DEBUG = config_manager.get('app.debug', True)
    SECRET_KEY = config_manager.get('app.secret_key', 'dev-secret-key')
    DATABASE_URL = f"sqlite:///{config_manager.get_database_path()}"
    UPLOAD_FOLDER = config_manager.get_test_files_dir()
    REPORTS_FOLDER = config_manager.get_reports_dir()
    HOST = config_manager.get('app.host', '127.0.0.1')
    PORT = config_manager.get('app.port', 8000)

class ProductionConfig:
    """Production configuration using centralized config"""
    DEBUG = False
    SECRET_KEY = config_manager.get('app.secret_key', 'prod-secret-key')
    DATABASE_URL = f"sqlite:///{config_manager.get_database_path()}"
    UPLOAD_FOLDER = config_manager.get_test_files_dir()
    REPORTS_FOLDER = config_manager.get_reports_dir()
    HOST = config_manager.get('app.host', '127.0.0.1')
    PORT = config_manager.get('app.port', 8000)

class TestingConfig:
    """Testing configuration using centralized config"""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    DATABASE_URL = 'sqlite:///:memory:'
    UPLOAD_FOLDER = config_manager.get_test_files_dir()
    REPORTS_FOLDER = config_manager.get_reports_dir()

config = Config()
