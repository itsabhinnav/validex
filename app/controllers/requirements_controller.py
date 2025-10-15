"""
Requirements Controller for Sakura Requirements Management System
"""

from flask import request, session, current_app
from typing import Dict, Any, List, Optional
from app.services.requirements_service import RequirementsService
from app.services.requirements_auto_loader import RequirementsAutoLoader
from app.models.requirement import Requirement

class RequirementsController:
    """Controller for requirements management"""
    
    def __init__(self):
        self.requirements_service = RequirementsService()
        self.auto_loader = RequirementsAutoLoader()
    
    def get_requirements_dashboard(self) -> Dict[str, Any]:
        """Get requirements dashboard data"""
        try:
            # Load requirements data
            requirements_data = self.requirements_service.load_requirements_from_files()
            
            # Get summary statistics
            summary = self.requirements_service.get_requirements_summary(requirements_data)
            
            # Get recent requirements
            all_requirements = []
            for file_data in requirements_data.values():
                all_requirements.extend(file_data)
            
            # Sort by created date (most recent first)
            recent_requirements = sorted(
                all_requirements, 
                key=lambda x: x.get('created_date', ''), 
                reverse=True
            )[:10]
            
            return {
                'summary': summary,
                'recent_requirements': recent_requirements,
                'requirements_data': requirements_data,
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting requirements dashboard: {e}")
            return {
                'summary': {
                    'total': 0,
                    'by_status': {},
                    'by_priority': {},
                    'by_category': {},
                    'by_assignee': {},
                    'overdue': 0,
                    'due_soon': 0
                },
                'recent_requirements': [],
                'requirements_data': {},
                'success': False,
                'error': str(e)
            }
    
    def browse_requirements(self) -> Dict[str, Any]:
        """Browse and filter requirements"""
        try:
            # Load requirements data
            requirements_data = self.requirements_service.load_requirements_from_files()
            
            # Get filter parameters
            filters = self._get_filter_parameters()
            
            # Apply filters
            filtered_requirements = self.requirements_service.filter_requirements(
                requirements_data, filters
            )
            
            # Get sorting parameters
            sort_by = request.args.get('sort', 'requirement_id')
            sort_order = request.args.get('order', 'asc')
            
            # Sort requirements
            filtered_requirements = self._sort_requirements(filtered_requirements, sort_by, sort_order)
            
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 25))
            
            # Calculate pagination
            total_requirements = len(filtered_requirements)
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_requirements = filtered_requirements[start_index:end_index]
            
            # Calculate pagination info
            total_pages = (total_requirements + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            # Get filter options
            filter_options = self._get_filter_options(requirements_data)
            
            return {
                'requirements': paginated_requirements,
                'total_requirements': total_requirements,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'filters': filters,
                'filter_options': filter_options,
                'sort_by': sort_by,
                'sort_order': sort_order,
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error browsing requirements: {e}")
            return {
                'requirements': [],
                'total_requirements': 0,
                'page': 1,
                'per_page': 25,
                'total_pages': 0,
                'has_prev': False,
                'has_next': False,
                'filters': {},
                'filter_options': {},
                'sort_by': 'requirement_id',
                'sort_order': 'asc',
                'success': False,
                'error': str(e)
            }
    
    def get_requirement_details(self, requirement_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific requirement"""
        try:
            # Load requirements data
            requirements_data = self.requirements_service.load_requirements_from_files()
            
            # Find the requirement
            requirement = None
            for file_data in requirements_data.values():
                for req in file_data:
                    if req.get('requirement_id') == requirement_id:
                        requirement = req
                        break
                if requirement:
                    break
            
            if not requirement:
                return {
                    'requirement': None,
                    'success': False,
                    'error': f'Requirement {requirement_id} not found'
                }
            
            # Get traceability information
            traceability = self.requirements_service.get_requirement_traceability(requirement_id)
            
            # Get related requirements
            related_requirements = self._get_related_requirements(requirement, requirements_data)
            
            return {
                'requirement': requirement,
                'traceability': traceability,
                'related_requirements': related_requirements,
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting requirement details: {e}")
            return {
                'requirement': None,
                'traceability': {},
                'related_requirements': [],
                'success': False,
                'error': str(e)
            }
    
    def create_requirement(self) -> Dict[str, Any]:
        """Create a new requirement"""
        try:
            # Get requirement data from request
            requirement_data = request.get_json() or request.form.to_dict()
            
            # Create requirement
            result = self.requirements_service.create_requirement(requirement_data)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error creating requirement: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_requirement(self, requirement_id: str) -> Dict[str, Any]:
        """Update an existing requirement"""
        try:
            # Get update data from request
            updates = request.get_json() or request.form.to_dict()
            
            # Update requirement
            result = self.requirements_service.update_requirement(requirement_id, updates)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error updating requirement: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_requirement(self, requirement_id: str) -> Dict[str, Any]:
        """Delete a requirement"""
        try:
            # Delete requirement
            result = self.requirements_service.delete_requirement(requirement_id)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error deleting requirement: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_requirements(self) -> Dict[str, Any]:
        """Export requirements to file"""
        try:
            # Get export parameters
            format = request.args.get('format', 'excel')
            filters = self._get_filter_parameters()
            
            # Load and filter requirements
            requirements_data = self.requirements_service.load_requirements_from_files()
            filtered_requirements = self.requirements_service.filter_requirements(
                requirements_data, filters
            )
            
            # Export requirements
            filename = self.requirements_service.export_requirements(filtered_requirements, format)
            
            return {
                'success': True,
                'filename': filename,
                'count': len(filtered_requirements)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error exporting requirements: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def import_requirements(self) -> Dict[str, Any]:
        """Import requirements from file"""
        try:
            # Check if file was uploaded
            if 'file' not in request.files:
                return {
                    'success': False,
                    'error': 'No file uploaded'
                }
            
            file = request.files['file']
            if file.filename == '':
                return {
                    'success': False,
                    'error': 'No file selected'
                }
            
            # Save uploaded file temporarily
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                file.save(tmp_file.name)
                
                # Import requirements
                result = self.requirements_service.import_requirements(tmp_file.name)
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
                return result
            
        except Exception as e:
            current_app.logger.error(f"Error importing requirements: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_filter_parameters(self) -> Dict[str, Any]:
        """Get filter parameters from request"""
        return {
            'search': request.args.get('search', ''),
            'status': request.args.get('status', ''),
            'priority': request.args.get('priority', ''),
            'category': request.args.get('category', ''),
            'assignee': request.args.get('assignee', ''),
            'tags': request.args.get('tags', ''),
            'due_date_range': request.args.get('due_date_range', '')
        }
    
    def _get_filter_options(self, requirements_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Get available filter options"""
        all_requirements = []
        for file_data in requirements_data.values():
            all_requirements.extend(file_data)
        
        if not all_requirements:
            return {
                'statuses': [],
                'priorities': [],
                'categories': [],
                'assignees': [],
                'tags': []
            }
        
        # Extract unique values
        statuses = list(set(req.get('status', '') for req in all_requirements if req.get('status')))
        priorities = list(set(req.get('priority', '') for req in all_requirements if req.get('priority')))
        categories = list(set(req.get('category', '') for req in all_requirements if req.get('category')))
        assignees = list(set(req.get('assignee', '') for req in all_requirements if req.get('assignee')))
        
        # Extract tags
        all_tags = []
        for req in all_requirements:
            tags = req.get('tags', '')
            if tags:
                all_tags.extend([tag.strip() for tag in tags.split(',') if tag.strip()])
        tags = list(set(all_tags))
        
        return {
            'statuses': sorted(statuses),
            'priorities': sorted(priorities),
            'categories': sorted(categories),
            'assignees': sorted(assignees),
            'tags': sorted(tags)
        }
    
    def _sort_requirements(self, requirements: List[Dict[str, Any]], sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
        """Sort requirements"""
        reverse = sort_order.lower() == 'desc'
        
        # Handle special sorting cases
        if sort_by == 'due_date':
            def sort_key(req):
                due_date = req.get('due_date', '')
                if not due_date:
                    return '9999-12-31'  # Put items without due date at the end
                return due_date
        elif sort_by == 'priority':
            priority_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
            def sort_key(req):
                return priority_order.get(req.get('priority', 'Medium'), 2)
        else:
            def sort_key(req):
                return str(req.get(sort_by, '')).lower()
        
        return sorted(requirements, key=sort_key, reverse=reverse)
    
    def _get_related_requirements(self, requirement: Dict[str, Any], requirements_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Get related requirements based on tags, category, or assignee"""
        related = []
        current_tags = set(requirement.get('tags', '').split(',')) if requirement.get('tags') else set()
        current_category = requirement.get('category', '')
        current_assignee = requirement.get('assignee', '')
        
        for file_data in requirements_data.values():
            for req in file_data:
                if req.get('requirement_id') == requirement.get('requirement_id'):
                    continue  # Skip self
                
                # Check for relationships
                req_tags = set(req.get('tags', '').split(',')) if req.get('tags') else set()
                req_category = req.get('category', '')
                req_assignee = req.get('assignee', '')
                
                # Calculate similarity score
                score = 0
                if current_tags and req_tags:
                    score += len(current_tags.intersection(req_tags)) * 2
                if current_category and req_category == current_category:
                    score += 1
                if current_assignee and req_assignee == current_assignee:
                    score += 1
                
                if score > 0:
                    req['similarity_score'] = score
                    related.append(req)
        
        # Sort by similarity score
        related.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return related[:5]  # Return top 5 related requirements
    
    def auto_load_requirements(self) -> Dict[str, Any]:
        """Automatically load requirements from Excel files"""
        try:
            result = self.auto_loader.auto_load_requirements()
            
            if result['success']:
                current_app.logger.info(f"Auto-loaded {result['total_requirements']} requirements from {result['loaded_files']} files")
            else:
                current_app.logger.error(f"Auto-load failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in auto_load_requirements: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_requirements': 0,
                'requirements_data': {}
            }
    
    def refresh_requirements(self) -> Dict[str, Any]:
        """Refresh requirements by reloading all files"""
        try:
            result = self.auto_loader.refresh_requirements()
            
            if result['success']:
                current_app.logger.info(f"Refreshed {result['total_requirements']} requirements from {result['loaded_files']} files")
            else:
                current_app.logger.error(f"Refresh failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in refresh_requirements: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_requirements': 0,
                'requirements_data': {}
            }
    
    def get_requirements_directory_info(self) -> Dict[str, Any]:
        """Get information about the requirements directory"""
        try:
            return self.auto_loader.get_requirements_directory_info()
            
        except Exception as e:
            current_app.logger.error(f"Error getting directory info: {e}")
            return {
                'exists': False,
                'path': None,
                'file_count': 0,
                'files': [],
                'error': str(e)
            }
    
    def get_available_columns(self) -> Dict[str, Any]:
        """Get all available columns from loaded requirements"""
        try:
            result = self.auto_loader.get_available_columns()
            
            if result['success']:
                current_app.logger.info(f"Retrieved {result['total_columns']} columns from {result['total_requirements']} requirements")
            else:
                current_app.logger.error(f"Failed to get columns: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in get_available_columns: {e}")
            return {
                'success': False,
                'error': str(e),
                'columns': [],
                'column_values': {}
            }
    
    def filter_requirements_by_columns(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter requirements based on column values"""
        try:
            result = self.auto_loader.filter_requirements_by_columns(filters)
            
            if result['success']:
                current_app.logger.info(f"Filtered {result['total_filtered']} requirements from {result['total_original']} total")
            else:
                current_app.logger.error(f"Filtering failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in filter_requirements_by_columns: {e}")
            return {
                'success': False,
                'error': str(e),
                'filtered_requirements': [],
                'total_filtered': 0
            }
