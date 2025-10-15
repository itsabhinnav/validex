"""
Requirements Auto-Loader Service
Automatically loads requirements from Excel files in the requirements directory
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
from app.utils.path_resolver import path_resolver

class RequirementsAutoLoader:
    """Service for automatically loading requirements from Excel files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.requirements_dir = None
        self._initialize_requirements_directory()
    
    def _initialize_requirements_directory(self):
        """Initialize the requirements directory path"""
        try:
            test_files_path = path_resolver.get_test_files_path()
            self.requirements_dir = os.path.join(str(test_files_path), 'requirements')
            
            # Create directory if it doesn't exist
            if not os.path.exists(self.requirements_dir):
                os.makedirs(self.requirements_dir, exist_ok=True)
                self.logger.info(f"Created requirements directory: {self.requirements_dir}")
            
            self.logger.info(f"Requirements directory initialized: {self.requirements_dir}")
            
        except Exception as e:
            self.logger.error(f"Error initializing requirements directory: {e}")
            self.requirements_dir = None
    
    def auto_load_requirements(self) -> Dict[str, Any]:
        """Automatically load all requirements from Excel files"""
        if not self.requirements_dir or not os.path.exists(self.requirements_dir):
            return {
                'success': False,
                'error': 'Requirements directory not found',
                'loaded_files': 0,
                'total_requirements': 0,
                'requirements_data': {}
            }
        
        try:
            requirements_data = {}
            total_requirements = 0
            loaded_files = 0
            errors = []
            
            self.logger.info("Starting auto-load of requirements from Excel files...")
            
            # Scan for Excel files
            excel_files = self._find_excel_files()
            
            if not excel_files:
                return {
                    'success': True,
                    'message': 'No Excel files found in requirements directory',
                    'loaded_files': 0,
                    'total_requirements': 0,
                    'requirements_data': {}
                }
            
            # Process each Excel file
            for file_path in excel_files:
                try:
                    file_data = self._process_excel_file(file_path)
                    if file_data:
                        filename = os.path.basename(file_path)
                        requirements_data[filename] = file_data
                        total_requirements += len(file_data)
                        loaded_files += 1
                        self.logger.info(f"Loaded {len(file_data)} requirements from {filename}")
                    
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(file_path)}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Generate summary
            summary = self._generate_summary(requirements_data)
            
            result = {
                'success': True,
                'message': f'Successfully loaded {total_requirements} requirements from {loaded_files} files',
                'loaded_files': loaded_files,
                'total_requirements': total_requirements,
                'requirements_data': requirements_data,
                'summary': summary,
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }
            
            if errors:
                result['warning'] = f'Completed with {len(errors)} errors'
            
            self.logger.info(f"Auto-load completed: {loaded_files} files, {total_requirements} requirements")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in auto_load_requirements: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_requirements': 0,
                'requirements_data': {}
            }
    
    def _find_excel_files(self) -> List[str]:
        """Find all Excel files in the requirements directory"""
        excel_files = []
        
        try:
            for root, dirs, files in os.walk(self.requirements_dir):
                for file in files:
                    if file.lower().endswith(('.xlsx', '.xls')):
                        file_path = os.path.join(root, file)
                        excel_files.append(file_path)
            
            self.logger.info(f"Found {len(excel_files)} Excel files")
            return excel_files
            
        except Exception as e:
            self.logger.error(f"Error finding Excel files: {e}")
            return []
    
    def _process_excel_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single Excel file and extract requirements"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            if df.empty:
                self.logger.warning(f"Empty file: {os.path.basename(file_path)}")
                return []
            
            # Standardize column names
            df = self._standardize_columns(df)
            
            # Add metadata
            df['source_file'] = os.path.basename(file_path)
            df['loaded_at'] = datetime.now().isoformat()
            df['file_path'] = file_path
            
            # Convert to list of dictionaries
            requirements = df.to_dict('records')
            
            # Validate and clean requirements
            validated_requirements = []
            for req in requirements:
                validated_req = self._validate_and_clean_requirement(req)
                if validated_req:
                    validated_requirements.append(validated_req)
            
            return validated_requirements
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected format"""
        column_mapping = {
            # Common variations of requirement ID
            'Requirement ID': 'requirement_id',
            'Req ID': 'requirement_id',
            'ID': 'requirement_id',
            'Requirement': 'requirement_id',
            
            # Description variations
            'Description': 'description',
            'Summary': 'description',
            'Title': 'description',
            'Name': 'description',
            
            # Screen ID variations
            'Screen ID': 'screen_id',
            'Screen': 'screen_id',
            'Page': 'screen_id',
            'Component': 'screen_id',
            
            # BDD-style fields
            'Given': 'given',
            'When': 'when',
            'Then': 'then',
            'Given When Then': 'given_when_then',
            
            # Priority variations
            'Priority': 'priority',
            'Severity': 'priority',
            'Importance': 'priority',
            
            # Status variations
            'Status': 'status',
            'State': 'status',
            'Phase': 'status',
            
            # Category variations
            'Category': 'category',
            'Type': 'category',
            'Module': 'category',
            'Feature': 'category',
            
            # Assignee variations
            'Assignee': 'assignee',
            'Owner': 'assignee',
            'Responsible': 'assignee',
            'Developer': 'assignee',
            
            # Date variations
            'Created Date': 'created_date',
            'Created': 'created_date',
            'Date Created': 'created_date',
            'Due Date': 'due_date',
            'Due': 'due_date',
            'Target Date': 'due_date',
            
            # Tags variations
            'Tags': 'tags',
            'Labels': 'tags',
            'Keywords': 'tags'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df[new_name] = df[old_name]
                # Remove the original column to avoid duplicates
                if old_name != new_name:
                    df.drop(columns=[old_name], inplace=True)
        
        # Ensure required fields exist with defaults
        if 'requirement_id' not in df.columns:
            df['requirement_id'] = [f"REQ-{i+1:03d}" for i in range(len(df))]
        
        if 'description' not in df.columns:
            # Try to find any text column as description
            text_columns = df.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                df['description'] = df[text_columns[0]]
            else:
                df['description'] = 'No description provided'
        
        if 'status' not in df.columns:
            df['status'] = 'Draft'
        
        if 'priority' not in df.columns:
            df['priority'] = 'Medium'
        
        if 'category' not in df.columns:
            df['category'] = 'Functional'
        
        return df
    
    def _validate_and_clean_requirement(self, requirement: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean a single requirement"""
        try:
            # Remove NaN values
            cleaned_req = {}
            for key, value in requirement.items():
                if pd.isna(value):
                    cleaned_req[key] = None
                else:
                    cleaned_req[key] = value
            
            # Ensure required fields
            if not cleaned_req.get('requirement_id'):
                cleaned_req['requirement_id'] = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if not cleaned_req.get('description'):
                cleaned_req['description'] = 'No description provided'
            
            # Set defaults
            cleaned_req.setdefault('status', 'Draft')
            cleaned_req.setdefault('priority', 'Medium')
            cleaned_req.setdefault('category', 'Functional')
            cleaned_req.setdefault('created_date', datetime.now().isoformat())
            
            # Clean string fields
            for field in ['description', 'given', 'when', 'then', 'tags']:
                if field in cleaned_req and cleaned_req[field]:
                    cleaned_req[field] = str(cleaned_req[field]).strip()
            
            return cleaned_req
            
        except Exception as e:
            self.logger.error(f"Error validating requirement: {e}")
            return None
    
    def _generate_summary(self, requirements_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate summary statistics for loaded requirements"""
        all_requirements = []
        for file_data in requirements_data.values():
            all_requirements.extend(file_data)
        
        if not all_requirements:
            return {
                'total': 0,
                'by_status': {},
                'by_priority': {},
                'by_category': {},
                'by_file': {}
            }
        
        # Calculate statistics
        by_status = {}
        by_priority = {}
        by_category = {}
        by_file = {}
        
        for req in all_requirements:
            # Status distribution
            status = req.get('status', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1
            
            # Priority distribution
            priority = req.get('priority', 'Unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Category distribution
            category = req.get('category', 'Unknown')
            by_category[category] = by_category.get(category, 0) + 1
            
            # File distribution
            source_file = req.get('source_file', 'Unknown')
            by_file[source_file] = by_file.get(source_file, 0) + 1
        
        return {
            'total': len(all_requirements),
            'by_status': by_status,
            'by_priority': by_priority,
            'by_category': by_category,
            'by_file': by_file
        }
    
    def get_requirements_directory_info(self) -> Dict[str, Any]:
        """Get information about the requirements directory"""
        if not self.requirements_dir:
            return {
                'exists': False,
                'path': None,
                'file_count': 0,
                'files': []
            }
        
        try:
            files = []
            file_count = 0
            
            if os.path.exists(self.requirements_dir):
                for root, dirs, filenames in os.walk(self.requirements_dir):
                    for filename in filenames:
                        if filename.lower().endswith(('.xlsx', '.xls')):
                            file_path = os.path.join(root, filename)
                            file_stat = os.stat(file_path)
                            files.append({
                                'name': filename,
                                'path': file_path,
                                'size': file_stat.st_size,
                                'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                            })
                            file_count += 1
            
            return {
                'exists': True,
                'path': self.requirements_dir,
                'file_count': file_count,
                'files': files
            }
            
        except Exception as e:
            self.logger.error(f"Error getting directory info: {e}")
            return {
                'exists': False,
                'path': self.requirements_dir,
                'file_count': 0,
                'files': [],
                'error': str(e)
            }
    
    def refresh_requirements(self) -> Dict[str, Any]:
        """Refresh requirements by reloading all files"""
        self.logger.info("Refreshing requirements...")
        return self.auto_load_requirements()
    
    def get_available_columns(self) -> Dict[str, Any]:
        """Get all available columns from loaded requirements"""
        try:
            requirements_data = self.auto_load_requirements()
            
            if not requirements_data['success']:
                return {
                    'success': False,
                    'error': requirements_data.get('error', 'Failed to load requirements'),
                    'columns': [],
                    'column_values': {}
                }
            
            all_requirements = []
            for file_data in requirements_data['requirements_data'].values():
                all_requirements.extend(file_data)
            
            if not all_requirements:
                return {
                    'success': True,
                    'columns': [],
                    'column_values': {},
                    'message': 'No requirements loaded'
                }
            
            # Extract all unique columns
            all_columns = set()
            for req in all_requirements:
                all_columns.update(req.keys())
            
            # Remove metadata columns
            metadata_columns = {'source_file', 'loaded_at', 'file_path'}
            filterable_columns = sorted(all_columns - metadata_columns)
            
            # Get unique values for each column
            column_values = {}
            for column in filterable_columns:
                values = set()
                for req in all_requirements:
                    value = req.get(column)
                    if value is not None and str(value).strip():
                        values.add(str(value).strip())
                
                # Sort values and limit to reasonable number
                sorted_values = sorted(values)
                if len(sorted_values) > 100:  # Limit to prevent UI overload
                    sorted_values = sorted_values[:100]
                    sorted_values.append('... (more values available)')
                
                column_values[column] = sorted_values
            
            return {
                'success': True,
                'columns': filterable_columns,
                'column_values': column_values,
                'total_requirements': len(all_requirements),
                'total_columns': len(filterable_columns)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting available columns: {e}")
            return {
                'success': False,
                'error': str(e),
                'columns': [],
                'column_values': {}
            }
    
    def filter_requirements_by_columns(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter requirements based on column values"""
        try:
            # Load requirements first
            requirements_data = self.auto_load_requirements()
            
            if not requirements_data['success']:
                return {
                    'success': False,
                    'error': requirements_data.get('error', 'Failed to load requirements'),
                    'filtered_requirements': [],
                    'total_filtered': 0
                }
            
            all_requirements = []
            for file_data in requirements_data['requirements_data'].values():
                all_requirements.extend(file_data)
            
            if not all_requirements:
                return {
                    'success': True,
                    'filtered_requirements': [],
                    'total_filtered': 0,
                    'message': 'No requirements to filter'
                }
            
            # Apply filters
            filtered_requirements = []
            for req in all_requirements:
                if self._matches_column_filters(req, filters):
                    filtered_requirements.append(req)
            
            # Generate summary for filtered results
            summary = self._generate_summary({'filtered': filtered_requirements})
            
            return {
                'success': True,
                'filtered_requirements': filtered_requirements,
                'total_filtered': len(filtered_requirements),
                'total_original': len(all_requirements),
                'summary': summary,
                'filters_applied': filters
            }
            
        except Exception as e:
            self.logger.error(f"Error filtering requirements: {e}")
            return {
                'success': False,
                'error': str(e),
                'filtered_requirements': [],
                'total_filtered': 0
            }
    
    def _matches_column_filters(self, requirement: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if requirement matches all applied column filters"""
        for column, filter_value in filters.items():
            if not filter_value or filter_value == '':
                continue
            
            req_value = requirement.get(column, '')
            
            # Handle different filter types
            if isinstance(filter_value, list):
                # Multiple values (OR condition)
                if not any(str(req_value).lower() == str(fv).lower() for fv in filter_value):
                    return False
            elif isinstance(filter_value, str):
                # Single value or text search
                if filter_value.startswith('*') and filter_value.endswith('*'):
                    # Contains search
                    search_term = filter_value[1:-1].lower()
                    if search_term not in str(req_value).lower():
                        return False
                elif filter_value.startswith('*'):
                    # Ends with search
                    search_term = filter_value[1:].lower()
                    if not str(req_value).lower().endswith(search_term):
                        return False
                elif filter_value.endswith('*'):
                    # Starts with search
                    search_term = filter_value[:-1].lower()
                    if not str(req_value).lower().startswith(search_term):
                        return False
                else:
                    # Exact match
                    if str(req_value).lower() != str(filter_value).lower():
                        return False
            
        return True
