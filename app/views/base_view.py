"""
Base View for MVC architecture
"""

from typing import Dict, Any, List, Optional
from collections import Counter

class BaseView:
    """Base view class with common functionality"""
    
    def __init__(self):
        pass
    
    def prepare_dashboard_data(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Prepare dashboard data from test cases"""
        file_count = len(test_cases_data)
        total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
        
        apps = set()
        test_types = set()
        
        for file_data in test_cases_data.values():
            for case in file_data:
                if 'App' in case:
                    apps.add(case['App'])
                if 'Test Type' in case:
                    test_types.add(case['Test Type'])
        
        app_counts = Counter()
        test_type_counts = Counter()
        directory_counts = Counter()
        
        for file_data in test_cases_data.values():
            for case in file_data:
                if 'App' in case:
                    app_counts[case['App']] += 1
                if 'Test Type' in case:
                    test_type_counts[case['Test Type']] += 1
                if 'File' in case:
                    directory = case['File'].split('/')[0] if '/' in case['File'] else 'root'
                    directory_counts[directory] += 1
        
        app_stats = {
            'by_app': dict(app_counts),
            'by_test_type': dict(test_type_counts),
            'by_directory': dict(directory_counts)
        }
        
        stats = {
            'total_files': file_count,
            'total_cases': total_cases,
            'apps': list(apps),
            'test_types': list(test_types)
        }
        
        return {
            'stats': stats,
            'app_stats': app_stats,
            'test_cases_data': test_cases_data
        }
    
    def prepare_filter_options(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Prepare filter options from test cases data"""
        apps = set()
        test_types = set()
        priorities = set()
        
        for file_data in test_cases_data.values():
            for case in file_data:
                if 'App' in case:
                    apps.add(case['App'])
                if 'Test Type' in case:
                    test_types.add(case['Test Type'])
                if 'Priority' in case:
                    priorities.add(case['Priority'])
        
        return {
            'apps': sorted(apps),
            'test_types': sorted(test_types),
            'priorities': sorted(priorities)
        }
    
    def prepare_pagination_data(self, total_items: int, page: int, per_page: int) -> Dict[str, Any]:
        """Prepare pagination data"""
        total_pages = (total_items + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return {
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next
        }

