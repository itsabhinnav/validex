"""
Dashboard Service for business logic
"""

from typing import Dict, Any, List
from collections import Counter

class DashboardService:
    """Service for dashboard business logic"""
    
    def __init__(self):
        pass
    
    def calculate_statistics(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate dashboard statistics"""
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
        
        return {
            'total_files': file_count,
            'total_cases': total_cases,
            'apps': list(apps),
            'test_types': list(test_types)
        }
    
    def calculate_app_stats(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, int]]:
        """Calculate application statistics"""
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
        
        return {
            'by_app': dict(app_counts),
            'by_test_type': dict(test_type_counts),
            'by_directory': dict(directory_counts)
        }
    
    def prepare_dashboard_data(self, test_cases_data: Dict[str, List[Dict[str, Any]]], 
                             db_status: Dict[str, Any], db_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare complete dashboard data"""
        stats = self.calculate_statistics(test_cases_data)
        app_stats = self.calculate_app_stats(test_cases_data)
        
        return {
            'stats': stats,
            'app_stats': app_stats,
            'test_cases_data': test_cases_data,
            'db_status': db_status,
            'db_stats': db_stats
        }

