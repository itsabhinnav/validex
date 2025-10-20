"""
Path Resolver for Portable Application

This module provides path resolution that works both in development
and in portable/executable environments.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Union

class PathResolver:
    """Resolves paths for both development and portable environments"""
    
    def __init__(self):
        self._base_path = None
        self._is_portable = None
        
    @property
    def base_path(self) -> Path:
        """Get the base application path"""
        if self._base_path is None:
            if getattr(sys, 'frozen', False):
                self._base_path = Path(sys._MEIPASS)
            else:
                self._base_path = Path(__file__).parent.parent.parent
        return self._base_path
    
    @property
    def is_portable(self) -> bool:
        """Check if running in portable mode"""
        if self._is_portable is None:
            self._is_portable = (
                getattr(sys, 'frozen', False) or
                'portable' in str(self.base_path).lower() or
                os.path.exists(self.base_path / 'START_VALIDEX.bat') or
                os.path.exists(self.base_path / 'start_validex.sh')
            )
        return self._is_portable
    
    def resolve_path(self, relative_path: Union[str, Path]) -> Path:
        """Resolve a relative path to absolute path"""
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        
        if relative_path.is_absolute():
            return relative_path
            
        return self.base_path / relative_path
    
    def get_config_path(self, config_file: str = "validex_config.json") -> Path:
        """Get the path to configuration file"""
        return self.resolve_path(f"config/{config_file}")
    
    def get_data_path(self, *subpaths: str) -> Path:
        """Get path to data directory with optional subpaths"""
        return self.resolve_path(Path("data") / Path(*subpaths))
    
    def get_database_path(self) -> Path:
        """Get the database file path"""
        return self.get_data_path("db", "test_cases.db")
    
    def get_logs_path(self, *subpaths: str) -> Path:
        """Get path to logs directory"""
        return self.resolve_path(Path("logs") / Path(*subpaths))
    
    def get_reports_path(self, *subpaths: str) -> Path:
        """Get path to reports directory"""
        return self.get_data_path("reports", *subpaths)
    
    def get_cache_path(self, *subpaths: str) -> Path:
        """Get path to cache directory"""
        return self.get_data_path("cache", *subpaths)
    
    def get_backup_path(self, *subpaths: str) -> Path:
        """Get path to backup directory"""
        return self.get_data_path("backups", *subpaths)
    
    def get_test_files_path(self, *subpaths: str) -> Path:
        """Get path to test files directory"""
        return self.get_data_path("excel_files", *subpaths)
    
    def ensure_directory(self, path: Path) -> Path:
        """Ensure directory exists and return the path"""
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def load_config(self, config_file: str = "validex_config.json") -> dict:
        """Load configuration from file"""
        config_path = self.get_config_path(config_file)
        
        if not config_path.exists():
            return self.get_default_config()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config from {config_path}: {e}")
            return self.get_default_config()
    
    def save_config(self, config: dict, config_file: str = "validex_config.json") -> bool:
        """Save configuration to file"""
        config_path = self.get_config_path(config_file)
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config to {config_path}: {e}")
            return False
    
    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "app": {
                "name": "Validex",
                "version": "1.0.0",
                "debug": True,
                "host": "127.0.0.1",
                "port": 8000
            },
            "database": {
                "path": str(self.get_database_path()),
                "backup_enabled": True
            },
            "filesystem": {
                "test_files_dir": str(self.get_test_files_path()),
                "reports_dir": str(self.get_reports_path()),
                "logs_dir": str(self.get_logs_path())
            }
        }

path_resolver = PathResolver()
