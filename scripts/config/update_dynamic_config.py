#!/usr/bin/env python3
"""
Dynamic Configuration Update Script
Analyzes Excel files and updates configuration automatically
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.dynamic_config_service import DynamicConfigService

def main():
    """Main function to run dynamic configuration update"""
    print("Starting Dynamic Configuration Analysis...")
    print("=" * 50)
    
    try:
        # Initialize service
        service = DynamicConfigService()
        
        # Get current app status
        print("Checking current app status...")
        status = service.get_app_status()
        
        for app_name, app_status in status.items():
            if app_status['enabled']:
                print(f"[OK] {app_name.upper()}: {app_status['file_count']} Excel files found")
                for file in app_status['files']:
                    print(f"   - {file}")
            else:
                print(f"[SKIP] {app_name.upper()}: Directory not found")
        
        print("\nAnalyzing Excel files...")
        
        # Run full analysis
        results = service.run_full_analysis()
        
        if results['success']:
            print("[SUCCESS] Analysis completed successfully!")
            print("\nAnalysis Results:")
            print("-" * 30)
            
            for app_name, analysis in results['analysis_results'].items():
                if analysis['total_files'] > 0:
                    print(f"\n{app_name.upper()}:")
                    print(f"   Files analyzed: {analysis['total_files']}")
                    print(f"   Total columns: {analysis['total_columns']}")
                    print(f"   Required columns: {len(analysis['required_columns'])}")
                    print(f"   Optional columns: {len(analysis['optional_columns'])}")
                    
                    if analysis['required_columns']:
                        print(f"   Required: {', '.join(analysis['required_columns'])}")
                    
                    if analysis['optional_columns']:
                        print(f"   Optional: {', '.join(analysis['optional_columns'])}")
                else:
                    print(f"\n[WARNING] {app_name.upper()}: No Excel files found")
            
            print(f"\nAnalysis completed at: {results['timestamp']}")
            print("\n[SUCCESS] Configuration files have been updated!")
            print("You can now restart the application to use the new configuration.")
            
        else:
            print("[ERROR] Analysis failed!")
            return 1
            
    except Exception as e:
        print(f"[ERROR] Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
