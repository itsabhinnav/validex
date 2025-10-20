"""
Design Phase Auto-Loader Service
Automatically loads design phases from Excel files in the design directory
"""

import os
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
from app.utils.path_resolver import path_resolver

class DesignPhaseAutoLoader:
    """Service for automatically loading design phases from Excel files"""
    
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
    
    def auto_load_design_phases(self) -> Dict[str, Any]:
        """Automatically load all design phases from Excel files"""
        if not self.design_dir or not os.path.exists(self.design_dir):
            return {
                'success': False,
                'error': 'Design directory not found',
                'loaded_files': 0,
                'total_phases': 0,
                'phases_data': {}
            }
        
        try:
            phases_data = {}
            total_phases = 0
            loaded_files = 0
            errors = []
            
            self.logger.info("Starting auto-load of design phases from Excel files...")
            
            # Scan for Excel files
            excel_files = self._find_excel_files()
            
            if not excel_files:
                return {
                    'success': True,
                    'message': 'No Excel files found in design directory',
                    'loaded_files': 0,
                    'total_phases': 0,
                    'phases_data': {}
                }
            
            # Process each Excel file
            for file_path in excel_files:
                try:
                    file_data = self._process_excel_file(file_path)
                    if file_data:
                        filename = os.path.basename(file_path)
                        phases_data[filename] = file_data
                        total_phases += len(file_data)
                        loaded_files += 1
                        self.logger.info(f"Loaded {len(file_data)} design phases from {filename}")
                    
                except Exception as e:
                    error_msg = f"Error processing {os.path.basename(file_path)}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)
            
            # Generate summary
            summary = self._generate_summary(phases_data)
            
            result = {
                'success': True,
                'message': f'Successfully loaded {total_phases} design phases from {loaded_files} files',
                'loaded_files': loaded_files,
                'total_phases': total_phases,
                'phases_data': phases_data,
                'summary': summary,
                'errors': errors,
                'timestamp': datetime.now().isoformat()
            }
            
            if errors:
                result['warning'] = f'Completed with {len(errors)} errors'
            
            self.logger.info(f"Auto-load completed: {loaded_files} files, {total_phases} design phases")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in auto_load_design_phases: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_phases': 0,
                'phases_data': {}
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
        """Process a single Excel file and extract design phases"""
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
            phases = df.to_dict('records')
            
            # Validate and clean phases
            validated_phases = []
            for phase in phases:
                validated_phase = self._validate_and_clean_phase(phase)
                if validated_phase:
                    validated_phases.append(validated_phase)
            
            return validated_phases
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected format for design phases"""
        column_mapping = {
            # Phase ID variations
            'Phase ID': 'phase_id',
            'Design Phase ID': 'phase_id',
            'Phase': 'phase_id',
            'ID': 'phase_id',
            'Phase Number': 'phase_id',
            
            # Phase Name variations
            'Phase Name': 'phase_name',
            'Name': 'phase_name',
            'Title': 'phase_name',
            'Phase Title': 'phase_name',
            'Description': 'phase_name',
            
            # Phase Type variations
            'Phase Type': 'phase_type',
            'Type': 'phase_type',
            'Category': 'phase_type',
            'Phase Category': 'phase_type',
            'Design Phase Type': 'phase_type',
            
            # Phase Status variations
            'Phase Status': 'phase_status',
            'Status': 'phase_status',
            'State': 'phase_status',
            'Current Status': 'phase_status',
            'Phase State': 'phase_status',
            
            # Phase Order variations
            'Phase Order': 'phase_order',
            'Order': 'phase_order',
            'Sequence': 'phase_order',
            'Step': 'phase_order',
            'Phase Number': 'phase_order',
            
            # Phase Duration variations
            'Duration': 'duration',
            'Phase Duration': 'duration',
            'Estimated Duration': 'duration',
            'Time Required': 'duration',
            'Effort': 'duration',
            
            # Phase Dependencies variations
            'Dependencies': 'dependencies',
            'Phase Dependencies': 'dependencies',
            'Prerequisites': 'dependencies',
            'Depends On': 'dependencies',
            'Required Phases': 'dependencies',
            
            # Phase Deliverables variations
            'Deliverables': 'deliverables',
            'Phase Deliverables': 'deliverables',
            'Outputs': 'deliverables',
            'Artifacts': 'deliverables',
            'Phase Outputs': 'deliverables',
            
            # Phase Activities variations
            'Activities': 'activities',
            'Phase Activities': 'activities',
            'Tasks': 'activities',
            'Phase Tasks': 'activities',
            'Work Items': 'activities',
            
            # Phase Resources variations
            'Resources': 'resources',
            'Phase Resources': 'resources',
            'Team Members': 'resources',
            'Assigned To': 'resources',
            'Responsible': 'resources',
            
            # Phase Tools variations
            'Tools': 'tools',
            'Phase Tools': 'tools',
            'Software': 'tools',
            'Technologies': 'tools',
            'Platforms': 'tools',
            
            # Phase Milestones variations
            'Milestones': 'milestones',
            'Phase Milestones': 'milestones',
            'Checkpoints': 'milestones',
            'Gates': 'milestones',
            'Review Points': 'milestones',
            
            # Phase Risks variations
            'Risks': 'risks',
            'Phase Risks': 'risks',
            'Risk Factors': 'risks',
            'Challenges': 'risks',
            'Issues': 'risks',
            
            # Phase Success Criteria variations
            'Success Criteria': 'success_criteria',
            'Phase Success Criteria': 'success_criteria',
            'Acceptance Criteria': 'success_criteria',
            'Completion Criteria': 'success_criteria',
            'Quality Gates': 'success_criteria',
            
            # Phase Start Date variations
            'Start Date': 'start_date',
            'Phase Start Date': 'start_date',
            'Begin Date': 'start_date',
            'Planned Start': 'start_date',
            'Scheduled Start': 'start_date',
            
            # Phase End Date variations
            'End Date': 'end_date',
            'Phase End Date': 'end_date',
            'Finish Date': 'end_date',
            'Planned End': 'end_date',
            'Scheduled End': 'end_date',
            
            # Phase Completion variations
            'Completion': 'completion',
            'Phase Completion': 'completion',
            'Progress': 'completion',
            'Percent Complete': 'completion',
            'Completion Percentage': 'completion',
            
            # Phase Notes variations
            'Notes': 'notes',
            'Phase Notes': 'notes',
            'Comments': 'notes',
            'Remarks': 'notes',
            'Additional Info': 'notes',
            
            # Phase Tags variations
            'Tags': 'tags',
            'Phase Tags': 'tags',
            'Labels': 'tags',
            'Keywords': 'tags',
            'Categories': 'tags'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df[new_name] = df[old_name]
                # Remove the original column to avoid duplicates
                if old_name != new_name:
                    df.drop(columns=[old_name], inplace=True)
        
        # Ensure required fields exist with defaults
        if 'phase_id' not in df.columns:
            df['phase_id'] = [f"PHASE-{i+1:03d}" for i in range(len(df))]
        
        if 'phase_name' not in df.columns:
            # Try to find any text column as phase name
            text_columns = df.select_dtypes(include=['object']).columns
            if len(text_columns) > 0:
                df['phase_name'] = df[text_columns[0]]
            else:
                df['phase_name'] = 'No phase name provided'
        
        if 'phase_status' not in df.columns:
            df['phase_status'] = 'Not Started'
        
        if 'phase_type' not in df.columns:
            df['phase_type'] = 'Design'
        
        if 'phase_order' not in df.columns:
            df['phase_order'] = [i+1 for i in range(len(df))]
        
        return df
    
    def _validate_and_clean_phase(self, phase: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean a single design phase"""
        try:
            # Remove NaN values
            cleaned_phase = {}
            for key, value in phase.items():
                if pd.isna(value):
                    cleaned_phase[key] = None
                else:
                    cleaned_phase[key] = value
            
            # Ensure required fields
            if not cleaned_phase.get('phase_id'):
                cleaned_phase['phase_id'] = f"PHASE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            if not cleaned_phase.get('phase_name'):
                cleaned_phase['phase_name'] = 'No phase name provided'
            
            # Set defaults
            cleaned_phase.setdefault('phase_status', 'Not Started')
            cleaned_phase.setdefault('phase_type', 'Design')
            cleaned_phase.setdefault('phase_order', 1)
            cleaned_phase.setdefault('completion', 0)
            
            # Clean string fields
            for field in ['phase_name', 'deliverables', 'activities', 'notes', 'tags']:
                if field in cleaned_phase and cleaned_phase[field]:
                    cleaned_phase[field] = str(cleaned_phase[field]).strip()
            
            return cleaned_phase
            
        except Exception as e:
            self.logger.error(f"Error validating phase: {e}")
            return None
    
    def _generate_summary(self, phases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate summary statistics for loaded design phases"""
        all_phases = []
        for file_data in phases_data.values():
            all_phases.extend(file_data)
        
        if not all_phases:
            return {
                'total': 0,
                'by_status': {},
                'by_type': {},
                'by_completion': {},
                'by_file': {}
            }
        
        # Calculate statistics
        by_status = {}
        by_type = {}
        by_completion = {}
        by_file = {}
        
        for phase in all_phases:
            # Status distribution
            status = phase.get('phase_status', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1
            
            # Type distribution
            phase_type = phase.get('phase_type', 'Unknown')
            by_type[phase_type] = by_type.get(phase_type, 0) + 1
            
            # Completion distribution
            completion = phase.get('completion', 0)
            if completion is None:
                completion = 0
            completion_range = self._get_completion_range(completion)
            by_completion[completion_range] = by_completion.get(completion_range, 0) + 1
            
            # File distribution
            source_file = phase.get('source_file', 'Unknown')
            by_file[source_file] = by_file.get(source_file, 0) + 1
        
        return {
            'total': len(all_phases),
            'by_status': by_status,
            'by_type': by_type,
            'by_completion': by_completion,
            'by_file': by_file
        }
    
    def _get_completion_range(self, completion: float) -> str:
        """Get completion range for statistics"""
        if completion is None or completion == 0:
            return 'Not Started'
        elif completion < 25:
            return '0-25%'
        elif completion < 50:
            return '25-50%'
        elif completion < 75:
            return '50-75%'
        elif completion < 100:
            return '75-99%'
        else:
            return 'Completed'
    
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
    
    def refresh_design_phases(self) -> Dict[str, Any]:
        """Refresh design phases by reloading all files"""
        self.logger.info("Refreshing design phases...")
        return self.auto_load_design_phases()
    
    def get_available_columns(self) -> Dict[str, Any]:
        """Get all available columns from loaded design phases"""
        try:
            phases_data = self.auto_load_design_phases()
            
            if not phases_data['success']:
                return {
                    'success': False,
                    'error': phases_data.get('error', 'Failed to load design phases'),
                    'columns': [],
                    'column_values': {}
                }
            
            all_phases = []
            for file_data in phases_data['phases_data'].values():
                all_phases.extend(file_data)
            
            if not all_phases:
                return {
                    'success': True,
                    'columns': [],
                    'column_values': {},
                    'message': 'No design phases loaded'
                }
            
            # Extract all unique columns
            all_columns = set()
            for phase in all_phases:
                all_columns.update(phase.keys())
            
            # Remove metadata columns
            metadata_columns = {'source_file', 'loaded_at', 'file_path'}
            filterable_columns = sorted(all_columns - metadata_columns)
            
            # Get unique values for each column
            column_values = {}
            for column in filterable_columns:
                values = set()
                for phase in all_phases:
                    value = phase.get(column)
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
                'total_phases': len(all_phases),
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
    
    def filter_design_phases_by_columns(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter design phases based on column values"""
        try:
            # Load design phases first
            phases_data = self.auto_load_design_phases()
            
            if not phases_data['success']:
                return {
                    'success': False,
                    'error': phases_data.get('error', 'Failed to load design phases'),
                    'filtered_phases': [],
                    'total_filtered': 0
                }
            
            all_phases = []
            for file_data in phases_data['phases_data'].values():
                all_phases.extend(file_data)
            
            if not all_phases:
                return {
                    'success': True,
                    'filtered_phases': [],
                    'total_filtered': 0,
                    'message': 'No design phases to filter'
                }
            
            # Apply filters
            filtered_phases = []
            for phase in all_phases:
                if self._matches_column_filters(phase, filters):
                    filtered_phases.append(phase)
            
            # Generate summary for filtered results
            summary = self._generate_summary({'filtered': filtered_phases})
            
            return {
                'success': True,
                'filtered_phases': filtered_phases,
                'total_filtered': len(filtered_phases),
                'total_original': len(all_phases),
                'summary': summary,
                'filters_applied': filters
            }
            
        except Exception as e:
            self.logger.error(f"Error filtering design phases: {e}")
            return {
                'success': False,
                'error': str(e),
                'filtered_phases': [],
                'total_filtered': 0
            }
    
    def _matches_column_filters(self, phase: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if design phase matches all applied column filters"""
        for column, filter_value in filters.items():
            if not filter_value or filter_value == '':
                continue
            
            phase_value = phase.get(column, '')
            
            # Handle different filter types
            if isinstance(filter_value, list):
                # Multiple values (OR condition)
                if not any(str(phase_value).lower() == str(fv).lower() for fv in filter_value):
                    return False
            elif isinstance(filter_value, str):
                # Single value or text search
                if filter_value.startswith('*') and filter_value.endswith('*'):
                    # Contains search
                    search_term = filter_value[1:-1].lower()
                    if search_term not in str(phase_value).lower():
                        return False
                elif filter_value.startswith('*'):
                    # Ends with search
                    search_term = filter_value[1:].lower()
                    if not str(phase_value).lower().endswith(search_term):
                        return False
                elif filter_value.endswith('*'):
                    # Starts with search
                    search_term = filter_value[:-1].lower()
                    if not str(phase_value).lower().startswith(search_term):
                        return False
                else:
                    # Exact match
                    if str(phase_value).lower() != str(filter_value).lower():
                        return False
            
        return True


