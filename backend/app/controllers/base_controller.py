"""
Base Controller for MVC architecture
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
from typing import Dict, Any, Optional, List
from app import get_services

class BaseController:
    """Base controller class with common functionality"""
    
    def __init__(self, name: str, import_name: str = None):
        self.name = name
        self.blueprint = Blueprint(name, import_name or __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register routes - to be implemented by subclasses"""
        pass
    
    def get_services(self) -> Dict[str, Any]:
        """Get application services"""
        return get_services()
    
    def check_role(self, required_role: str = None) -> bool:
        """Check if user has required role"""
        current_role = session.get('current_role')
        if not current_role:
            return False
        if required_role and current_role != required_role:
            return False
        return True
    
    def redirect_to_role_selection(self):
        """Redirect to role selection if no role is set"""
        return redirect(url_for('main.role_selection'))
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database availability status"""
        try:
            services = self.get_services()
            db_service = services.get('db_service')
            
            if not db_service:
                return {
                    'available': False,
                    'error': 'Database service not initialized',
                    'status': 'Database service not available',
                    'fallback_mode': True
                }
            
            if not db_service.is_initialized():
                return {
                    'available': False,
                    'error': 'Database not properly initialized',
                    'status': 'Database not initialized',
                    'fallback_mode': True
                }
            
            return {
                'available': True,
                'status': 'Database is ready',
                'connection_info': db_service.get_connection_status(),
                'fallback_mode': False
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'status': f'Database error: {str(e)}',
                'fallback_mode': True
            }
    
    def load_test_files(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load test cases from local files - only from validex folder"""
        import os
        import pandas as pd
        from app.utils.path_resolver import path_resolver
        
        print("Loading local test files from validex folder...")
        test_dir = current_app.config.get('UPLOAD_FOLDER', str(path_resolver.get_test_files_path()))
        
        if not os.path.exists(test_dir):
            print(f"Test files directory {test_dir} not found")
            return {}
        
        # Only load from validex folder
        validex_dir = os.path.join(test_dir, 'validex')
        if not os.path.exists(validex_dir):
            print(f"Validex directory {validex_dir} not found")
            return {}
        
        test_cases_data = {}
        
        for root, dirs, files in os.walk(validex_dir):
            for file in files:
                # Only process Excel files and exclude requirements files
                if file.endswith(('.xlsx', '.xls')) and 'requirement' not in file.lower():
                    file_path = os.path.join(root, file)
                    try:
                        df = pd.read_excel(file_path)
                        if not df.empty:
                            print(f"Columns in {file}: {list(df.columns)}")
                            
                            if 'Test Case ID' not in df.columns:
                                id_columns = [col for col in df.columns if 'id' in col.lower() or 'case' in col.lower()]
                                if id_columns:
                                    df['Test Case ID'] = df[id_columns[0]]
                                else:
                                    df['Test Case ID'] = [f"TC-{i+1:03d}" for i in range(len(df))]
                            
                            if 'App' not in df.columns:
                                app_columns = [col for col in df.columns if 'app' in col.lower()]
                                if app_columns:
                                    df['App'] = df[app_columns[0]]
                                else:
                                    app_name = file.replace('.xlsx', '').replace('.xls', '').split('_')[0].title()
                                    df['App'] = app_name
                            
                            if 'Test Type' not in df.columns:
                                type_columns = [col for col in df.columns if 'type' in col.lower()]
                                if type_columns:
                                    df['Test Type'] = df[type_columns[0]]
                                else:
                                    test_type = file.replace('.xlsx', '').replace('.xls', '').split('_')[1] if '_' in file else 'Functional'
                                    df['Test Type'] = test_type.title()
                            
                            test_cases_data[file] = df.to_dict('records')
                            print(f"Loaded {len(df)} test cases from {file}")
                    except Exception as e:
                        print(f"Error loading {file}: {e}")
        
        print(f"Total files loaded: {len(test_cases_data)}")
        return test_cases_data

