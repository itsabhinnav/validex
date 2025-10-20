#!/usr/bin/env python3
"""
Validex Manager - Unified Script for All Operations
Combines all build, configuration, and management scripts into one tool
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
import platform
import logging

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ValidexManager:
    """Unified manager for all Validex operations"""
    
    def __init__(self):
        self.project_root = project_root
        self.scripts_dir = self.project_root / 'scripts'
        self.build_dir = self.project_root / 'build'
        self.data_dir = self.project_root / 'data'
        self.config_dir = self.project_root / 'config'
        
        # Setup logging
        log_dir = self.project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_dir / 'validex_manager.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message, level='info'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == 'error':
            self.logger.error(message)
            print(f"[{timestamp}] ERROR: {message}")
        elif level == 'warning':
            self.logger.warning(message)
            print(f"[{timestamp}] WARNING: {message}")
        else:
            self.logger.info(message)
            print(f"[{timestamp}] {message}")
    
    def ensure_directories(self):
        """Ensure required directories exist"""
        dirs = [
            self.build_dir,
            self.data_dir / 'excel_files' / 'validex',
            self.data_dir / 'excel_files' / 'requirements',
            self.data_dir / 'db',
            self.data_dir / 'reports',
            self.project_root / 'logs'
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def run_dynamic_config_analysis(self):
        """Run dynamic configuration analysis"""
        self.log("Starting dynamic configuration analysis...")
        
        try:
            from app.services.dynamic_config_service import DynamicConfigService
            
            service = DynamicConfigService()
            results = service.run_full_analysis()
            
            if results['success']:
                self.log("Dynamic configuration analysis completed successfully!")
                
                for app_name, analysis in results['analysis_results'].items():
                    if analysis['total_files'] > 0:
                        self.log(f"{app_name.upper()}: {analysis['total_files']} files, {analysis['total_columns']} columns")
                        self.log(f"  Required: {len(analysis['required_columns'])} columns")
                        self.log(f"  Optional: {len(analysis['optional_columns'])} columns")
                    else:
                        self.log(f"{app_name.upper()}: No Excel files found")
                
                return True
            else:
                self.log("Dynamic configuration analysis failed!", 'error')
                return False
                
        except Exception as e:
            self.log(f"Error during dynamic configuration analysis: {e}", 'error')
            return False
    
    def create_sample_requirements(self):
        """Create sample requirements Excel file"""
        self.log("Creating sample requirements file...")
        
        try:
            requirements_data = {
                'Requirement ID': ['REQ-001', 'REQ-002', 'REQ-003', 'REQ-004', 'REQ-005', 'REQ-006'],
                'Screen ID': ['SCR-001', 'SCR-002', 'SCR-003', 'SCR-004', 'SCR-005', 'SCR-006'],
                'Description': [
                    'User Authentication System',
                    'Payment Gateway Integration', 
                    'API Documentation Standards',
                    'Database Schema Design',
                    'Security Requirements',
                    'User Interface Guidelines'
                ],
                'Given': [
                    'User wants to access the system',
                    'User needs to process payments',
                    'Developers need API documentation',
                    'System needs data storage',
                    'System needs security measures',
                    'Users need intuitive interface'
                ],
                'When': [
                    'User enters credentials',
                    'User initiates payment',
                    'Developer accesses API',
                    'System stores data',
                    'System validates access',
                    'User interacts with UI'
                ],
                'Then': [
                    'System authenticates user',
                    'Payment is processed',
                    'Documentation is available',
                    'Data is stored securely',
                    'Access is granted/denied',
                    'Interface responds appropriately'
                ],
                'Priority': ['High', 'Medium', 'Low', 'High', 'Critical', 'Medium'],
                'Status': ['Draft', 'Review', 'Approved', 'In Progress', 'Testing', 'Complete'],
                'Category': ['Security', 'Payment', 'Documentation', 'Database', 'Security', 'UI/UX'],
                'Assignee': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Charlie Davis', 'Diana Lee'],
                'Created Date': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20'],
                'Due Date': ['2024-02-15', '2024-02-16', '2024-02-17', '2024-02-18', '2024-02-19', '2024-02-20'],
                'Tags': ['auth,security', 'payment,integration', 'docs,api', 'database,schema', 'security,access', 'ui,ux']
            }
            
            df = pd.DataFrame(requirements_data)
            output_path = self.data_dir / 'excel_files' / 'requirements' / 'sample_requirements.xlsx'
            df.to_excel(output_path, index=False)
            
            self.log(f"Sample requirements file created: {output_path}")
            return True
            
        except Exception as e:
            self.log(f"Error creating sample requirements: {e}", 'error')
            return False
    
    def build_portable(self):
        """Build portable distribution"""
        self.log("Building portable distribution...")
        
        try:
            from scripts.build.build_portable_final import main as build_portable_main
            result = build_portable_main()
            
            if result == 0:
                self.log("Portable distribution built successfully!")
                return True
            else:
                self.log("Portable distribution build failed!", 'error')
                return False
                
        except Exception as e:
            self.log(f"Error building portable distribution: {e}", 'error')
            return False
    
    def build_executable(self):
        """Build executable distribution"""
        self.log("Building executable distribution...")
        
        try:
            from scripts.build.build_executable import main as build_executable_main
            result = build_executable_main()
            
            if result == 0:
                self.log("Executable distribution built successfully!")
                return True
            else:
                self.log("Executable distribution build failed!", 'error')
                return False
                
        except Exception as e:
            self.log(f"Error building executable distribution: {e}", 'error')
            return False
    
    def build_desktop_app(self):
        """Build desktop app distribution"""
        self.log("Building desktop app distribution...")
        
        try:
            from scripts.build.build_desktop_app import main as build_desktop_main
            result = build_desktop_main()
            
            if result == 0:
                self.log("Desktop app distribution built successfully!")
                return True
            else:
                self.log("Desktop app distribution build failed!", 'error')
                return False
                
        except Exception as e:
            self.log(f"Error building desktop app distribution: {e}", 'error')
            return False
    
    def build_all_distributions(self):
        """Build all distribution types"""
        self.log("Building all distributions...")
        
        results = {
            'portable': self.build_portable(),
            'executable': self.build_executable(),
            'desktop': self.build_desktop_app()
        }
        
        success_count = sum(results.values())
        total_count = len(results)
        
        self.log(f"Build results: {success_count}/{total_count} distributions built successfully")
        
        for dist_type, success in results.items():
            status = "[OK]" if success else "[FAIL]"
            self.log(f"  {status} {dist_type.title()} distribution")
        
        return success_count == total_count
    
    def get_app_status(self):
        """Get current application status"""
        self.log("Checking application status...")
        
        try:
            from app.services.dynamic_config_service import DynamicConfigService
            
            service = DynamicConfigService()
            status = service.get_app_status()
            
            self.log("Application Status:")
            for app_name, app_status in status.items():
                if app_status['enabled']:
                    self.log(f"  [OK] {app_name.upper()}: {app_status['file_count']} Excel files")
                    for file in app_status['files']:
                        self.log(f"    - {file}")
                else:
                    self.log(f"  [SKIP] {app_name.upper()}: Directory not found")
            
            return status
            
        except Exception as e:
            self.log(f"Error getting app status: {e}", 'error')
            return None
    
    def clean_build(self):
        """Clean build directory"""
        self.log("Cleaning build directory...")
        
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                self.log("Build directory cleaned")
            else:
                self.log("Build directory does not exist")
            return True
            
        except Exception as e:
            self.log(f"Error cleaning build directory: {e}", 'error')
            return False
    
    def show_help(self):
        """Show help information"""
        help_text = """
Validex Manager - Unified Script for All Operations

USAGE:
    python validex_manager.py <command> [options]

COMMANDS:
    config          Run dynamic configuration analysis
    sample          Create sample requirements file
    build           Build distributions
    status          Show application status
    clean           Clean build directory
    help            Show this help message

BUILD OPTIONS:
    --portable      Build portable distribution only
    --executable    Build executable distribution only
    --desktop       Build desktop app distribution only
    --all           Build all distributions (default)

EXAMPLES:
    python validex_manager.py config
    python validex_manager.py sample
    python validex_manager.py build --portable
    python validex_manager.py build --all
    python validex_manager.py status
    python validex_manager.py clean

FEATURES:
    - Dynamic configuration analysis
    - Sample data generation
    - Multiple distribution builds
    - Application status monitoring
    - Build directory management
        """
        print(help_text)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validex Manager - Unified Script for All Operations',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', 
                       choices=['config', 'sample', 'build', 'status', 'clean', 'help'],
                       help='Command to execute')
    
    parser.add_argument('--portable', action='store_true',
                       help='Build portable distribution only')
    parser.add_argument('--executable', action='store_true',
                       help='Build executable distribution only')
    parser.add_argument('--desktop', action='store_true',
                       help='Build desktop app distribution only')
    parser.add_argument('--all', action='store_true',
                       help='Build all distributions')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = ValidexManager()
    manager.ensure_directories()
    
    # Execute command
    if args.command == 'help':
        manager.show_help()
        return 0
    
    elif args.command == 'config':
        success = manager.run_dynamic_config_analysis()
        return 0 if success else 1
    
    elif args.command == 'sample':
        success = manager.create_sample_requirements()
        return 0 if success else 1
    
    elif args.command == 'build':
        if args.portable:
            success = manager.build_portable()
        elif args.executable:
            success = manager.build_executable()
        elif args.desktop:
            success = manager.build_desktop_app()
        else:  # --all or default
            success = manager.build_all_distributions()
        
        return 0 if success else 1
    
    elif args.command == 'status':
        status = manager.get_app_status()
        return 0 if status else 1
    
    elif args.command == 'clean':
        success = manager.clean_build()
        return 0 if success else 1
    
    else:
        manager.log(f"Unknown command: {args.command}", 'error')
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
