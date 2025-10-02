#!/usr/bin/env python3
"""
Simple Portable Build Script for Validex

This script creates a simple portable version of the Validex application.

Copyright 2025 Validex Project
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def create_portable_package():
    """Create a simple portable package"""
    print("=== Creating Portable Package ===")
    
    # Create portable directory
    portable_dir = Path('build/portable')
    portable_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        'app',
        'config', 
        'core',
        'data',
        'scripts',
        'requirements.txt',
        'run.py'
    ]
    
    for item in files_to_copy:
        src = Path(item)
        dst = portable_dir / item
        
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Copied directory: {item}")
        else:
            shutil.copy2(src, dst)
            print(f"Copied file: {item}")
    
    # Create launcher scripts
    create_launcher_scripts(portable_dir)
    
    # Create README
    create_readme(portable_dir)
    
    print(f"✅ Portable package created in: {portable_dir}")
    return True

def create_launcher_scripts(portable_dir):
    """Create launcher scripts for different platforms"""
    
    # Windows launcher
    windows_launcher = '''@echo off
echo Starting Validex Portable...
echo Server: http://127.0.0.1:8000
echo Press Ctrl+C to stop
echo.

set FLASK_HOST=127.0.0.1
set FLASK_DEBUG=false
set FLASK_ENV=production

python run.py
pause
'''
    
    with open(portable_dir / 'start_validex.bat', 'w') as f:
        f.write(windows_launcher)
    
    # Linux/macOS launcher
    unix_launcher = '''#!/bin/bash
echo "Starting Validex Portable..."
echo "Server: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop"
echo ""

export FLASK_HOST=127.0.0.1
export FLASK_DEBUG=false
export FLASK_ENV=production

python run.py
'''
    
    with open(portable_dir / 'start_validex.sh', 'w') as f:
        f.write(unix_launcher)
    
    # Make shell script executable
    if platform.system() != "Windows":
        os.chmod(portable_dir / 'start_validex.sh', 0o755)
    
    print("Created launcher scripts")

def create_readme(portable_dir):
    """Create README for portable version"""
    
    readme_content = '''# Validex Portable

## Quick Start

### Windows
1. Install Python 3.8+ if not already installed
2. Run: `pip install -r requirements.txt`
3. Double-click `start_validex.bat`
4. Open browser: http://127.0.0.1:8000

### Linux/macOS
1. Install Python 3.8+ if not already installed
2. Run: `pip install -r requirements.txt`
3. Run: `./start_validex.sh`
4. Open browser: http://127.0.0.1:8000

## Features
- ✅ Test case management
- ✅ Excel file processing
- ✅ Database auto-creation
- ✅ Secure localhost binding
- ✅ Network security
- ✅ JIRA-style UI

## Configuration
- Edit `config/validex_config.json` for settings
- Add Excel files to `data/excel_files/`
- Database: `data/db/test_cases.db`

## Security
- Binds only to localhost (127.0.0.1)
- Network access restricted to whitelisted domains
- No external network access by default
'''
    
    with open(portable_dir / 'README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Created README")

def main():
    """Main function"""
    print("Validex Simple Portable Build")
    print("=============================")
    print()
    
    try:
        # Create portable package
        if create_portable_package():
            print()
            print("Build Complete!")
            print("Portable package: build/portable/")
            print()
            print("To distribute:")
            print("1. Copy the 'build/portable' folder")
            print("2. Ensure Python 3.8+ is installed on target system")
            print("3. Run 'pip install -r requirements.txt'")
            print("4. Run the appropriate launcher script")
            return True
        else:
            print("Build failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
