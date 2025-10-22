"""
Dashboard Controller for MVC architecture
"""

from flask import render_template, redirect, url_for, session
from typing import Dict, Any
from collections import Counter
from .base_controller import BaseController
from app.services.dashboard_service import DashboardService
from app.views.dashboard_view import DashboardView

class DashboardController(BaseController):
    """Controller for dashboard functionality"""
    
    def __init__(self):
        super().__init__('dashboard')
        self.dashboard_service = DashboardService()
        self.dashboard_view = DashboardView()
    
    def _register_routes(self):
        """Register dashboard routes - not used in MVC structure"""
        pass
    
    def _handle_dashboard(self):
        """Handle dashboard page logic"""
        role = session.get('current_role')
        if not role:
            return redirect('/')
        
        db_status = self.get_database_status()
        
        test_cases_data = self.load_test_files()
        
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
        
        db_stats = {}
        if db_status.get('available', False):
            try:
                services = self.get_services()
                db_service = services.get('db_service')
                if db_service:
                    db_stats = db_service.get_safe_statistics()
            except Exception as e:
                print(f"Error getting database statistics: {e}")
                db_stats = {}
        
        return render_template('validex/dashboard.html', 
                             stats=stats, 
                             total_cases=total_cases,
                             file_count=file_count,
                             test_cases_data=test_cases_data, 
                             app_stats=app_stats,
                             db_status=db_status,
                             db_stats=db_stats)
