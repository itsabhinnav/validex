#!/usr/bin/env python3
"""
Check App1 test types and files
"""

import os
import pandas as pd

def check_app1_test_types():
    """Check what test types App1 actually has"""
    
    print("Checking App1 Test Types")
    print("=" * 30)
    
    app1_dir = 'data/excel_files/validex/App1'
    
    # Check subdirectories
    subdirs = [d for d in os.listdir(app1_dir) if os.path.isdir(os.path.join(app1_dir, d))]
    print(f"App1 subdirectories: {subdirs}")
    
    # Check files in each subdirectory
    for subdir in subdirs:
        subdir_path = os.path.join(app1_dir, subdir)
        files = [f for f in os.listdir(subdir_path) if f.endswith('.xlsx')]
        print(f"\n{subdir}: {files}")
        
        # Check the content of each file
        for file in files:
            file_path = os.path.join(subdir_path, file)
            try:
                df = pd.read_excel(file_path)
                print(f"  {file}: {len(df)} test cases")
                print(f"    Columns: {df.columns.tolist()}")
                
                # Check if there's a 'type' column and its values
                if 'type' in df.columns:
                    unique_types = df['type'].unique()
                    print(f"    Type values: {unique_types}")
                elif 'Test Type' in df.columns:
                    unique_types = df['Test Type'].unique()
                    print(f"    Test Type values: {unique_types}")
                else:
                    print(f"    No type column found")
                    
            except Exception as e:
                print(f"  Error reading {file}: {e}")

if __name__ == "__main__":
    check_app1_test_types()

