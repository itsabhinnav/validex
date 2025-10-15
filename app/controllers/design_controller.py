"""
Design Controller for Design Specifications Management System
"""

from flask import request, session, current_app
from typing import Dict, Any, List, Optional
from app.services.design_auto_loader import DesignAutoLoader

class DesignController:
    """Controller for design specifications management"""
    
    def __init__(self):
        self.auto_loader = DesignAutoLoader()
    
    def get_design_dashboard(self) -> Dict[str, Any]:
        """Get design specifications dashboard data"""
        try:
            # Load design specifications data
            designs_data = self.auto_loader.auto_load_designs()
            
            # Get summary statistics
            summary = self.auto_loader._generate_summary(designs_data.get('designs_data', {}))
            
            # Get recent design specifications
            all_designs = []
            for file_data in designs_data.get('designs_data', {}).values():
                all_designs.extend(file_data)
            
            # Sort by created date (most recent first)
            recent_designs = sorted(
                all_designs, 
                key=lambda x: x.get('created_date', ''), 
                reverse=True
            )[:10]
            
            return {
                'summary': summary,
                'recent_designs': recent_designs,
                'designs_data': designs_data.get('designs_data', {}),
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting design dashboard: {e}")
            return {
                'summary': {
                    'total': 0,
                    'by_status': {},
                    'by_priority': {},
                    'by_design_type': {},
                    'by_designer': {},
                    'by_file': {}
                },
                'recent_designs': [],
                'designs_data': {},
                'success': False,
                'error': str(e)
            }
    
    def auto_load_designs(self) -> Dict[str, Any]:
        """Automatically load design specifications from Excel files"""
        try:
            result = self.auto_loader.auto_load_designs()
            
            if result['success']:
                current_app.logger.info(f"Auto-loaded {result['total_designs']} design specifications from {result['loaded_files']} files")
            else:
                current_app.logger.error(f"Auto-load failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in auto_load_designs: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_designs': 0,
                'designs_data': {}
            }
    
    def refresh_designs(self) -> Dict[str, Any]:
        """Refresh design specifications by reloading all files"""
        try:
            result = self.auto_loader.refresh_designs()
            
            if result['success']:
                current_app.logger.info(f"Refreshed {result['total_designs']} design specifications from {result['loaded_files']} files")
            else:
                current_app.logger.error(f"Refresh failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in refresh_designs: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_designs': 0,
                'designs_data': {}
            }
    
    def get_design_directory_info(self) -> Dict[str, Any]:
        """Get information about the design directory"""
        try:
            return self.auto_loader.get_design_directory_info()
            
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
        """Get all available columns from loaded design specifications"""
        try:
            result = self.auto_loader.get_available_columns()
            
            if result['success']:
                current_app.logger.info(f"Retrieved {result['total_columns']} columns from {result['total_designs']} design specifications")
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
    
    def filter_designs_by_columns(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter design specifications based on column values"""
        try:
            result = self.auto_loader.filter_designs_by_columns(filters)
            
            if result['success']:
                current_app.logger.info(f"Filtered {result['total_filtered']} design specifications from {result['total_original']} total")
            else:
                current_app.logger.error(f"Filtering failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in filter_designs_by_columns: {e}")
            return {
                'success': False,
                'error': str(e),
                'filtered_designs': [],
                'total_filtered': 0
            }
    
    def browse_designs(self) -> Dict[str, Any]:
        """Browse and filter design specifications"""
        try:
            # Load design specifications data
            designs_data = self.auto_loader.auto_load_designs()
            
            # Get filter parameters
            filters = self._get_filter_parameters()
            
            # Apply filters
            filtered_designs = self.auto_loader.filter_designs_by_columns(filters)
            
            if not filtered_designs['success']:
                return {
                    'designs': [],
                    'total_designs': 0,
                    'page': 1,
                    'per_page': 25,
                    'total_pages': 0,
                    'has_prev': False,
                    'has_next': False,
                    'filters': filters,
                    'filter_options': {},
                    'sort_by': 'design_id',
                    'sort_order': 'asc',
                    'success': False,
                    'error': filtered_designs.get('error', 'Unknown error')
                }
            
            # Get sorting parameters
            sort_by = request.args.get('sort', 'design_id')
            sort_order = request.args.get('order', 'asc')
            
            # Sort design specifications
            filtered_designs['filtered_designs'] = self._sort_designs(
                filtered_designs['filtered_designs'], sort_by, sort_order
            )
            
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 25))
            
            # Calculate pagination
            total_designs = len(filtered_designs['filtered_designs'])
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_designs = filtered_designs['filtered_designs'][start_index:end_index]
            
            # Calculate pagination info
            total_pages = (total_designs + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            # Get filter options
            filter_options = self._get_filter_options(designs_data.get('designs_data', {}))
            
            return {
                'designs': paginated_designs,
                'total_designs': total_designs,
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
            current_app.logger.error(f"Error browsing design specifications: {e}")
            return {
                'designs': [],
                'total_designs': 0,
                'page': 1,
                'per_page': 25,
                'total_pages': 0,
                'has_prev': False,
                'has_next': False,
                'filters': {},
                'filter_options': {},
                'sort_by': 'design_id',
                'sort_order': 'asc',
                'success': False,
                'error': str(e)
            }
    
    def get_design_details(self, design_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific design specification"""
        try:
            # Load design specifications data
            designs_data = self.auto_loader.auto_load_designs()
            
            # Find the design specification
            design = None
            for file_data in designs_data.get('designs_data', {}).values():
                for des in file_data:
                    if des.get('design_id') == design_id:
                        design = des
                        break
                if design:
                    break
            
            if not design:
                return {
                    'design': None,
                    'success': False,
                    'error': f'Design specification {design_id} not found'
                }
            
            # Get related design specifications
            related_designs = self._get_related_designs(design, designs_data.get('designs_data', {}))
            
            return {
                'design': design,
                'related_designs': related_designs,
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting design details: {e}")
            return {
                'design': None,
                'related_designs': [],
                'success': False,
                'error': str(e)
            }
    
    def _get_filter_parameters(self) -> Dict[str, Any]:
        """Get filter parameters from request"""
        return {
            'search': request.args.get('search', ''),
            'status': request.args.get('status', ''),
            'priority': request.args.get('priority', ''),
            'design_type': request.args.get('design_type', ''),
            'designer': request.args.get('designer', ''),
            'tags': request.args.get('tags', ''),
            'due_date_range': request.args.get('due_date_range', '')
        }
    
    def _get_filter_options(self, designs_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Get available filter options"""
        all_designs = []
        for file_data in designs_data.values():
            all_designs.extend(file_data)
        
        if not all_designs:
            return {
                'statuses': [],
                'priorities': [],
                'design_types': [],
                'designers': [],
                'tags': []
            }
        
        # Extract unique values
        statuses = list(set(des.get('status', '') for des in all_designs if des.get('status')))
        priorities = list(set(des.get('priority', '') for des in all_designs if des.get('priority')))
        design_types = list(set(des.get('design_type', '') for des in all_designs if des.get('design_type')))
        designers = list(set(des.get('designer', '') for des in all_designs if des.get('designer')))
        
        # Extract tags
        all_tags = []
        for des in all_designs:
            tags = des.get('tags', '')
            if tags:
                all_tags.extend([tag.strip() for tag in tags.split(',') if tag.strip()])
        tags = list(set(all_tags))
        
        return {
            'statuses': sorted(statuses),
            'priorities': sorted(priorities),
            'design_types': sorted(design_types),
            'designers': sorted(designers),
            'tags': sorted(tags)
        }
    
    def _sort_designs(self, designs: List[Dict[str, Any]], sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
        """Sort design specifications"""
        reverse = sort_order.lower() == 'desc'
        
        # Handle special sorting cases
        if sort_by == 'due_date':
            def sort_key(des):
                due_date = des.get('due_date', '')
                if not due_date:
                    return '9999-12-31'  # Put items without due date at the end
                return due_date
        elif sort_by == 'priority':
            priority_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
            def sort_key(des):
                return priority_order.get(des.get('priority', 'Medium'), 2)
        else:
            def sort_key(des):
                return str(des.get(sort_by, '')).lower()
        
        return sorted(designs, key=sort_key, reverse=reverse)
    
    def _get_related_designs(self, design: Dict[str, Any], designs_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Get related design specifications based on tags, design_type, or designer"""
        related = []
        current_tags = set(design.get('tags', '').split(',')) if design.get('tags') else set()
        current_design_type = design.get('design_type', '')
        current_designer = design.get('designer', '')
        
        for file_data in designs_data.values():
            for des in file_data:
                if des.get('design_id') == design.get('design_id'):
                    continue  # Skip self
                
                # Check for relationships
                des_tags = set(des.get('tags', '').split(',')) if des.get('tags') else set()
                des_design_type = des.get('design_type', '')
                des_designer = des.get('designer', '')
                
                # Calculate similarity score
                score = 0
                if current_tags and des_tags:
                    score += len(current_tags.intersection(des_tags)) * 2
                if current_design_type and des_design_type == current_design_type:
                    score += 1
                if current_designer and des_designer == current_designer:
                    score += 1
                
                if score > 0:
                    des['similarity_score'] = score
                    related.append(des)
        
        # Sort by similarity score
        related.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return related[:5]  # Return top 5 related design specifications


