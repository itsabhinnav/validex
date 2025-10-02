#!/usr/bin/env python3
"""
Portable Build Script for Validex

This script creates a portable executable version of the Validex application
that can run without Python installed on the target system.

Copyright 2025 Validex Project
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required build dependencies are installed"""
    print("=== Checking Build Dependencies ===")
    
    required_packages = ['pyinstaller', 'auto-py-to-exe']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("✅ All dependencies installed")
    
    return True

def create_build_structure():
    """Create the build directory structure"""
    print("=== Creating Build Structure ===")
    
    build_dirs = [
        'build/portable',
        'build/dist',
        'build/temp',
        'build/portable/data',
        'build/portable/config',
        'build/portable/logs',
        'build/portable/scripts'
    ]
    
    for dir_path in build_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created: {dir_path}")
    
    return True

def copy_application_files():
    """Copy application files to build directory"""
    print("=== Copying Application Files ===")
    
    # Files to copy
    files_to_copy = [
        ('app', 'build/portable/app'),
        ('config', 'build/portable/config'),
        ('core', 'build/portable/core'),
        ('data', 'build/portable/data'),
        ('scripts', 'build/portable/scripts'),
        ('requirements.txt', 'build/portable/requirements.txt'),
        ('run.py', 'build/portable/run.py')
    ]
    
    for src, dst in files_to_copy:
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Copied directory: {src} -> {dst}")
        else:
            shutil.copy2(src, dst)
            print(f"Copied file: {src} -> {dst}")
    
    return True

def create_portable_launcher():
    """Create portable launcher scripts"""
    print("=== Creating Portable Launchers ===")
    
    # Windows batch file
    windows_launcher = '''@echo off
echo Starting Validex Portable...
echo.
echo Environment: Portable
echo Server: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Set environment variables for portable mode
set FLASK_HOST=127.0.0.1
set FLASK_DEBUG=false
set FLASK_ENV=production
set VALIDEX_PORTABLE=true

REM Start the application
python run.py

pause
'''
    
    with open('build/portable/start_validex.bat', 'w') as f:
        f.write(windows_launcher)
    
    # Linux/macOS shell script
    unix_launcher = '''#!/bin/bash
echo "Starting Validex Portable..."
echo ""
echo "Environment: Portable"
echo "Server: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set environment variables for portable mode
export FLASK_HOST=127.0.0.1
export FLASK_DEBUG=false
export FLASK_ENV=production
export VALIDEX_PORTABLE=true

# Start the application
python run.py
'''
    
    with open('build/portable/start_validex.sh', 'w') as f:
        f.write(unix_launcher)
    
    # Make shell script executable on Unix systems
    if platform.system() != "Windows":
        os.chmod('build/portable/start_validex.sh', 0o755)
    
    print("Created portable launchers")
    return True

def create_pyinstaller_spec():
    """Create PyInstaller spec file for building executable"""
    print("=== Creating PyInstaller Spec ===")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('config', 'config'),
        ('core', 'core'),
        ('data', 'data'),
        ('scripts', 'scripts'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'flask',
        'pandas',
        'openpyxl',
        'werkzeug',
        'jinja2',
        'click',
        'blinker',
        'itsdangerous',
        'markupsafe',
        'numpy',
        'python_dateutil',
        'pytz',
        'tzdata',
        'six',
        'et_xmlfile',
        'colorama',
        'sqlite3',
        'urllib',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Validex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app/static/icons/icon-192x192.png',
)
'''
    
    with open('build/Validex.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")
    return True

def build_executable():
    """Build the portable executable using PyInstaller"""
    print("=== Building Portable Executable ===")
    
    try:
        # Change to build directory
        os.chdir('build')
        
        # Run PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--onefile',
            '--windowed',
            '--name', 'Validex',
            '--icon', '../app/static/icons/icon-192x192.png',
            '--add-data', '../app;app',
            '--add-data', '../config;config',
            '--add-data', '../core;core',
            '--add-data', '../data;data',
            '--add-data', '../scripts;scripts',
            '--add-data', '../requirements.txt;.',
            '--hidden-import', 'flask',
            '--hidden-import', 'pandas',
            '--hidden-import', 'openpyxl',
            '--hidden-import', 'werkzeug',
            '--hidden-import', 'jinja2',
            '--hidden-import', 'click',
            '--hidden-import', 'blinker',
            '--hidden-import', 'itsdangerous',
            '--hidden-import', 'markupsafe',
            '--hidden-import', 'numpy',
            '--hidden-import', 'python_dateutil',
            '--hidden-import', 'pytz',
            '--hidden-import', 'tzdata',
            '--hidden-import', 'six',
            '--hidden-import', 'et_xmlfile',
            '--hidden-import', 'colorama',
            '--hidden-import', 'sqlite3',
            '--hidden-import', 'urllib',
            '--hidden-import', 'requests',
            '../run.py'
        ]
        
        print("Running PyInstaller...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully")
            return True
        else:
            print(f"❌ Build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False
    finally:
        # Return to project root
        os.chdir('..')

def create_portable_package():
    """Create the final portable package"""
    print("=== Creating Portable Package ===")
    
    package_dir = Path('build/portable')
    
    # Copy executable to portable directory
    exe_name = 'Validex.exe' if platform.system() == 'Windows' else 'Validex'
    exe_path = f'build/dist/{exe_name}'
    
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, package_dir / exe_name)
        print(f"Copied executable: {exe_name}")
    else:
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    # Create README for portable version
    readme_content = '''# Validex Portable

This is a portable version of the Validex Test Case Management System.

## Quick Start

### Windows
1. Double-click `start_validex.bat`
2. Open your browser and go to http://127.0.0.1:8000

### Linux/macOS
1. Run `./start_validex.sh`
2. Open your browser and go to http://127.0.0.1:8000

## Features

- ✅ No Python installation required
- ✅ All dependencies bundled
- ✅ Portable data directory
- ✅ Secure localhost-only binding
- ✅ Network security enabled
- ✅ Excel file processing
- ✅ Database auto-creation

## Configuration

- Edit `config/validex_config.json` to configure settings
- Add Excel files to `data/excel_files/` directory
- Database is automatically created in `data/db/`

## Security

- Application binds only to localhost (127.0.0.1)
- Network access is restricted to whitelisted domains
- All outbound connections are filtered

## Support

For issues or questions, check the documentation in the `docs/` directory.
'''
    
    with open(package_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    
    print("Created portable package")
    return True

def create_installer_script():
    """Create installer script for the portable version"""
    print("=== Creating Installer Script ===")
    
    # Windows installer
    installer_content = '''@echo off
echo Validex Portable Installer
echo ==========================
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\Validex
echo Installing to: %INSTALL_DIR%

REM Create directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
xcopy /E /I /Y "build\\portable\\*" "%INSTALL_DIR%\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Validex.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\start_validex.bat'; $Shortcut.Save()"

echo.
echo Installation complete!
echo.
echo To start Validex:
echo 1. Double-click the desktop shortcut, or
echo 2. Navigate to %INSTALL_DIR% and run start_validex.bat
echo.
pause
'''
    
    with open('build/install_portable.bat', 'w') as f:
        f.write(installer_content)
    
    print("Created installer script")
    return True

def main():
    """Main build process"""
    print("Validex Portable Build Script")
    print("=============================")
    print()
    
    try:
        # Check dependencies
        if not check_dependencies():
            return False
        
        # Create build structure
        if not create_build_structure():
            return False
        
        # Copy application files
        if not copy_application_files():
            return False
        
        # Create portable launchers
        if not create_portable_launcher():
            return False
        
        # Create PyInstaller spec
        if not create_pyinstaller_spec():
            return False
        
        # Build executable
        if not build_executable():
            return False
        
        # Create portable package
        if not create_portable_package():
            return False
        
        # Create installer script
        if not create_installer_script():
            return False
        
        print()
        print("=== Build Complete ===")
        print("Portable package created in: build/portable/")
        print("Executable location: build/dist/")
        print("Installer script: build/install_portable.bat")
        print()
        print("To distribute:")
        print("1. Copy the entire 'build/portable' folder")
        print("2. Or run 'build/install_portable.bat' to install")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

