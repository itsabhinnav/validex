"""
Admin View for MVC architecture
"""

from typing import Dict, Any, List
from .base_view import BaseView

class AdminView(BaseView):
    """View for admin functionality"""
    
    def __init__(self):
        super().__init__()
    
    def render_admin(self, test_cases_data: Dict[str, List[Dict[str, Any]]], 
                    current_role: str) -> Dict[str, Any]:
        """Prepare admin view data"""
        file_count = len(test_cases_data)
        total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
        
        return {
            'file_count': file_count,
            'total_cases': total_cases,
            'current_role': current_role,
            'test_cases_data': test_cases_data
        }
    
    def render_jfrog_config(self, current_role: str) -> Dict[str, Any]:
        """Prepare JFrog configuration view data"""
        jfrog_config = {
            'base_url': '',
            'username': '',
            'password': '',
            'repository': '',
            'enabled': False
        }
        
        return {
            'current_role': current_role,
            'jfrog_config': jfrog_config
        }
    
    def render_sync_dashboard(self, current_role: str) -> Dict[str, Any]:
        """Prepare sync dashboard view data"""
        return {
            'current_role': current_role
        }

