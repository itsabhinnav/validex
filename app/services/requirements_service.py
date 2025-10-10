"""
Requirements Service for Sakura Requirements Management System
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import re
import os
from app.models.requirement import Requirement
from app.services.database_service import DatabaseService

class RequirementsService:
    """Service for requirements business logic and management"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.requirement_types = [
            'Functional', 'Non-Functional', 'Business', 'Technical', 
            'User Story', 'Epic', 'Feature', 'Bug Fix'
        ]
        self.priorities = ['Critical', 'High', 'Medium', 'Low']
        self.statuses = ['Draft', 'Review', 'Approved', 'In Progress', 'Completed', 'Rejected', 'On Hold']
        self.categories = [
            'Authentication', 'Authorization', 'Data Management', 'UI/UX', 
            'Performance', 'Security', 'Integration', 'Reporting', 'Analytics',
            'API', 'Database', 'Infrastructure', 'Documentation'
        ]
    
    def load_requirements_from_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load requirements from Excel files in requirements directory"""
        import os
        from app.utils.path_resolver import path_resolver
        
        requirements_data = {}
        requirements_dir = os.path.join(str(path_resolver.get_test_files_path()), 'requirements')
        
        if not os.path.exists(requirements_dir):
            print(f"Requirements directory {requirements_dir} not found")
            return {}
        
        print("Loading requirements files...")
        
        for root, dirs, files in os.walk(requirements_dir):
            for file in files:
                if file.endswith(('.xlsx', '.xls')):
                    file_path = os.path.join(root, file)
                    try:
                        df = pd.read_excel(file_path)
                        if not df.empty:
                            print(f"Columns in {file}: {list(df.columns)}")
                            
                            # Standardize column names
                            df = self._standardize_columns(df)
                            
                            # Add metadata
                            df['source_file'] = file
                            df['loaded_at'] = datetime.now().isoformat()
                            
                            requirements_data[file] = df.to_dict('records')
                            print(f"Loaded {len(df)} requirements from {file}")
                    except Exception as e:
                        print(f"Error loading {file}: {e}")
        
        print(f"Total requirement files loaded: {len(requirements_data)}")
        return requirements_data
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to match expected format"""
        column_mapping = {
            'Requirement ID': 'requirement_id',
            'Screen ID': 'screen_id', 
            'Description': 'description',
            'Given': 'given',
            'When': 'when',
            'Then': 'then',
            'Priority': 'priority',
            'Status': 'status',
            'Category': 'category',
            'Assignee': 'assignee',
            'Created Date': 'created_date',
            'Due Date': 'due_date',
            'Tags': 'tags'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df[new_name] = df[old_name]
        
        # Ensure required fields exist
        if 'requirement_id' not in df.columns:
            df['requirement_id'] = [f"REQ-{i+1:03d}" for i in range(len(df))]
        
        if 'status' not in df.columns:
            df['status'] = 'Draft'
        
        if 'priority' not in df.columns:
            df['priority'] = 'Medium'
        
        if 'category' not in df.columns:
            df['category'] = 'Functional'
        
        return df
    
    def get_requirements_summary(self, requirements_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Get summary statistics for requirements"""
        all_requirements = []
        for file_data in requirements_data.values():
            all_requirements.extend(file_data)
        
        if not all_requirements:
            return {
                'total': 0,
                'by_status': {},
                'by_priority': {},
                'by_category': {},
                'by_assignee': {},
                'overdue': 0,
                'due_soon': 0
            }
        
        # Calculate statistics
        by_status = {}
        by_priority = {}
        by_category = {}
        by_assignee = {}
        overdue = 0
        due_soon = 0
        
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
            
            # Assignee distribution
            assignee = req.get('assignee', 'Unassigned')
            by_assignee[assignee] = by_assignee.get(assignee, 0) + 1
            
            # Due date analysis
            due_date = req.get('due_date')
            if due_date:
                try:
                    due_date_obj = pd.to_datetime(due_date).date()
                    today = datetime.now().date()
                    days_until_due = (due_date_obj - today).days
                    
                    if days_until_due < 0:
                        overdue += 1
                    elif days_until_due <= 7:
                        due_soon += 1
                except:
                    pass
        
        return {
            'total': len(all_requirements),
            'by_status': by_status,
            'by_priority': by_priority,
            'by_category': by_category,
            'by_assignee': by_assignee,
            'overdue': overdue,
            'due_soon': due_soon
        }
    
    def filter_requirements(self, requirements_data: Dict[str, List[Dict[str, Any]]], 
                          filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter requirements based on criteria"""
        filtered_requirements = []
        
        for file_name, file_data in requirements_data.items():
            for req in file_data:
                req['source_file'] = file_name
                
                # Apply filters
                if not self._matches_filters(req, filters):
                    continue
                
                filtered_requirements.append(req)
        
        return filtered_requirements
    
    def _matches_filters(self, requirement: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if requirement matches all applied filters"""
        for filter_key, filter_value in filters.items():
            if not filter_value:
                continue
                
            req_value = requirement.get(filter_key, '')
            
            if filter_key == 'search':
                # Full-text search
                search_text = ' '.join(str(v) for v in requirement.values() if v).lower()
                if filter_value.lower() not in search_text:
                    return False
            elif filter_key in ['status', 'priority', 'category', 'assignee']:
                # Exact match for categorical fields
                if str(req_value).lower() != str(filter_value).lower():
                    return False
            elif filter_key == 'tags':
                # Tag matching
                req_tags = str(req_value).lower().split(',')
                filter_tags = [tag.strip().lower() for tag in str(filter_value).split(',')]
                if not any(tag in req_tags for tag in filter_tags):
                    return False
            elif filter_key == 'due_date_range':
                # Date range filtering
                due_date = requirement.get('due_date')
                if due_date:
                    try:
                        due_date_obj = pd.to_datetime(due_date).date()
                        if filter_value == 'overdue':
                            if due_date_obj >= datetime.now().date():
                                return False
                        elif filter_value == 'due_soon':
                            days_until_due = (due_date_obj - datetime.now().date()).days
                            if days_until_due > 7 or days_until_due < 0:
                                return False
                    except:
                        pass
        
        return True
    
    def create_requirement(self, requirement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new requirement"""
        # Generate ID if not provided
        if 'requirement_id' not in requirement_data:
            requirement_data['requirement_id'] = self._generate_requirement_id()
        
        # Set defaults
        requirement_data.setdefault('status', 'Draft')
        requirement_data.setdefault('priority', 'Medium')
        requirement_data.setdefault('category', 'Functional')
        requirement_data.setdefault('created_date', datetime.now().isoformat())
        
        # Validate requirement
        validation_result = self._validate_requirement(requirement_data)
        if not validation_result['valid']:
            return {'success': False, 'errors': validation_result['errors']}
        
        # Save to database or file
        # For now, return success
        return {'success': True, 'requirement': requirement_data}
    
    def update_requirement(self, requirement_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing requirement"""
        # Validate updates
        validation_result = self._validate_requirement(updates, is_update=True)
        if not validation_result['valid']:
            return {'success': False, 'errors': validation_result['errors']}
        
        # Update in database or file
        # For now, return success
        return {'success': True, 'requirement': updates}
    
    def delete_requirement(self, requirement_id: str) -> Dict[str, Any]:
        """Delete a requirement"""
        # Delete from database or file
        # For now, return success
        return {'success': True, 'message': f'Requirement {requirement_id} deleted successfully'}
    
    def _generate_requirement_id(self) -> str:
        """Generate a unique requirement ID"""
        # This would typically query the database for the next available ID
        return f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def _validate_requirement(self, requirement_data: Dict[str, Any], is_update: bool = False) -> Dict[str, Any]:
        """Validate requirement data"""
        errors = []
        
        # Required fields
        required_fields = ['description']
        if not is_update:
            required_fields.append('requirement_id')
        
        for field in required_fields:
            if field not in requirement_data or not requirement_data[field]:
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate status
        if 'status' in requirement_data:
            if requirement_data['status'] not in self.statuses:
                errors.append(f"Status must be one of: {', '.join(self.statuses)}")
        
        # Validate priority
        if 'priority' in requirement_data:
            if requirement_data['priority'] not in self.priorities:
                errors.append(f"Priority must be one of: {', '.join(self.priorities)}")
        
        # Validate category
        if 'category' in requirement_data:
            if requirement_data['category'] not in self.categories:
                errors.append(f"Category must be one of: {', '.join(self.categories)}")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def get_requirement_traceability(self, requirement_id: str) -> Dict[str, Any]:
        """Get traceability information for a requirement"""
        # This would typically query the database for related test cases, user stories, etc.
        return {
            'requirement_id': requirement_id,
            'related_test_cases': [],
            'related_user_stories': [],
            'related_features': [],
            'dependencies': [],
            'impact_analysis': {}
        }
    
    def export_requirements(self, requirements: List[Dict[str, Any]], format: str = 'excel') -> str:
        """Export requirements to file"""
        if format == 'excel':
            df = pd.DataFrame(requirements)
            filename = f"requirements_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            return filename
        elif format == 'csv':
            df = pd.DataFrame(requirements)
            filename = f"requirements_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            return filename
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_requirements(self, file_path: str) -> Dict[str, Any]:
        """Import requirements from file"""
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                return {'success': False, 'error': 'Unsupported file format'}
            
            # Standardize columns
            df = self._standardize_columns(df)
            
            # Validate each requirement
            valid_requirements = []
            errors = []
            
            for index, row in df.iterrows():
                requirement_data = row.to_dict()
                validation_result = self._validate_requirement(requirement_data)
                
                if validation_result['valid']:
                    valid_requirements.append(requirement_data)
                else:
                    errors.append(f"Row {index + 1}: {', '.join(validation_result['errors'])}")
            
            return {
                'success': True,
                'imported_count': len(valid_requirements),
                'error_count': len(errors),
                'errors': errors,
                'requirements': valid_requirements
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
