"""
Dashboard View for MVC architecture
"""

from typing import Dict, Any, List
from .base_view import BaseView

class DashboardView(BaseView):
    """View for dashboard functionality"""
    
    def __init__(self):
        super().__init__()
    
    def render_dashboard(self, test_cases_data: Dict[str, List[Dict[str, Any]]], 
                        db_status: Dict[str, Any], db_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare dashboard view data"""
        dashboard_data = self.prepare_dashboard_data(test_cases_data)
        
        return {
            **dashboard_data,
            'db_status': db_status,
            'db_stats': db_stats
        }

