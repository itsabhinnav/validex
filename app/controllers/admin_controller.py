"""
Admin Controller for MVC architecture
"""

from flask import render_template, redirect, url_for, session
from typing import Dict, Any
from .base_controller import BaseController

class AdminController(BaseController):
    """Controller for admin functionality"""
    
    def __init__(self):
        super().__init__('admin')
    
    def _register_routes(self):
        """Register admin routes - not used in MVC structure"""
        pass
    
    def _handle_admin(self):
        """Handle admin page logic"""
        role = session.get('current_role')
        
        from config.settings import config
        if not config.is_admin_enabled():
            return redirect(url_for('main.role_selection'))
        
        if role != 'admin':
            return redirect(url_for('main.role_selection'))
        
        test_cases_data = self.load_test_files()
        
        file_count = len(test_cases_data)
        total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
        
        return render_template('validex/admin.html', 
                             file_count=file_count, 
                             total_cases=total_cases,
                             current_role=session.get('current_role'),
                             test_cases_data=test_cases_data)
    
    def _handle_jfrog_config(self):
        """Handle JFrog configuration page"""
        role = session.get('current_role')
        
        from config.settings import config
        if not config.is_admin_enabled():
            return redirect(url_for('main.role_selection'))
        
        if role != 'admin':
            return redirect(url_for('main.role_selection'))
        
        jfrog_config = {
            'base_url': '',
            'username': '',
            'password': '',
            'repository': '',
            'enabled': False
        }
        
        return render_template('validex/jfrog_config.html', current_role=role, jfrog_config=jfrog_config)
    
    def _handle_sync_dashboard(self):
        """Handle sync dashboard page"""
        role = session.get('current_role')
        
        from config.settings import config
        if not config.is_admin_enabled():
            return redirect(url_for('main.role_selection'))
        
        if role != 'admin':
            return redirect(url_for('main.role_selection'))
        
        return render_template('validex/sync_dashboard.html', current_role=role)
