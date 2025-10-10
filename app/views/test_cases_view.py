"""
Test Cases View for MVC architecture
"""

from typing import Dict, Any, List
from .base_view import BaseView

class TestCasesView(BaseView):
    """View for test cases functionality"""
    
    def __init__(self):
        super().__init__()
    
    def render_test_cases(self, test_cases: List[Dict[str, Any]], 
                         filter_options: Dict[str, List[str]], 
                         pagination_data: Dict[str, Any],
                         current_filters: Dict[str, Any],
                         dynamic_filters: Dict[str, Any],
                         current_role: str,
                         multiselect_threshold: int) -> Dict[str, Any]:
        """Prepare test cases view data"""
        return {
            'test_cases': test_cases,
            'apps': filter_options['apps'],
            'test_types': filter_options['test_types'],
            'priorities': filter_options['priorities'],
            'current_app_filter': current_filters.get('app_filter'),
            'current_test_type_filter': current_filters.get('test_type_filter'),
            'current_priority_filter': current_filters.get('priority_filter'),
            'current_search': current_filters.get('search_query'),
            'current_sort': current_filters.get('sort_by'),
            'current_order': current_filters.get('sort_order'),
            'current_role': current_role,
            'dynamic_filters': dynamic_filters,
            'multiselect_threshold': multiselect_threshold,
            **pagination_data
        }
    
    def render_execute_test(self, test_case: Dict[str, Any], current_role: str) -> Dict[str, Any]:
        """Prepare execute test view data"""
        return {
            'test_case': test_case,
            'current_role': current_role
        }
    
    def render_prepare_test_suite(self, test_cases: List[Dict[str, Any]], 
                                 filter_options: Dict[str, List[str]], 
                                 current_role: str,
                                 multiselect_threshold: int) -> Dict[str, Any]:
        """Prepare test suite view data"""
        return {
            'test_cases': test_cases,
            'apps': filter_options['apps'],
            'test_types': filter_options['test_types'],
            'priorities': filter_options['priorities'],
            'total_cases': len(test_cases),
            'current_role': current_role,
            'multiselect_threshold': multiselect_threshold
        }

