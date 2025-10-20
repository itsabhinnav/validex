"""
Design Auto-Loader Service
Automatically loads design specifications from Excel files in the design directory
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
from app.utils.path_resolver import path_resolver

class DesignAutoLoader:
    """Service for automatically loading design specifications from Excel files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.design_dir = None
        self._initialize_design_directory()
    
    def _initialize_design_directory(self):
        """Initialize the design directory path"""
        try:
            test_files_path = path_resolver.get_test_files_path()
            self.design_dir = os.path.join(str(test_files_path), 'design')
            
            # Create directory if it doesn't exist
            if not os.path.exists(self.design_dir):
                os.makedirs(self.design_dir, exist_ok=True)
                self.logger.info(f"Created design directory: {self.design_dir}")
            
            self.logger.info(f"Design directory initialized: {self.design_dir}")
            
        except Exception as e:
            self.logger.error(f"Error initializing design directory: {e}")
            self.design_dir = None
    
    def auto_load_designs(self) -> Dict[str, Any]:
        """Automatically load all design specifications from Excel files"""
        if not self.design_dir or not os.path.exists(self.design_dir):
            return {
                'success': False,
                'error': 'Design directory not found',
                'loaded_files': 0,
                'total_designs': 0,
                'designs_data': {}
            }
        
        try:
            designs_data = {}
            total_designs = 0
            loaded_files = 0
            errors = []
            
            self.logger.info("Starting auto-load of design specifications from Excel files...")
            
            # Scan for Excel files
            excel_files = self._find_excel_files()
            
            if not excel_files:
                return {
                    'success': True,
                    'message': 'No Excel files found in design directory',
                    'loaded_files': 0,
                    'total_designs': 0,
                    'designs_data': {}
                }
            
            # Process each Excel file
            for file_path in excel_files:
                try:
                    file_data = self._process_excel_file(file_path)
                    if file_data:
                        filename = os.path.basename(file_path)
                        designs_data[filename] = file_data
                        total_designs += len(file_data)
                        loaded_files += 1
                        self.logger.info(f"Loaded {len(file_data)} design specifications from {filename}")
                    
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(file_path)}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Generate summary
            summary = self._generate_summary(designs_data)
            
            result = {
                'success': True,
                'message': f'Successfully loaded {total_designs} design specifications from {loaded_files} files',
                'loaded_files': loaded_files,
                'total_designs': total_designs,
                'designs_data': designs_data,
                'summary': summary,
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }
            
            if errors:
                result['warning'] = f'Completed with {len(errors)} errors'
            
            self.logger.info(f"Auto-load completed: {loaded_files} files, {total_designs} design specifications")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in auto_load_designs: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_designs': 0,
                'designs_data': {}
            }
    
    def _find_excel_files(self) -> List[str]:
        """Find all Excel files in the design directory"""
        excel_files = []
        
        try:
            for root, dirs, files in os.walk(self.design_dir):
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
        """Process a single Excel file and extract design specifications"""
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
            designs = df.to_dict('records')
            
            # Validate and clean designs
            validated_designs = []
            for design in designs:
                validated_design = self._validate_and_clean_design(design)
                if validated_design:
                    validated_designs.append(validated_design)
            
            return validated_designs
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected format for design specifications"""
        column_mapping = {
            # Design ID variations
            'Design ID': 'design_id',
            'Design Specification ID': 'design_id',
            'Spec ID': 'design_id',
            'ID': 'design_id',
            'Design': 'design_id',
            
            # Title/Name variations
            'Title': 'title',
            'Name': 'title',
            'Design Name': 'title',
            'Specification Name': 'title',
            'Component Name': 'title',
            
            # Description variations
            'Description': 'description',
            'Summary': 'description',
            'Overview': 'description',
            'Details': 'description',
            
            # Design Type variations
            'Design Type': 'design_type',
            'Type': 'design_type',
            'Category': 'design_type',
            'Component Type': 'design_type',
            'Specification Type': 'design_type',
            
            # Component variations
            'Component': 'component',
            'Module': 'component',
            'System': 'component',
            'Feature': 'component',
            'Area': 'component',
            
            # Version variations
            'Version': 'version',
            'Ver': 'version',
            'Rev': 'version',
            'Revision': 'version',
            
            # Status variations
            'Status': 'status',
            'State': 'status',
            'Phase': 'status',
            'Stage': 'status',
            
            # Priority variations
            'Priority': 'priority',
            'Severity': 'priority',
            'Importance': 'priority',
            'Urgency': 'priority',
            
            # Designer/Author variations
            'Designer': 'designer',
            'Author': 'designer',
            'Owner': 'designer',
            'Responsible': 'designer',
            'Created By': 'designer',
            
            # Reviewer variations
            'Reviewer': 'reviewer',
            'Reviewed By': 'reviewer',
            'Approved By': 'reviewer',
            'Validator': 'reviewer',
            
            # Technical specifications
            'Technical Requirements': 'technical_requirements',
            'Tech Requirements': 'technical_requirements',
            'Specifications': 'technical_requirements',
            'Requirements': 'technical_requirements',
            
            # Architecture variations
            'Architecture': 'architecture',
            'Arch': 'architecture',
            'Structure': 'architecture',
            'Framework': 'architecture',
            
            # Dependencies variations
            'Dependencies': 'dependencies',
            'Depends On': 'dependencies',
            'Prerequisites': 'dependencies',
            'Requirements': 'dependencies',
            
            # Implementation variations
            'Implementation Notes': 'implementation_notes',
            'Implementation': 'implementation_notes',
            'Notes': 'implementation_notes',
            'Comments': 'implementation_notes',
            'Remarks': 'implementation_notes',
            
            # Testing variations
            'Testing Requirements': 'testing_requirements',
            'Test Requirements': 'testing_requirements',
            'Validation': 'testing_requirements',
            'Verification': 'testing_requirements',
            
            # Performance variations
            'Performance Requirements': 'performance_requirements',
            'Performance': 'performance_requirements',
            'Metrics': 'performance_requirements',
            'Benchmarks': 'performance_requirements',
            
            # Security variations
            'Security Requirements': 'security_requirements',
            'Security': 'security_requirements',
            'Security Considerations': 'security_requirements',
            
            # Date variations
            'Created Date': 'created_date',
            'Created': 'created_date',
            'Date Created': 'created_date',
            'Design Date': 'created_date',
            'Due Date': 'due_date',
            'Due': 'due_date',
            'Target Date': 'due_date',
            'Deadline': 'due_date',
            'Last Modified': 'last_modified',
            'Modified Date': 'last_modified',
            'Updated': 'last_modified',
            
            # Tags variations
            'Tags': 'tags',
            'Labels': 'tags',
            'Keywords': 'tags',
            'Categories': 'tags',
            
            # Complexity variations
            'Complexity': 'complexity',
            'Difficulty': 'complexity',
            'Effort': 'complexity',
            'Size': 'complexity',
            
            # Risk variations
            'Risk Level': 'risk_level',
            'Risk': 'risk_level',
            'Risk Assessment': 'risk_level',
            
            # Cost variations
            'Cost': 'cost',
            'Budget': 'cost',
            'Estimate': 'cost',
            'Resource Cost': 'cost'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df[new_name] = df[old_name]
                # Remove the original column to avoid duplicates
                if old_name != new_name:
                    df.drop(columns=[old_name], inplace=True)
        
        # Ensure required fields exist with defaults
        if 'design_id' not in df.columns:
            df['design_id'] = [f"DES-{i+1:03d}" for i in range(len(df))]
        
        if 'title' not in df.columns:
            # Try to find any text column as title
            text_columns = df.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                df['title'] = df[text_columns[0]]
            else:
                df['title'] = 'No title provided'
        
        if 'status' not in df.columns:
            df['status'] = 'Draft'
        
        if 'priority' not in df.columns:
            df['priority'] = 'Medium'
        
        if 'design_type' not in df.columns:
            df['design_type'] = 'Functional'
        
        if 'version' not in df.columns:
            df['version'] = '1.0'
        
        return df
    
    def _validate_and_clean_design(self, design: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean a single design specification"""
        try:
            # Remove NaN values
            cleaned_design = {}
            for key, value in design.items():
                if pd.isna(value):
                    cleaned_design[key] = None
                else:
                    cleaned_design[key] = value
            
            # Ensure required fields
            if not cleaned_design.get('design_id'):
                cleaned_design['design_id'] = f"DES-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if not cleaned_design.get('title'):
                cleaned_design['title'] = 'No title provided'
            
            # Set defaults
            cleaned_design.setdefault('status', 'Draft')
            cleaned_design.setdefault('priority', 'Medium')
            cleaned_design.setdefault('design_type', 'Functional')
            cleaned_design.setdefault('version', '1.0')
            cleaned_design.setdefault('created_date', datetime.now().isoformat())
            
            # Clean string fields
            for field in ['title', 'description', 'technical_requirements', 'implementation_notes', 'tags']:
                if field in cleaned_design and cleaned_design[field]:
                    cleaned_design[field] = str(cleaned_design[field]).strip()
            
            return cleaned_design
            
        except Exception as e:
            self.logger.error(f"Error validating design: {e}")
            return None
    
    def _generate_summary(self, designs_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate summary statistics for loaded design specifications"""
        all_designs = []
        for file_data in designs_data.values():
            all_designs.extend(file_data)
        
        if not all_designs:
            return {
                'total': 0,
                'by_status': {},
                'by_priority': {},
                'by_design_type': {},
                'by_designer': {},
                'by_file': {}
            }
        
        # Calculate statistics
        by_status = {}
        by_priority = {}
        by_design_type = {}
        by_designer = {}
        by_file = {}
        
        for design in all_designs:
            # Status distribution
            status = design.get('status', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1
            
            # Priority distribution
            priority = design.get('priority', 'Unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1
            
            # Design type distribution
            design_type = design.get('design_type', 'Unknown')
            by_design_type[design_type] = by_design_type.get(design_type, 0) + 1
            
            # Designer distribution
            designer = design.get('designer', 'Unassigned')
            by_designer[designer] = by_designer.get(designer, 0) + 1
            
            # File distribution
            source_file = design.get('source_file', 'Unknown')
            by_file[source_file] = by_file.get(source_file, 0) + 1
        
        return {
            'total': len(all_designs),
            'by_status': by_status,
            'by_priority': by_priority,
            'by_design_type': by_design_type,
            'by_designer': by_designer,
            'by_file': by_file
        }
    
    def get_design_directory_info(self) -> Dict[str, Any]:
        """Get information about the design directory"""
        if not self.design_dir:
            return {
                'exists': False,
                'path': None,
                'file_count': 0,
                'files': []
            }
        
        try:
            files = []
            file_count = 0
            
            if os.path.exists(self.design_dir):
                for root, dirs, filenames in os.walk(self.design_dir):
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
                'path': self.design_dir,
                'file_count': file_count,
                'files': files
            }
            
        except Exception as e:
            self.logger.error(f"Error getting directory info: {e}")
            return {
                'exists': False,
                'path': self.design_dir,
                'file_count': 0,
                'files': [],
                'error': str(e)
            }
    
    def refresh_designs(self) -> Dict[str, Any]:
        """Refresh design specifications by reloading all files"""
        self.logger.info("Refreshing design specifications...")
        return self.auto_load_designs()
    
    def get_available_columns(self) -> Dict[str, Any]:
        """Get all available columns from loaded design specifications"""
        try:
            designs_data = self.auto_load_designs()
            
            if not designs_data['success']:
                return {
                    'success': False,
                    'error': designs_data.get('error', 'Failed to load design specifications'),
                    'columns': [],
                    'column_values': {}
                }
            
            all_designs = []
            for file_data in designs_data['designs_data'].values():
                all_designs.extend(file_data)
            
            if not all_designs:
                return {
                    'success': True,
                    'columns': [],
                    'column_values': {},
                    'message': 'No design specifications loaded'
                }
            
            # Extract all unique columns
            all_columns = set()
            for design in all_designs:
                all_columns.update(design.keys())
            
            # Remove metadata columns
            metadata_columns = {'source_file', 'loaded_at', 'file_path'}
            filterable_columns = sorted(all_columns - metadata_columns)
            
            # Get unique values for each column
            column_values = {}
            for column in filterable_columns:
                values = set()
                for design in all_designs:
                    value = design.get(column)
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
                'total_designs': len(all_designs),
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
    
    def filter_designs_by_columns(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter design specifications based on column values"""
        try:
            # Load design specifications first
            designs_data = self.auto_load_designs()
            
            if not designs_data['success']:
                return {
                    'success': False,
                    'error': designs_data.get('error', 'Failed to load design specifications'),
                    'filtered_designs': [],
                    'total_filtered': 0
                }
            
            all_designs = []
            for file_data in designs_data['designs_data'].values():
                all_designs.extend(file_data)
            
            if not all_designs:
                return {
                    'success': True,
                    'filtered_designs': [],
                    'total_filtered': 0,
                    'message': 'No design specifications to filter'
                }
            
            # Apply filters
            filtered_designs = []
            for design in all_designs:
                if self._matches_column_filters(design, filters):
                    filtered_designs.append(design)
            
            # Generate summary for filtered results
            summary = self._generate_summary({'filtered': filtered_designs})
            
            return {
                'success': True,
                'filtered_designs': filtered_designs,
                'total_filtered': len(filtered_designs),
                'total_original': len(all_designs),
                'summary': summary,
                'filters_applied': filters
            }
            
        except Exception as e:
            self.logger.error(f"Error filtering design specifications: {e}")
            return {
                'success': False,
                'error': str(e),
                'filtered_designs': [],
                'total_filtered': 0
            }
    
    def _matches_column_filters(self, design: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if design specification matches all applied column filters"""
        for column, filter_value in filters.items():
            if not filter_value or filter_value == '':
                continue
            
            design_value = design.get(column, '')
            
            # Handle different filter types
            if isinstance(filter_value, list):
                # Multiple values (OR condition)
                if not any(str(design_value).lower() == str(fv).lower() for fv in filter_value):
                    return False
            elif isinstance(filter_value, str):
                # Single value or text search
                if filter_value.startswith('*') and filter_value.endswith('*'):
                    # Contains search
                    search_term = filter_value[1:-1].lower()
                    if search_term not in str(design_value).lower():
                        return False
                elif filter_value.startswith('*'):
                    # Ends with search
                    search_term = filter_value[1:].lower()
                    if not str(design_value).lower().endswith(search_term):
                        return False
                elif filter_value.endswith('*'):
                    # Starts with search
                    search_term = filter_value[:-1].lower()
                    if not str(design_value).lower().startswith(search_term):
                        return False
                else:
                    # Exact match
                    if str(design_value).lower() != str(filter_value).lower():
                        return False
            
        return True


