#!/usr/bin/env python3
"""
Team Distribution Build Script for Validex

This script creates an optimized portable package specifically designed
for team distribution with pre-configured settings and team-specific features.

Copyright 2025 Validex Project
"""

import os
import sys
import shutil
import json
import platform
from pathlib import Path
from datetime import datetime

def create_team_package():
    """Create optimized team distribution package"""
    print("=== Creating Team Distribution Package ===")
    
    # Create team package directory
    team_dir = Path('build/team_distribution')
    team_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy application files
    copy_application_files(team_dir)
    
    # Create team-specific configuration
    create_team_configuration(team_dir)
    
    # Create team launcher scripts
    create_team_launchers(team_dir)
    
    # Create team documentation
    create_team_documentation(team_dir)
    
    # Create team setup scripts
    create_team_setup_scripts(team_dir)
    
    print(f"Team distribution package created: {team_dir}")
    return True

def copy_application_files(team_dir):
    """Copy application files to team package"""
    print("Copying application files...")
    
    # Essential directories
    dirs_to_copy = ['app', 'config', 'core', 'data', 'scripts']
    
    for dir_name in dirs_to_copy:
        src = Path(dir_name)
        dst = team_dir / dir_name
        
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  Copied: {dir_name}")
    
    # Essential files
    files_to_copy = ['requirements.txt', 'run.py']
    
    for file_name in files_to_copy:
        src = Path(file_name)
        dst = team_dir / file_name
        
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Copied: {file_name}")

def create_team_configuration(team_dir):
    """Create team-specific configuration"""
    print("Creating team configuration...")
    
    # Team configuration template
    team_config = {
        "team": {
            "name": "Your Team Name",
            "artifactory_url": "https://your-company.jfrog.io/artifactory",
            "repository": "test-cases",
            "access_token": "YOUR_ARTIFACTORY_TOKEN",
            "enabled": True
        },
        "app": {
            "excel_files_dir": "data/excel_files",
            "reports_dir": "data/reports",
            "auto_refresh_interval": 30,
            "admin_enabled": False,
            "multiselect_threshold": 5
        },
        "network_security": {
            "restricted_mode": True,
            "allowed_domains": [
                "your-company.jfrog.io",
                "*.jfrog.io",
                "localhost",
                "127.0.0.1"
            ],
            "allowed_ips": [
                "127.0.0.1",
                "::1"
            ],
            "blocked_domains": []
        }
    }
    
    # Write team configuration
    config_file = team_dir / 'config' / 'team_config.json'
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(team_config, f, indent=2)
    
    print(f"  Created: {config_file}")

def create_team_launchers(team_dir):
    """Create team-specific launcher scripts"""
    print("Creating team launchers...")
    
    # Windows team launcher
    windows_launcher = '''@echo off
echo ========================================
echo    Validex Team Distribution
echo ========================================
echo.
echo Starting Validex for Team Use...
echo Server: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Set team-specific environment variables
set FLASK_HOST=127.0.0.1
set FLASK_DEBUG=false
set FLASK_ENV=production
set VALIDEX_TEAM_MODE=true

REM Start the application
python run.py

echo.
echo Validex stopped.
pause
'''
    
    with open(team_dir / 'start_team.bat', 'w', encoding='utf-8') as f:
        f.write(windows_launcher)
    
    # Linux/macOS team launcher
    unix_launcher = '''#!/bin/bash
echo "========================================"
echo "   Validex Team Distribution"
echo "========================================"
echo ""
echo "Starting Validex for Team Use..."
echo "Server: http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Set team-specific environment variables
export FLASK_HOST=127.0.0.1
export FLASK_DEBUG=false
export FLASK_ENV=production
export VALIDEX_TEAM_MODE=true

# Start the application
python run.py

echo ""
echo "Validex stopped."
'''
    
    with open(team_dir / 'start_team.sh', 'w', encoding='utf-8') as f:
        f.write(unix_launcher)
    
    # Make shell script executable
    if platform.system() != "Windows":
        os.chmod(team_dir / 'start_team.sh', 0o755)
    
    print("  Created team launchers")

def create_team_documentation(team_dir):
    """Create team-specific documentation"""
    print("Creating team documentation...")
    
    # Team README
    team_readme = '''# Validex Team Distribution

## 🎯 Team Setup Guide

### Quick Start
1. **Install Python 3.8+** (if not already installed)
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Configure Artifactory**: Edit `config/team_config.json`
4. **Start Application**: Run `start_team.bat` (Windows) or `./start_team.sh` (Unix)
5. **Access Application**: Open http://127.0.0.1:8000

## 🔧 Team Configuration

### Artifactory Setup
Edit `config/team_config.json`:
```json
{
  "team": {
    "name": "Your Team Name",
    "artifactory_url": "https://your-company.jfrog.io/artifactory",
    "repository": "test-cases",
    "access_token": "YOUR_ARTIFACTORY_TOKEN"
  }
}
```

### Network Security
- Application binds only to localhost (127.0.0.1)
- External access is blocked for security
- Only whitelisted domains can be accessed
- Artifactory integration is pre-configured

## 📊 Team Features

### Test Case Management
- ✅ **Excel File Processing**: Load test cases from Excel files
- ✅ **Database Management**: Local SQLite database
- ✅ **Search & Filter**: Advanced filtering capabilities
- ✅ **Export Functions**: Export test cases and reports

### Team Collaboration
- ✅ **Artifactory Integration**: Shared Excel file storage
- ✅ **Version Control**: Track file changes
- ✅ **Data Synchronization**: Sync with team repository
- ✅ **Report Sharing**: Export and share reports

### Security Features
- ✅ **Network Isolation**: Localhost-only access
- ✅ **Secure File Access**: Encrypted Artifactory connections
- ✅ **Data Privacy**: Local database storage
- ✅ **Access Control**: Team-based permissions

## 🚀 Usage Instructions

### 1. Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure team settings
# Edit config/team_config.json with your team's Artifactory details
```

### 2. Daily Usage
```bash
# Start the application
./start_team.sh  # Linux/macOS
start_team.bat   # Windows

# Access the application
# Open browser: http://127.0.0.1:8000
```

### 3. Team Collaboration
- **Shared Files**: Access team Excel files from Artifactory
- **Data Sync**: Download latest test cases
- **Report Export**: Share reports with team members
- **Configuration**: Use team-standard settings

## 🔒 Security Notes

### Network Security
- **Localhost Only**: Application cannot be accessed from other machines
- **No External Access**: Cannot be accessed from network
- **Firewall Friendly**: No inbound connections required
- **VPN Compatible**: Works in restricted network environments

### Data Security
- **Local Storage**: All data stored locally
- **Encrypted Connections**: Secure Artifactory access
- **No Cloud Dependencies**: No external data storage
- **Team Access**: Only team members can access shared files

## 🛠️ Troubleshooting

### Common Issues
1. **Python Not Found**: Install Python 3.8+ from python.org
2. **Dependencies Error**: Run `pip install -r requirements.txt`
3. **Port Already in Use**: Check if another instance is running
4. **Artifactory Connection**: Verify credentials in team_config.json

### Support
- Check the logs in `logs/` directory
- Review configuration in `config/team_config.json`
- Contact your team administrator for Artifactory access

## 📞 Team Support

For team-specific issues:
1. Check this documentation
2. Review configuration settings
3. Contact team administrator
4. Check team communication channels

---
**Team Distribution Version**: 1.0  
**Last Updated**: ''' + datetime.now().strftime('%Y-%m-%d') + '''  
**Team**: Your Team Name
'''
    
    with open(team_dir / 'TEAM_README.md', 'w', encoding='utf-8') as f:
        f.write(team_readme)
    
    print("  Created team documentation")

def create_team_setup_scripts(team_dir):
    """Create team setup and configuration scripts"""
    print("Creating team setup scripts...")
    
    # Team configuration script
    config_script = '''#!/usr/bin/env python3
"""
Team Configuration Script

This script helps configure Validex for team use.
"""

import json
import os
from pathlib import Path

def configure_team():
    """Configure team settings"""
    print("Validex Team Configuration")
    print("=" * 30)
    
    # Get team information
    team_name = input("Enter team name: ").strip()
    artifactory_url = input("Enter Artifactory URL: ").strip()
    repository = input("Enter repository name: ").strip()
    access_token = input("Enter Artifactory access token: ").strip()
    
    # Create configuration
    config = {
        "team": {
            "name": team_name,
            "artifactory_url": artifactory_url,
            "repository": repository,
            "access_token": access_token,
            "enabled": True
        }
    }
    
    # Write configuration
    config_file = Path("config/team_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\\nConfiguration saved to {config_file}")
    print("You can now start Validex with: ./start_team.sh")

if __name__ == '__main__':
    configure_team()
'''
    
    with open(team_dir / 'scripts' / 'configure_team.py', 'w', encoding='utf-8') as f:
        f.write(config_script)
    
    # Make script executable
    if platform.system() != "Windows":
        os.chmod(team_dir / 'scripts' / 'configure_team.py', 0o755)
    
    print("  Created team setup scripts")

def create_team_installer():
    """Create team installer script"""
    print("Creating team installer...")
    
    # Windows installer
    installer_content = '''@echo off
echo Validex Team Distribution Installer
echo ===================================
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\\Validex
echo Installing to: %INSTALL_DIR%

REM Create directory
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
xcopy /E /I /Y "build\\team_distribution\\*" "%INSTALL_DIR%\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Validex Team.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\start_team.bat'; $Shortcut.Save()"

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Run: %INSTALL_DIR%\\scripts\\configure_team.py
echo 2. Start: %INSTALL_DIR%\\start_team.bat
echo.
pause
'''
    
    with open('build/install_team.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("  Created team installer")

def main():
    """Main function"""
    print("Validex Team Distribution Builder")
    print("=" * 40)
    print()
    
    try:
        # Create team package
        if create_team_package():
            # Create team installer
            create_team_installer()
            
            print()
            print("Team Distribution Package Complete!")
            print()
            print("Package Location: build/team_distribution/")
            print("Installer: build/install_team.bat")
            print()
            print("To distribute to team:")
            print("1. Copy the 'build/team_distribution' folder")
            print("2. Or run 'build/install_team.bat' to install")
            print("3. Team members run 'scripts/configure_team.py'")
            print("4. Team members start with 'start_team.bat'")
            return True
        else:
            print("Team package creation failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
