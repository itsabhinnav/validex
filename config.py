import os
import json
from pathlib import Path

class Config:
    """Configuration management for Validex application"""
    
    def __init__(self):
        self.config_file = Path("validex_config.json")
        self.default_config = {
            "jfrog": {
                "base_url": "https://trialdablg5.jfrog.io/artifactory",
                "repository": "testccs-test",
                "root_path": "test",
                "access_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                "enabled": True
            },
            "app": {
                "excel_files_dir": "excel_files",
                "reports_dir": "reports",
                "auto_refresh_interval": 30
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with default config to ensure all keys exist
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using default configuration.")
                return self.default_config.copy()
        else:
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation (e.g., 'jfrog.base_url')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        self.save_config()
    
    def update_jfrog_config(self, base_url=None, repository=None, root_path=None, 
                          access_token=None, enabled=None):
        """Update JFrog configuration"""
        jfrog_config = self.config.get('jfrog', {})
        
        if base_url is not None:
            jfrog_config['base_url'] = base_url
        if repository is not None:
            jfrog_config['repository'] = repository
        if root_path is not None:
            jfrog_config['root_path'] = root_path
        if access_token is not None:
            jfrog_config['access_token'] = access_token
        if enabled is not None:
            jfrog_config['enabled'] = enabled
        
        self.config['jfrog'] = jfrog_config
        self.save_config()
    
    def get_jfrog_config(self):
        """Get complete JFrog configuration"""
        return self.config.get('jfrog', {})
    
    def is_jfrog_enabled(self):
        """Check if JFrog integration is enabled"""
        return self.get('jfrog.enabled', False)
    
    def get_jfrog_file_url(self, filename):
        """Get full JFrog URL for a file"""
        base_url = self.get('jfrog.base_url', '').rstrip('/')
        repository = self.get('jfrog.repository', '')
        root_path = self.get('jfrog.root_path', '').strip('/')
        
        if root_path:
            return f"{base_url}/{repository}/{root_path}/{filename}"
        else:
            return f"{base_url}/{repository}/{filename}"

# Global config instance
config = Config()
