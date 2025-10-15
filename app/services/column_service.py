import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

class ColumnManager:
    """Manages column definitions and mappings for test cases"""
    
    def __init__(self, config_file: str = "column_config.json"):
        from app.utils.path_resolver import path_resolver
        self.config_file = path_resolver.get_config_path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load column configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading column config: {e}")
                return self.get_default_config()
        else:
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default column configuration"""
        return {
            "primary_key": "TC ID",
            "required_columns": ["TC ID", "Summary"],
            "column_definitions": {
                "TC ID": {
                    "display_name": "Test Case ID",
                    "type": "string",
                    "required": True,
                    "unique": True
                },
                "Summary": {
                    "display_name": "Test Summary",
                    "type": "text",
                    "required": True,
                    "unique": False
                }
            },
            "column_mapping": {
                "legacy_mappings": {}
            },
            "display_settings": {
                "default_columns": ["TC ID", "Summary"],
                "filterable_columns": ["Feature", "Priority", "Status"],
                "searchable_columns": ["TC ID", "Summary", "Feature"]
            }
        }
    
    def get_primary_key(self) -> str:
        """Get the primary key column name"""
        return self.config.get("primary_key", "TC ID")
    
    def get_required_columns(self) -> List[str]:
        """Get list of required columns"""
        return self.config.get("required_columns", ["TC ID", "Summary"])
    
    def get_column_definition(self, column_name: str) -> Optional[Dict[str, Any]]:
        """Get definition for a specific column"""
        return self.config.get("column_definitions", {}).get(column_name)
    
    def get_all_columns(self) -> List[str]:
        """Get all defined column names"""
        return list(self.config.get("column_definitions", {}).keys())
    
    def get_display_name(self, column_name: str) -> str:
        """Get display name for a column"""
        definition = self.get_column_definition(column_name)
        if definition:
            return definition.get("display_name", column_name)
        return column_name
    
    def get_column_type(self, column_name: str) -> str:
        """Get data type for a column"""
        definition = self.get_column_definition(column_name)
        if definition:
            return definition.get("type", "string")
        return "string"
    
    def is_column_required(self, column_name: str) -> bool:
        """Check if a column is required"""
        definition = self.get_column_definition(column_name)
        if definition:
            return definition.get("required", False)
        return False
    
    def is_column_unique(self, column_name: str) -> bool:
        """Check if a column must be unique"""
        definition = self.get_column_definition(column_name)
        if definition:
            return definition.get("unique", False)
        return False
    
    def get_allowed_values(self, column_name: str) -> Optional[List[str]]:
        """Get allowed values for a column (for dropdowns)"""
        definition = self.get_column_definition(column_name)
        if definition:
            return definition.get("allowed_values")
        return None
    
    def get_legacy_mapping(self, legacy_column: str) -> Optional[str]:
        """Get new column name for legacy column name"""
        # Return the same column name since mappings are disabled
        return legacy_column
    
    def map_legacy_columns(self, df_columns: List[str]) -> Dict[str, str]:
        """Map legacy column names to new standardized names"""
        # Return identity mapping since mappings are disabled
        mapping = {}
        for col in df_columns:
            mapping[col] = col
        return mapping
    
    def get_default_display_columns(self) -> List[str]:
        """Get default columns to display in tables"""
        return self.config.get("display_settings", {}).get("default_columns", ["TC ID", "Summary"])
    
    def get_filterable_columns(self) -> List[str]:
        """Get columns that can be used for filtering"""
        return self.config.get("display_settings", {}).get("filterable_columns", [])
    
    def get_searchable_columns(self) -> List[str]:
        """Get columns that can be searched"""
        return self.config.get("display_settings", {}).get("searchable_columns", [])
    
    def validate_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a test case against column definitions"""
        errors = []
        warnings = []
        
        for required_col in self.get_required_columns():
            if required_col not in test_case or not test_case.get(required_col):
                errors.append(f"Required column '{required_col}' is missing or empty")
        
        primary_key = self.get_primary_key()
        if primary_key in test_case and self.is_column_unique(primary_key):
            pass
        
        for column_name, value in test_case.items():
            allowed_values = self.get_allowed_values(column_name)
            if allowed_values and value not in allowed_values:
                warnings.append(f"Column '{column_name}' has value '{value}' not in allowed values: {allowed_values}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def normalize_test_case(self, test_case: Dict[str, Any], file_columns: List[str]) -> Dict[str, Any]:
        """Normalize a test case using column mappings"""
        # Return the test case as-is since mappings are disabled
        return test_case
    
    def get_column_info_for_template(self) -> Dict[str, Any]:
        """Get column information formatted for templates"""
        columns = {}
        for col_name in self.get_all_columns():
            definition = self.get_column_definition(col_name)
            if definition:
                columns[col_name] = {
                    "display_name": definition.get("display_name", col_name),
                    "type": definition.get("type", "string"),
                    "required": definition.get("required", False),
                    "unique": definition.get("unique", False),
                    "allowed_values": definition.get("allowed_values"),
                    "description": definition.get("description", "")
                }
        
        return {
            "primary_key": self.get_primary_key(),
            "required_columns": self.get_required_columns(),
            "all_columns": self.get_all_columns(),
            "default_display_columns": self.get_default_display_columns(),
            "filterable_columns": self.get_filterable_columns(),
            "searchable_columns": self.get_searchable_columns(),
            "column_definitions": columns
        }

column_manager = ColumnManager()

