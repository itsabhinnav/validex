"""
Dynamic Configuration Service
Automatically parses Excel files and updates configuration based on actual data structure
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
import json
from datetime import datetime
import logging
from collections import defaultdict, Counter

class DynamicConfigService:
    """Service for dynamic configuration based on Excel file analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.excel_extensions = ['.xlsx', '.xls', '.xlsm']
        self.app_directories = {
            'validex': 'data/excel_files/validex'
        }
        
    def analyze_all_apps(self) -> Dict[str, Any]:
        """Analyze all applications and return comprehensive configuration data"""
        results = {}
        
        for app_name, directory in self.app_directories.items():
            if os.path.exists(directory):
                results[app_name] = self.analyze_app_directory(app_name, directory)
            else:
                self.logger.warning(f"Directory {directory} not found for app {app_name}")
                results[app_name] = self._get_empty_app_config()
        
        return results
    
    def analyze_app_directory(self, app_name: str, directory: str) -> Dict[str, Any]:
        """Analyze a specific app directory and return configuration"""
        self.logger.info(f"Analyzing {app_name} directory: {directory}")
        
        excel_files = self._find_excel_files(directory)
        if not excel_files:
            self.logger.warning(f"No Excel files found in {directory}")
            return self._get_empty_app_config()
        
        # Analyze each file
        file_analyses = []
        all_columns = set()
        column_frequency = Counter()
        column_types = defaultdict(set)
        sample_data = {}
        
        for file_path in excel_files:
            analysis = self._analyze_excel_file(file_path)
            if analysis:
                file_analyses.append(analysis)
                all_columns.update(analysis['columns'])
                
                # Count column frequency
                for col in analysis['columns']:
                    column_frequency[col] += 1
                
                # Collect column types
                for col, col_type in analysis['column_types'].items():
                    column_types[col].add(col_type)
                
                # Collect sample data
                for col, samples in analysis['sample_data'].items():
                    if col not in sample_data:
                        sample_data[col] = set()
                    sample_data[col].update(samples)
        
        # Generate configuration
        config = self._generate_app_config(
            app_name, file_analyses, all_columns, 
            column_frequency, column_types, sample_data
        )
        
        return config
    
    def _find_excel_files(self, directory: str) -> List[str]:
        """Find all Excel files in directory"""
        excel_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.excel_extensions):
                    excel_files.append(os.path.join(root, file))
        return excel_files
    
    def _analyze_excel_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            if df.empty:
                return None
            
            # Get basic info
            columns = list(df.columns)
            row_count = len(df)
            
            # Analyze column types
            column_types = {}
            sample_data = {}
            
            for col in columns:
                # Determine column type
                col_type = self._determine_column_type(df[col])
                column_types[col] = col_type
                
                # Get sample values (non-null, unique)
                samples = df[col].dropna().unique()[:10]  # First 10 unique values
                sample_data[col] = [str(s) for s in samples if str(s).strip()]
            
            return {
                'file_path': file_path,
                'file_name': os.path.basename(file_path),
                'columns': columns,
                'row_count': row_count,
                'column_types': column_types,
                'sample_data': sample_data,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return None
    
    def _determine_column_type(self, series: pd.Series) -> str:
        """Determine the most appropriate type for a column"""
        # Remove null values
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return 'string'
        
        # Check for numeric types
        try:
            pd.to_numeric(non_null_series, errors='raise')
            # Check if it's integer or float
            if non_null_series.dtype in ['int64', 'int32']:
                return 'integer'
            else:
                return 'number'
        except (ValueError, TypeError):
            pass
        
        # Check for date types
        try:
            pd.to_datetime(non_null_series, errors='raise')
            return 'date'
        except (ValueError, TypeError):
            pass
        
        # Check for boolean
        if non_null_series.dtype == 'bool':
            return 'boolean'
        
        # Check if it's categorical (limited unique values)
        unique_ratio = len(non_null_series.unique()) / len(non_null_series)
        if unique_ratio < 0.1 and len(non_null_series.unique()) <= 20:
            return 'categorical'
        
        # Default to string
        return 'string'
    
    def _generate_app_config(self, app_name: str, file_analyses: List[Dict], 
                           all_columns: Set[str], column_frequency: Counter,
                           column_types: Dict[str, Set[str]], 
                           sample_data: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Generate configuration for an app based on analysis"""
        
        # Determine required vs optional columns
        total_files = len(file_analyses)
        required_threshold = 0.8  # 80% of files must have this column
        
        required_columns = []
        optional_columns = []
        
        for col in all_columns:
            frequency = column_frequency[col]
            if frequency >= total_files * required_threshold:
                required_columns.append(col)
            else:
                optional_columns.append(col)
        
        # Generate column definitions
        column_definitions = {}
        for col in all_columns:
            # Determine final type (most common type)
            types = column_types[col]
            if types:
                # Convert set to list and find most common type
                type_list = list(types)
                final_type = max(set(type_list), key=type_list.count)
            else:
                final_type = 'string'
            
            # Get sample values
            samples = list(sample_data.get(col, []))[:5]
            
            column_definitions[col] = {
                'display_name': col,
                'type': final_type,
                'required': col in required_columns,
                'unique': self._is_likely_unique(col, file_analyses),
                'description': self._generate_column_description(col, final_type, samples),
                'sample_values': samples,
                'frequency': column_frequency[col],
                'frequency_percentage': round((column_frequency[col] / total_files) * 100, 1)
            }
        
        # Generate mappings (common column name variations)
        mappings = self._generate_column_mappings(all_columns, sample_data)
        
        return {
            'app_name': app_name,
            'total_files': total_files,
            'total_columns': len(all_columns),
            'required_columns': sorted(required_columns),
            'optional_columns': sorted(optional_columns),
            'column_definitions': column_definitions,
            'mappings': mappings,
            'file_analyses': file_analyses,
            'generated_at': datetime.now().isoformat()
        }
    
    def _is_likely_unique(self, column: str, file_analyses: List[Dict]) -> bool:
        """Determine if a column is likely to contain unique values"""
        # Check for common ID patterns
        id_patterns = ['id', 'ID', 'Id', 'tc_id', 'TC ID', 'test_case_id', 'requirement_id']
        if any(pattern in column for pattern in id_patterns):
            return True
        
        # Check if column appears to be unique across files
        unique_count = 0
        for analysis in file_analyses:
            if column in analysis['columns']:
                # This is a simplified check - in practice you'd analyze the actual data
                unique_count += 1
        
        return unique_count > 0
    
    def _generate_column_description(self, column: str, col_type: str, samples: List[str]) -> str:
        """Generate a description for a column"""
        descriptions = {
            'id': 'Unique identifier',
            'summary': 'Brief description or title',
            'description': 'Detailed description',
            'priority': 'Priority level',
            'status': 'Current status',
            'feature': 'Feature or component',
            'type': 'Type or category',
            'screen': 'Screen or page reference',
            'expected': 'Expected result or behavior',
            'given': 'Given condition',
            'when': 'When condition',
            'then': 'Then condition'
        }
        
        # Check for partial matches
        column_lower = column.lower()
        for key, desc in descriptions.items():
            if key in column_lower:
                return desc
        
        # Generate based on type
        type_descriptions = {
            'string': 'Text field',
            'number': 'Numeric value',
            'integer': 'Integer value',
            'date': 'Date field',
            'boolean': 'True/False value',
            'categorical': 'Categorical value'
        }
        
        return type_descriptions.get(col_type, 'Data field')
    
    def _generate_column_mappings(self, all_columns: Set[str], sample_data: Dict[str, Set[str]]) -> Dict[str, List[str]]:
        """Generate column mappings for common variations"""
        mappings = {}
        
        # Common mapping patterns
        mapping_patterns = {
            'id': ['ID', 'Id', 'test_case_id', 'requirement_id', 'TC ID'],
            'summary': ['Summary', 'Description', 'Title', 'Name'],
            'feature': ['Feature', 'Component', 'Module', 'Area'],
            'priority': ['Priority', 'Level', 'Importance'],
            'status': ['Status', 'State', 'Condition'],
            'screen': ['Screen ID', 'Screen', 'Page', 'Page ID'],
            'type': ['Test Type', 'Type', 'Category', 'Kind'],
            'expected': ['Expected Behavior', 'Expected Result', 'Expected', 'Outcome']
        }
        
        for pattern, variations in mapping_patterns.items():
            matches = []
            for col in all_columns:
                for variation in variations:
                    if variation.lower() in col.lower() or col.lower() in variation.lower():
                        matches.append(col)
                        break
            if matches:
                mappings[pattern] = matches
        
        return mappings
    
    def _get_empty_app_config(self) -> Dict[str, Any]:
        """Return empty configuration for apps with no files"""
        return {
            'app_name': '',
            'total_files': 0,
            'total_columns': 0,
            'required_columns': [],
            'optional_columns': [],
            'column_definitions': {},
            'mappings': {},
            'file_analyses': [],
            'generated_at': datetime.now().isoformat()
        }
    
    def update_configuration_files(self, analysis_results: Dict[str, Any]) -> bool:
        """Update configuration files based on analysis results"""
        try:
            # Update validex config
            if 'validex' in analysis_results:
                self._update_validex_config(analysis_results['validex'])
            
            # Update column service config
            self._update_column_service_config(analysis_results)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating configuration files: {e}")
            return False
    
    def _update_validex_config(self, validex_config: Dict[str, Any]) -> None:
        """Update validex configuration"""
        config_path = 'config/validex_config.json'
        
        try:
            # Load existing config
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update columns section
            config['columns'] = {
                'required': validex_config['required_columns'],
                'optional': validex_config['optional_columns'],
                'mappings': {}
            }
            
            # Add dynamic column definitions
            config['dynamic_columns'] = validex_config['column_definitions']
            config['last_auto_update'] = datetime.now().isoformat()
            
            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info("Updated validex_config.json with dynamic columns")
            
        except Exception as e:
            self.logger.error(f"Error updating validex config: {e}")
    
    def _update_validex_config(self, validex_config: Dict[str, Any]) -> None:
        """Update validex configuration"""
        # Update validex-specific config
        config_path = 'config/validex_config.json'
        
        config = {
            'app_name': 'Validex',
            'description': 'Test Case Management System',
            'columns': {
                'required': validex_config['required_columns'],
                'optional': validex_config['optional_columns'],
                'mappings': {}
            },
            'dynamic_columns': validex_config['column_definitions'],
            'last_auto_update': datetime.now().isoformat()
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info("Updated validex_config.json with dynamic columns")
            
        except Exception as e:
            self.logger.error(f"Error updating validex config: {e}")
    
    def _update_column_service_config(self, analysis_results: Dict[str, Any]) -> None:
        """Update column service configuration"""
        # This would integrate with the existing column service
        # For now, we'll create a summary file
        summary_path = 'config/dynamic_columns_summary.json'
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'apps': analysis_results,
            'total_apps': len(analysis_results),
            'total_files': sum(app['total_files'] for app in analysis_results.values()),
            'total_columns': sum(app['total_columns'] for app in analysis_results.values())
        }
        
        try:
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            self.logger.info("Updated dynamic columns summary")
            
        except Exception as e:
            self.logger.error(f"Error updating column service config: {e}")
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run complete analysis and update all configurations"""
        self.logger.info("Starting full dynamic configuration analysis")
        
        # Analyze all apps
        analysis_results = self.analyze_all_apps()
        
        # Update configuration files
        success = self.update_configuration_files(analysis_results)
        
        if success:
            self.logger.info("Dynamic configuration update completed successfully")
        else:
            self.logger.error("Dynamic configuration update failed")
        
        return {
            'success': success,
            'analysis_results': analysis_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_app_status(self) -> Dict[str, Any]:
        """Get current status of all apps"""
        status = {}
        
        for app_name, directory in self.app_directories.items():
            if os.path.exists(directory):
                excel_files = self._find_excel_files(directory)
                status[app_name] = {
                    'enabled': True,
                    'directory': directory,
                    'file_count': len(excel_files),
                    'files': [os.path.basename(f) for f in excel_files]
                }
            else:
                status[app_name] = {
                    'enabled': False,
                    'directory': directory,
                    'file_count': 0,
                    'files': []
                }
        
        return status
