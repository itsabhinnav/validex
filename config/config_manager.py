"""
Centralized Configuration Manager for Validex
==========================================

This module provides a unified configuration system that consolidates all
scattered configuration files into a single, well-organized structure.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class ConfigManager:
    """Centralized configuration management for Validex application"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "validex_config.json"
        self.config = self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get the complete default configuration"""
        return {
            "app": {
                "name": "Validex",
                "version": "1.0.0",
                "description": " Test Case Management Platform",
                "tagline": "Quality Assurance Management System",
                "debug": True,
                "secret_key": "dev-secret-key-change-in-production",
                "host": "127.0.0.1",
                "port": 8000,
                "admin_enabled": False,
                "sakura_enabled": False,
                "multiselect_threshold": 5,
                "test_cases_per_page": 10,
                "auto_refresh_interval": 30,
                "auto_launch_browser": True,
                "startup_delay": 2
            },
            
            "database": {
                "type": "sqlite",
                "path": "data/db/test_cases.db",
                "backup_enabled": True,
                "backup_interval_hours": 24,
                "max_backups": 7,
                "thread_safe": True,
                "connection_timeout": 30
            },
            
            "filesystem": {
                "test_files_dir": "data/excel_files",
                "reports_dir": "data/reports",
                "cache_dir": "data/cache",
                "logs_dir": "logs",
                "backup_dir": "data/backups",
                "allowed_extensions": [".xlsx", ".xls"],
                "max_file_size_mb": 50
            },
            
            "jfrog": {
                "enabled": False,
                "base_url": "https://your-artifactory.com",
                "repository": "your-repository",
                "root_path": "your-project-path",
                "access_token": "your-access-token",
                "sync_enabled": True,
                "auto_sync_interval": 300,
                "retry_attempts": 3,
                "retry_delay": 60
            },
            
            "network_security": {
                "restricted_mode": True,
                "allowed_domains": [
                    "localhost",
                    "127.0.0.1",
                    "*.jfrog.io"
                ],
                "allowed_ips": [
                    "127.0.0.1",
                    "::1"
                ],
                "blocked_domains": [
                    "malicious-site.com",
                    "*.suspicious-domain.com"
                ],
                "firewall_enabled": False,
                "ssl_required": False
            },
            
            "sync": {
                "background_sync_enabled": True,
                "sync_interval_seconds": 300,
                "change_detection_enabled": True,
                "file_hash_cache_enabled": True,
                "incremental_sync_enabled": True,
                "force_sync_on_startup": False,
                "sync_strategy": "incremental",
                "max_retry_attempts": 3,
                "retry_delay_seconds": 60,
                "concurrent_downloads": 3
            },
            
            "logging": {
                "level": "INFO",
                "console_logging": True,
                "file_logging": True,
                "log_file": "logs/validex.log",
                "max_log_size_mb": 10,
                "backup_count": 5,
                "sync_log_level": "INFO",
                "sync_log_file": "logs/sync.log"
            },
            
            "ui": {
                "theme": "light",
                "language": "en",
                "date_format": "%Y-%m-%d",
                "time_format": "%H:%M:%S",
                "pagination": {
                    "default_per_page": 10,
                    "max_per_page": 100,
                    "show_page_numbers": True
                },
                "filters": {
                    "smart_multiselect_threshold": 5,
                    "search_placeholder": "Search test cases...",
                    "clear_filters_text": "Clear All"
                },
                "notifications": {
                    "auto_hide_delay": 5000,
                    "position": "top-right"
                }
            },
            
            "text": {
                "app_name": "Validex",
                "tagline": " Test Case Management Platform",
                "description": "Streamline your testing workflow with our powerful BDD-style test case management system.",
                "navigation": {
                    "dashboard": "Dashboard",
                    "test_cases": "Test Cases",
                    "reports": "Reports",
                    "admin": "Admin",
                    "jfrog": "JFrog",
                    "logout": "Logout"
                },
                "roles": {
                    "admin": "Administrator",
                    "tester": "Tester",
                    "guest": "Guest"
                },
                "statuses": {
                    "passed": "Passed",
                    "failed": "Failed",
                    "running": "Running",
                    "pending": "Pending",
                    "blocked": "Blocked",
                    "skipped": "Skipped"
                },
                "priorities": {
                    "high": "High",
                    "medium": "Medium",
                    "low": "Low",
                    "critical": "Critical"
                },
                "environments": {
                    "development": "Development",
                    "staging": "Staging",
                    "production": "Production"
                }
            },
            
            "columns": {
                "primary_key": "TC ID",
                "required_columns": ["TC ID", "Summary"],
                "column_definitions": {
                    "TC ID": {
                        "display_name": "Test Case ID",
                        "type": "string",
                        "required": True,
                        "unique": True,
                        "description": "Unique identifier for the test case"
                    },
                    "Summary": {
                        "display_name": "Test Summary",
                        "type": "text",
                        "required": True,
                        "unique": False,
                        "description": "Brief summary of the test case"
                    },
                    "Feature": {
                        "display_name": "HMI Feature",
                        "type": "string",
                        "required": False,
                        "unique": False,
                        "description": "Feature or module being tested"
                    },
                    "Priority": {
                        "display_name": "Priority",
                        "type": "string",
                        "required": False,
                        "unique": False,
                        "description": "Test priority level",
                        "allowed_values": ["High", "Medium", "Low", "Critical"]
                    },
                    "Status": {
                        "display_name": "Status",
                        "type": "string",
                        "required": False,
                        "unique": False,
                        "description": "Current test status",
                        "allowed_values": ["Pending", "Passed", "Failed", "Running", "Blocked", "Skipped"]
                    },
                    "type": {
                        "display_name": "Test Type",
                        "type": "string",
                        "required": False,
                        "unique": False,
                        "description": "Type of test (functional, integration, etc.)"
                    },
                    "Expected Behavior": {
                        "display_name": "Expected Behavior",
                        "type": "text",
                        "required": False,
                        "unique": False,
                        "description": "Expected outcome of the test"
                    }
                },
                "display_settings": {
                    "default_columns": ["TC ID", "Summary", "Feature", "Priority", "Status"],
                    "filterable_columns": ["Feature", "Priority", "Status", "type", "Screen ID"],
                    "searchable_columns": ["TC ID", "Summary", "Feature", "Expected Behavior"]
                }
            },
            
            "export": {
                "formats": ["excel", "csv", "pdf"],
                "default_format": "excel",
                "include_metadata": True,
                "include_execution_history": True,
                "max_export_records": 10000
            },
            
            "security": {
                "session_timeout_minutes": 480,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "password_min_length": 8,
                "require_strong_passwords": False,
                "csrf_protection": True,
                "secure_cookies": False
            },
            
            "performance": {
                "cache_enabled": True,
                "cache_ttl_seconds": 3600,
                "max_concurrent_requests": 100,
                "request_timeout_seconds": 30,
                "database_pool_size": 10,
                "enable_compression": True
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return self._merge_configs(self._get_default_config(), config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using default configuration.")
                return self._get_default_config()
        else:
            self._save_config(self._get_default_config())
            return self._get_default_config()
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user config with default config"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'app.debug')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self._save_config()
    
    def update_section(self, section: str, updates: Dict[str, Any]) -> None:
        """Update an entire configuration section"""
        if section in self.config:
            self.config[section].update(updates)
        else:
            self.config[section] = updates
        self._save_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section"""
        return self.config.get(section, {})
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self._get_default_config()
        self._save_config()

    def is_admin_enabled(self) -> bool:
        """Check if admin section is enabled"""
        return self.get('app.admin_enabled', False)
    
    def is_sakura_enabled(self) -> bool:
        """Check if Sakura app is enabled"""
        return self.get('app.sakura_enabled', False)
    
    def is_jfrog_enabled(self) -> bool:
        """Check if JFrog integration is enabled"""
        return self.get('jfrog.enabled', False)
    
    def is_network_restricted(self) -> bool:
        """Check if network access is restricted"""
        return self.get('network_security.restricted_mode', True)
    
    def get_database_path(self) -> str:
        """Get database file path"""
        return self.get('database.path', 'data/db/test_cases.db')
    
    def get_test_files_dir(self) -> str:
        """Get test files directory"""
        return self.get('filesystem.test_files_dir', 'data/excel_files')
    
    def get_reports_dir(self) -> str:
        """Get reports directory"""
        return self.get('filesystem.reports_dir', 'data/reports')
    
    def get_multiselect_threshold(self) -> int:
        """Get the multiselect threshold for UI switching"""
        return self.get('app.multiselect_threshold', 5)
    
    def get_allowed_domains(self) -> List[str]:
        """Get list of allowed domains"""
        return self.get('network_security.allowed_domains', [])
    
    def get_allowed_ips(self) -> List[str]:
        """Get list of allowed IPs"""
        return self.get('network_security.allowed_ips', [])
    
    def get_blocked_domains(self) -> List[str]:
        """Get list of blocked domains"""
        return self.get('network_security.blocked_domains', [])
    
    def get_jfrog_config(self) -> Dict[str, Any]:
        """Get complete JFrog configuration"""
        return self.get_section('jfrog')
    
    def update_jfrog_config(self, **kwargs) -> None:
        """Update JFrog configuration"""
        jfrog_config = self.get_section('jfrog')
        jfrog_config.update(kwargs)
        self.update_section('jfrog', jfrog_config)
    
    def get_column_definitions(self) -> Dict[str, Any]:
        """Get column definitions"""
        return self.get_section('columns')
    
    def get_text_config(self) -> Dict[str, Any]:
        """Get text/UI configuration"""
        return self.get_section('text')
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return self.get_section('ui')
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get sync configuration"""
        return self.get_section('sync')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get_section('logging')
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.get_section('security')
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.get_section('performance')
    
    def is_auto_launch_browser_enabled(self) -> bool:
        """Check if auto-launch browser is enabled"""
        return self.get('app.auto_launch_browser', True)
    
    def get_startup_delay(self) -> int:
        """Get startup delay in seconds"""
        return self.get('app.startup_delay', 2)

config_manager = ConfigManager()

def get_config():
    """Get the global configuration instance"""
    return config_manager

def get_setting(key_path: str, default: Any = None) -> Any:
    """Get a configuration setting"""
    return config_manager.get(key_path, default)

def set_setting(key_path: str, value: Any) -> None:
    """Set a configuration setting"""
    config_manager.set(key_path, value)

