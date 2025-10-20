"""
Design Phase Controller for Design Phase Management System
"""

from flask import request, session, current_app
from typing import Dict, Any, List, Optional
from app.services.design_phase_auto_loader import DesignPhaseAutoLoader

class DesignPhaseController:
    """Controller for design phase management"""
    
    def __init__(self):
        self.auto_loader = DesignPhaseAutoLoader()
    
    def get_design_phase_dashboard(self) -> Dict[str, Any]:
        """Get design phase dashboard data"""
        try:
            # Load design phase data
            phases_data = self.auto_loader.auto_load_design_phases()
            
            # Get summary statistics
            summary = self.auto_loader._generate_summary(phases_data.get('phases_data', {}))
            
            # Get recent design phases
            all_phases = []
            for file_data in phases_data.get('phases_data', {}).values():
                all_phases.extend(file_data)
            
            # Sort by phase order
            recent_phases = sorted(
                all_phases, 
                key=lambda x: x.get('phase_order', 0)
            )[:10]
            
            return {
                'summary': summary,
                'recent_phases': recent_phases,
                'phases_data': phases_data.get('phases_data', {}),
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting design phase dashboard: {e}")
            return {
                'summary': {
                    'total': 0,
                    'by_status': {},
                    'by_type': {},
                    'by_completion': {},
                    'by_file': {}
                },
                'recent_phases': [],
                'phases_data': {},
                'success': False,
                'error': str(e)
            }
    
    def auto_load_design_phases(self) -> Dict[str, Any]:
        """Automatically load design phases from Excel files"""
        try:
            result = self.auto_loader.auto_load_design_phases()
            
            if result['success']:
                current_app.logger.info(f"Auto-loaded {result['total_phases']} design phases from {result['loaded_files']} files")
            else:
                current_app.logger.error(f"Auto-load failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in auto_load_design_phases: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_phases': 0,
                'phases_data': {}
            }
    
    def refresh_design_phases(self) -> Dict[str, Any]:
        """Refresh design phases by reloading all files"""
        try:
            result = self.auto_loader.refresh_design_phases()
            
            if result['success']:
                current_app.logger.info(f"Refreshed {result['total_phases']} design phases from {result['loaded_files']} files")
            else:
                current_app.logger.error(f"Refresh failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in refresh_design_phases: {e}")
            return {
                'success': False,
                'error': str(e),
                'loaded_files': 0,
                'total_phases': 0,
                'phases_data': {}
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
        """Get all available columns from loaded design phases"""
        try:
            result = self.auto_loader.get_available_columns()
            
            if result['success']:
                current_app.logger.info(f"Retrieved {result['total_columns']} columns from {result['total_phases']} design phases")
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
    
    def filter_design_phases_by_columns(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Filter design phases based on column values"""
        try:
            result = self.auto_loader.filter_design_phases_by_columns(filters)
            
            if result['success']:
                current_app.logger.info(f"Filtered {result['total_filtered']} design phases from {result['total_original']} total")
            else:
                current_app.logger.error(f"Filtering failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in filter_design_phases_by_columns: {e}")
            return {
                'success': False,
                'error': str(e),
                'filtered_phases': [],
                'total_filtered': 0
            }
    
    def browse_design_phases(self) -> Dict[str, Any]:
        """Browse and filter design phases"""
        try:
            # Load design phase data
            phases_data = self.auto_loader.auto_load_design_phases()
            
            # Get filter parameters
            filters = self._get_filter_parameters()
            
            # Apply filters
            filtered_phases = self.auto_loader.filter_design_phases_by_columns(filters)
            
            if not filtered_phases['success']:
                return {
                    'phases': [],
                    'total_phases': 0,
                    'page': 1,
                    'per_page': 25,
                    'total_pages': 0,
                    'has_prev': False,
                    'has_next': False,
                    'filters': filters,
                    'filter_options': {},
                    'sort_by': 'phase_order',
                    'sort_order': 'asc',
                    'success': False,
                    'error': filtered_phases.get('error', 'Unknown error')
                }
            
            # Get sorting parameters
            sort_by = request.args.get('sort', 'phase_order')
            sort_order = request.args.get('order', 'asc')
            
            # Sort design phases
            filtered_phases['filtered_phases'] = self._sort_phases(
                filtered_phases['filtered_phases'], sort_by, sort_order
            )
            
            # Get pagination parameters
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 25))
            
            # Calculate pagination
            total_phases = len(filtered_phases['filtered_phases'])
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            paginated_phases = filtered_phases['filtered_phases'][start_index:end_index]
            
            # Calculate pagination info
            total_pages = (total_phases + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            # Get filter options
            filter_options = self._get_filter_options(phases_data.get('phases_data', {}))
            
            return {
                'phases': paginated_phases,
                'total_phases': total_phases,
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
            current_app.logger.error(f"Error browsing design phases: {e}")
            return {
                'phases': [],
                'total_phases': 0,
                'page': 1,
                'per_page': 25,
                'total_pages': 0,
                'has_prev': False,
                'has_next': False,
                'filters': {},
                'filter_options': {},
                'sort_by': 'phase_order',
                'sort_order': 'asc',
                'success': False,
                'error': str(e)
            }
    
    def get_design_phase_details(self, phase_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific design phase"""
        try:
            # Load design phase data
            phases_data = self.auto_loader.auto_load_design_phases()
            
            # Find the design phase
            phase = None
            for file_data in phases_data.get('phases_data', {}).values():
                for ph in file_data:
                    if ph.get('phase_id') == phase_id:
                        phase = ph
                        break
                if phase:
                    break
            
            if not phase:
                return {
                    'phase': None,
                    'success': False,
                    'error': f'Design phase {phase_id} not found'
                }
            
            # Get related design phases
            related_phases = self._get_related_phases(phase, phases_data.get('phases_data', {}))
            
            return {
                'phase': phase,
                'related_phases': related_phases,
                'success': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting design phase details: {e}")
            return {
                'phase': None,
                'related_phases': [],
                'success': False,
                'error': str(e)
            }
    
    def _get_filter_parameters(self) -> Dict[str, Any]:
        """Get filter parameters from request"""
        return {
            'search': request.args.get('search', ''),
            'phase_status': request.args.get('phase_status', ''),
            'phase_type': request.args.get('phase_type', ''),
            'completion': request.args.get('completion', ''),
            'tags': request.args.get('tags', ''),
            'start_date_range': request.args.get('start_date_range', '')
        }
    
    def _get_filter_options(self, phases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Get available filter options"""
        all_phases = []
        for file_data in phases_data.values():
            all_phases.extend(file_data)
        
        if not all_phases:
            return {
                'phase_statuses': [],
                'phase_types': [],
                'completions': [],
                'tags': []
            }
        
        # Extract unique values
        phase_statuses = list(set(ph.get('phase_status', '') for ph in all_phases if ph.get('phase_status')))
        phase_types = list(set(ph.get('phase_type', '') for ph in all_phases if ph.get('phase_type')))
        completions = list(set(ph.get('completion', '') for ph in all_phases if ph.get('completion')))
        
        # Extract tags
        all_tags = []
        for ph in all_phases:
            tags = ph.get('tags', '')
            if tags:
                all_tags.extend([tag.strip() for tag in tags.split(',') if tag.strip()])
        tags = list(set(all_tags))
        
        return {
            'phase_statuses': sorted(phase_statuses),
            'phase_types': sorted(phase_types),
            'completions': sorted(completions),
            'tags': sorted(tags)
        }
    
    def _sort_phases(self, phases: List[Dict[str, Any]], sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
        """Sort design phases"""
        reverse = sort_order.lower() == 'desc'
        
        # Handle special sorting cases
        if sort_by == 'phase_order':
            def sort_key(ph):
                return ph.get('phase_order', 0)
        elif sort_by == 'completion':
            def sort_key(ph):
                return ph.get('completion', 0)
        elif sort_by == 'start_date':
            def sort_key(ph):
                start_date = ph.get('start_date', '')
                if not start_date:
                    return '9999-12-31'  # Put items without start date at the end
                return start_date
        else:
            def sort_key(ph):
                return str(ph.get(sort_by, '')).lower()
        
        return sorted(phases, key=sort_key, reverse=reverse)
    
    def _get_related_phases(self, phase: Dict[str, Any], phases_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Get related design phases based on tags, phase_type, or dependencies"""
        related = []
        current_tags = set(phase.get('tags', '').split(',')) if phase.get('tags') else set()
        current_phase_type = phase.get('phase_type', '')
        current_dependencies = phase.get('dependencies', '')
        
        for file_data in phases_data.values():
            for ph in file_data:
                if ph.get('phase_id') == phase.get('phase_id'):
                    continue  # Skip self
                
                # Check for relationships
                ph_tags = set(ph.get('tags', '').split(',')) if ph.get('tags') else set()
                ph_phase_type = ph.get('phase_type', '')
                ph_dependencies = ph.get('dependencies', '')
                
                # Calculate similarity score
                score = 0
                if current_tags and ph_tags:
                    score += len(current_tags.intersection(ph_tags)) * 2
                if current_phase_type and ph_phase_type == current_phase_type:
                    score += 1
                if current_dependencies and ph_dependencies:
                    # Check if phases are related through dependencies
                    if phase.get('phase_id') in ph_dependencies or ph.get('phase_id') in current_dependencies:
                        score += 3
                
                if score > 0:
                    ph['similarity_score'] = score
                    related.append(ph)
        
        # Sort by similarity score
        related.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return related[:5]  # Return top 5 related design phases


