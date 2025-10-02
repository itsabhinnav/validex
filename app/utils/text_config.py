"""
Text configuration utility for Validex application.
Provides centralized text management for all UI strings.

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

import json
import os
from typing import Dict, Any, Optional


class TextConfig:
    """Centralized text configuration manager."""
    
    def __init__(self, config_path: str = None):
        """Initialize the text configuration.
        
        Args:
            config_path: Path to the text configuration JSON file
        """
        if config_path is None:
            # Default path relative to the app directory
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(current_dir, '..', 'config', 'text_config.json')
        
        self.config_path = config_path
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load the text configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Text configuration file not found at {self.config_path}")
            self._config = {}
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in text configuration file: {e}")
            self._config = {}
    
    def get(self, key_path: str, default: str = "") -> str:
        """Get a text value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to the text value (e.g., 'app.name')
            default: Default value if key is not found
            
        Returns:
            The text value or default if not found
        """
        if not self._config:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return str(value) if value is not None else default
        except (KeyError, TypeError):
            return default
    
    def get_dict(self, key_path: str, default: Dict = None) -> Dict:
        """Get a dictionary value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to the dictionary value
            default: Default dictionary if key is not found
            
        Returns:
            The dictionary value or default if not found
        """
        if default is None:
            default = {}
        
        if not self._config:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value if isinstance(value, dict) else default
        except (KeyError, TypeError):
            return default
    
    def get_list(self, key_path: str, default: list = None) -> list:
        """Get a list value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to the list value
            default: Default list if key is not found
            
        Returns:
            The list value or default if not found
        """
        if default is None:
            default = []
        
        if not self._config:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value if isinstance(value, list) else default
        except (KeyError, TypeError):
            return default
    
    def reload(self):
        """Reload the configuration from file."""
        self._load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary.
        
        Returns:
            The complete configuration dictionary
        """
        return self._config.copy() if self._config else {}


# Global instance
text_config = TextConfig()


def get_text(key_path: str, default: str = "") -> str:
    """Convenience function to get text values.
    
    Args:
        key_path: Dot-separated path to the text value
        default: Default value if key is not found
        
    Returns:
        The text value or default if not found
    """
    return text_config.get(key_path, default)


def get_text_dict(key_path: str, default: Dict = None) -> Dict:
    """Convenience function to get dictionary values.
    
    Args:
        key_path: Dot-separated path to the dictionary value
        default: Default dictionary if key is not found
        
    Returns:
        The dictionary value or default if not found
    """
    return text_config.get_dict(key_path, default)


def get_text_list(key_path: str, default: list = None) -> list:
    """Convenience function to get list values.
    
    Args:
        key_path: Dot-separated path to the list value
        default: Default list if key is not found
        
    Returns:
        The list value or default if not found
    """
    return text_config.get_list(key_path, default)


# Template context processor function
def inject_text_config():
    """Template context processor to inject text configuration into templates."""
    return {
        'text': text_config,
        'get_text': get_text,
        'get_text_dict': get_text_dict,
        'get_text_list': get_text_list
    }
