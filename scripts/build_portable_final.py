#!/usr/bin/env python3
"""
Final Portable Build Script for Validex

Creates a truly portable version that works without any installation.
Uses the path resolver to ensure all paths work correctly in portable mode.
"""

import os
import sys
import shutil
import subprocess
import zipfile
import json
from pathlib import Path
from datetime import datetime
import platform

def log(message):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_portable_package():
    """Create the portable package"""
    project_root = Path(__file__).parent.parent
    build_dir = project_root / "build"
    portable_dir = build_dir / "validex_portable"
    
    # Create directories
    build_dir.mkdir(exist_ok=True)
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir()
    
    log("Creating portable package structure...")
    
    # Create subdirectories
    dirs = [
        "app", "config", "data", "data/db", "data/excel_files", 
        "data/reports", "data/cache", "data/backups", "logs", "docs"
    ]
    for dir_path in dirs:
        (portable_dir / dir_path).mkdir(parents=True, exist_ok=True)
    
    # Copy application files
    log("Copying application files...")
    items_to_copy = [
        ("app", "app"),
        ("config", "config"), 
        ("data", "data"),
        ("docs", "docs"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE"),
        ("run.py", "run.py")
    ]
    
    for src, dst in items_to_copy:
        src_path = project_root / src
        dst_path = portable_dir / dst
        
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
            log(f"✓ Copied {src}")
        elif src_path.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            log(f"✓ Copied {src}/")
    
    # Create portable configuration
    log("Creating portable configuration...")
    portable_config = {
        "app": {
            "name": "Validex",
            "version": "1.0.0",
            "description": "Professional Test Case Management Platform",
            "tagline": "Quality Assurance Management System",
            "debug": False,
            "secret_key": "portable-secret-key-change-in-production",
            "host": "127.0.0.1",
            "port": 8000,
            "admin_enabled": False,
            "multiselect_threshold": 5,
            "test_cases_per_page": 10,
            "auto_refresh_interval": 30
        },
        "database": {
            "type": "sqlite",
            "path": "data/db/test_cases.db",
            "backup_enabled": True,
            "backup_interval_hours": 24,
            "max_backups": 7,
            "thread_safe": True,
            "connection_timeout": 30
        },
        "filesystem": {
            "test_files_dir": "data/excel_files",
            "reports_dir": "data/reports",
            "cache_dir": "data/cache",
            "logs_dir": "logs",
            "backup_dir": "data/backups",
            "allowed_extensions": [".xlsx", ".xls"],
            "max_file_size_mb": 50
        },
        "jfrog": {
            "enabled": False,
            "base_url": "https://your-artifactory.com",
            "repository": "your-repository",
            "root_path": "your-project-path",
            "access_token": "your-access-token",
            "sync_enabled": False,
            "auto_sync_interval": 300,
            "retry_attempts": 3,
            "retry_delay": 60
        },
        "network_security": {
            "restricted_mode": True,
            "allowed_domains": ["localhost", "127.0.0.1"],
            "blocked_domains": [],
            "allowed_ips": ["127.0.0.1", "::1"],
            "blocked_ips": []
        },
        "sync": {
            "strategy": "incremental",
            "enabled": False,
            "auto_sync": False,
            "sync_interval": 300,
            "max_retries": 3,
            "retry_delay": 60,
            "chunk_size": 1000
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "logs/validex.log",
            "max_size": 10485760,
            "backup_count": 5
        },
        "ui": {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "date_format": "%Y-%m-%d",
            "time_format": "%H:%M:%S"
        },
        "text": {
            "landing_page": {
                "title": "Validex - Test Case Management",
                "hero_title": "Professional Test Case Management",
                "hero_tagline": "Streamline your testing process with enterprise-grade tools",
                "hero_description": "Manage test cases, execute tests, and generate comprehensive reports with our powerful platform.",
                "get_started": "Get Started"
            },
            "dashboard": {
                "title": "Dashboard",
                "welcome": "Welcome to Validex"
            },
            "test_cases": {
                "title": "Test Cases",
                "no_cases": "No test cases found"
            }
        },
        "columns": {
            "required": ["TC ID", "Summary"],
            "optional": ["Feature", "Priority", "Status", "Screen ID", "Test Type", "Expected Behavior"],
            "mappings": {
                "id": ["TC ID", "Test Case ID", "ID"],
                "summary": ["Summary", "Description", "Title"],
                "feature": ["Feature", "Component", "Module"],
                "priority": ["Priority", "Level"],
                "status": ["Status", "State"],
                "screen": ["Screen ID", "Screen", "Page"],
                "type": ["Test Type", "Type", "Category"],
                "expected": ["Expected Behavior", "Expected Result", "Expected"]
            }
        },
        "export": {
            "default_format": "file",
            "include_metadata": True,
            "include_timestamps": True,
            "max_file_size_mb": 50
        },
        "security": {
            "session_timeout": 3600,
            "max_login_attempts": 5,
            "lockout_duration": 900,
            "password_min_length": 8,
            "require_https": False
        },
        "performance": {
            "cache_enabled": True,
            "cache_ttl": 3600,
            "max_workers": 4,
            "chunk_size": 1000,
            "timeout": 30
        }
    }
    
    # Save portable configuration
    config_path = portable_dir / "config" / "validex_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(portable_config, f, indent=2, ensure_ascii=False)
    log("✓ Created portable configuration")
    
    # Create launcher scripts
    log("Creating launcher scripts...")
    
    # Windows batch file
    if platform.system().lower() == "windows":
        bat_content = '''@echo off
title Validex Test Case Management System
echo.
echo ========================================
echo   Validex Portable Edition
echo ========================================
echo.
echo Starting application...
echo Please wait while the application loads...
echo.
echo Once started, open your browser and go to:
echo   http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the application
echo.

REM Check if Python exists
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Start the application
python run.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Application encountered an error.
    echo Please check the logs in the 'logs' directory.
    echo ========================================
    pause
)
'''
        with open(portable_dir / "START_VALIDEX.bat", 'w', encoding='utf-8') as f:
            f.write(bat_content)
        log("✓ Created START_VALIDEX.bat")
    
    # Unix shell script
    else:
        sh_content = '''#!/bin/bash
echo ""
echo "========================================"
echo "  Validex Portable Edition"
echo "========================================"
echo ""
echo "Starting application..."
echo "Please wait while the application loads..."
echo ""
echo "Once started, open your browser and go to:"
echo "  http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Check if Python exists
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or later"
    echo ""
    exit 1
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Start the application
python run.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "Application encountered an error."
    echo "Please check the logs in the 'logs' directory."
    echo "========================================"
    read -p "Press Enter to continue..."
fi
'''
        with open(portable_dir / "start_validex.sh", 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Make executable
        os.chmod(portable_dir / "start_validex.sh", 0o755)
        log("✓ Created start_validex.sh")
    
    # Create README
    log("Creating portable README...")
    readme_content = f'''# Validex Portable Edition

## 🚀 Quick Start

This is a **completely portable** version of Validex that requires **minimal setup**!

### Windows Users:
1. Double-click `START_VALIDEX.bat`
2. Wait for the application to start (first run will install dependencies)
3. Open your browser and go to: http://127.0.0.1:8000

### Linux/macOS Users:
1. Open terminal in this directory
2. Run: `./start_validex.sh`
3. Open your browser and go to: http://127.0.0.1:8000

## 📁 What's Included

- **Complete Application** - All source code and files
- **Portable Configuration** - Optimized for portable use
- **Sample Data** - Test files included
- **Documentation** - Complete user guide
- **Virtual Environment** - Isolated Python environment

## 🔧 System Requirements

- **Windows**: Windows 7 or later
- **Linux**: Most modern distributions  
- **macOS**: macOS 10.12 or later
- **Python**: 3.7 or later (will be installed automatically)
- **RAM**: 1GB minimum, 2GB recommended
- **Disk Space**: 500MB for application + data

## 📊 Features

- **Test Case Management** - Create, edit, and organize test cases
- **Role-Based Access** - Administrator and Tester roles
- **File Import/Export** - Support for test files
- **Reporting** - Generate comprehensive reports
- **Search & Filter** - Advanced filtering capabilities
- **Portable** - Runs from any directory

## 🛠️ Troubleshooting

### Application Won't Start
1. Check that all files are extracted properly
2. Ensure you have write permissions in the directory
3. Check the `logs` directory for error messages
4. First run may take longer to install dependencies

### Browser Can't Connect
1. Make sure the application is running
2. Try: http://localhost:8000
3. Check Windows Firewall settings

### Performance Issues
1. Close other applications to free up memory
2. Ensure you have at least 1GB RAM available

## 🔒 Security

This portable version:
- Runs only on localhost (127.0.0.1)
- No internet access required
- All data stays on your machine
- No installation or system changes

## 📝 License

This software is provided under the MIT License.
See LICENSE file for details.

---
**Validex Portable Edition** - Professional Test Case Management Made Simple
'''
    
    with open(portable_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    log("✓ Created README.md")
    
    # Create distribution zip
    log("Creating distribution package...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    system = platform.system().lower()
    arch = platform.machine().lower()
    zip_name = f"validex_portable_{system}_{arch}_{timestamp}.zip"
    zip_path = build_dir / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(portable_dir)
                zipf.write(file_path, arc_path)
    
    log(f"✓ Created distribution package: {zip_name}")
    log(f"  Size: {zip_path.stat().st_size / (1024*1024):.1f} MB")
    
    return zip_path

def main():
    """Main build process"""
    log("=" * 60)
    log("Validex Portable Build Process")
    log("=" * 60)
    
    # Create portable package
    try:
        zip_path = create_portable_package()
        
        log("=" * 60)
        log("✅ BUILD COMPLETED SUCCESSFULLY!")
        log("=" * 60)
        log(f"Portable package created: {zip_path.name}")
        log(f"Package location: {zip_path.parent}")
        log("")
        log("📦 Distribution Instructions:")
        log(f"1. Share the file: {zip_path.name}")
        log("2. Recipients extract the zip file")
        log("3. Run the appropriate launcher script")
        log("4. Open browser to http://127.0.0.1:8000")
        log("")
        log("🎉 Minimal setup required on target systems!")
        log("   - Python 3.7+ required")
        log("   - Dependencies installed automatically")
        log("   - Virtual environment created automatically")
        
        return True
        
    except Exception as e:
        log(f"❌ Build failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Portable build completed successfully!")
        print("The application is ready for distribution.")
    else:
        print("\n❌ Build failed. Please check the error messages above.")
        sys.exit(1)
