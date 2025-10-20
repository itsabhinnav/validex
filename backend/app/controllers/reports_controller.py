"""
Reports Controller for MVC architecture
"""

from flask import render_template, redirect, url_for, session
from typing import Dict, Any
from .base_controller import BaseController

class ReportsController(BaseController):
    """Controller for reports functionality"""
    
    def __init__(self):
        super().__init__('reports')
    
    def _register_routes(self):
        """Register reports routes - not used in MVC structure"""
        pass
    
    def _handle_reports(self):
        """Handle reports page logic"""
        role = session.get('current_role')
        
        if not role:
            return redirect(url_for('main.role_selection'))
        
        test_cases_data = self.load_test_files()
        
        file_count = len(test_cases_data)
        total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
        
        return render_template('validex/reports.html', 
                             file_count=file_count, 
                             total_cases=total_cases,
                             current_role=role,
                             test_cases_data=test_cases_data)
