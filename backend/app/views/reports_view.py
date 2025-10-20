"""
Reports View for MVC architecture
"""

from typing import Dict, Any, List
from .base_view import BaseView

class ReportsView(BaseView):
    """View for reports functionality"""
    
    def __init__(self):
        super().__init__()
    
    def render_reports(self, test_cases_data: Dict[str, List[Dict[str, Any]]], 
                      current_role: str) -> Dict[str, Any]:
        """Prepare reports view data"""
        file_count = len(test_cases_data)
        total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
        
        return {
            'file_count': file_count,
            'total_cases': total_cases,
            'current_role': current_role,
            'test_cases_data': test_cases_data
        }

