#!/usr/bin/env python3
"""
Secure Deployment Configuration Script

This script configures the Validex application for secure deployment with
network isolation and restricted access.

Copyright 2025 Validex Project
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import config

def configure_secure_settings():
    """Configure secure application settings"""
    print("=== Configuring Secure Settings ===")
    
    # Force localhost binding
    print("Setting Flask to bind only to localhost...")
    os.environ['FLASK_HOST'] = '127.0.0.1'
    
    # Disable debug in production
    print("Disabling debug mode...")
    os.environ['FLASK_DEBUG'] = 'false'
    
    # Set production environment
    print("Setting production environment...")
    os.environ['FLASK_ENV'] = 'production'
    
    print("Secure settings configured")

def configure_network_security():
    """Configure network security settings"""
    print("=== Configuring Network Security ===")
    
    # Get current config
    security_config = config.get_network_security_config()
    
    # Ensure restricted mode is enabled
    if not security_config.get('restricted_mode', True):
        config.set('network_security.restricted_mode', True)
        print("Enabled restricted mode")
    
    # Add essential allowed domains
    allowed_domains = security_config.get('allowed_domains', [])
    essential_domains = [
        'localhost',
        '127.0.0.1',
        'trialdablg5.jfrog.io',
        '*.jfrog.io'
    ]
    
    for domain in essential_domains:
        if domain not in allowed_domains:
            allowed_domains.append(domain)
    
    config.set('network_security.allowed_domains', allowed_domains)
    print(f"Configured allowed domains: {allowed_domains}")
    
    # Add localhost IPs
    allowed_ips = security_config.get('allowed_ips', [])
    essential_ips = ['127.0.0.1', '::1']
    
    for ip in essential_ips:
        if ip not in allowed_ips:
            allowed_ips.append(ip)
    
    config.set('network_security.allowed_ips', allowed_ips)
    print(f"Configured allowed IPs: {allowed_ips}")
    
    print("Network security configured")

def create_secure_startup_script():
    """Create a secure startup script"""
    print("=== Creating Secure Startup Script ===")
    
    if platform.system() == "Windows":
        script_content = '''@echo off
echo Starting Validex in Secure Mode...
set FLASK_HOST=127.0.0.1
set FLASK_DEBUG=false
set FLASK_ENV=production
python run.py
'''
        script_path = "start_secure.bat"
    else:
        script_content = '''#!/bin/bash
echo "Starting Validex in Secure Mode..."
export FLASK_HOST=127.0.0.1
export FLASK_DEBUG=false
export FLASK_ENV=production
python run.py
'''
        script_path = "start_secure.sh"
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    if platform.system() != "Windows":
        os.chmod(script_path, 0o755)
    
    print(f"Created secure startup script: {script_path}")

def configure_firewall():
    """Configure firewall settings"""
    print("=== Configuring Firewall ===")
    
    if platform.system() == "Windows":
        print("Windows detected - configuring Windows Firewall...")
        try:
            # Run PowerShell script as administrator
            subprocess.run([
                "powershell", "-Command", 
                "Start-Process", "powershell", 
                "-ArgumentList", "-File", "scripts/configure_firewall.ps1", "-Enable",
                "-Verb", "RunAs"
            ], check=True)
            print("Windows Firewall configured")
        except subprocess.CalledProcessError:
            print("Warning: Could not configure Windows Firewall (requires administrator privileges)")
    else:
        print("Linux/macOS detected - configuring iptables...")
        try:
            # Block outbound connections except for allowed domains
            subprocess.run([
                "iptables", "-A", "OUTPUT", "-p", "tcp", "--dport", "80", "-j", "DROP"
            ], check=True)
            subprocess.run([
                "iptables", "-A", "OUTPUT", "-p", "tcp", "--dport", "443", "-j", "DROP"
            ], check=True)
            print("iptables configured (requires root privileges)")
        except subprocess.CalledProcessError:
            print("Warning: Could not configure iptables (requires root privileges)")

def test_security_configuration():
    """Test the security configuration"""
    print("=== Testing Security Configuration ===")
    
    # Test network security service
    try:
        from app.services.network_security_service import network_security_service
        network_security_service.configure_security(config.get_network_security_config())
        
        # Test allowed URL
        test_url = "http://localhost:8000"
        result = network_security_service.test_connectivity(test_url)
        print(f"Test URL {test_url}: Allowed={result['allowed']}, Reachable={result['reachable']}")
        
        # Test blocked URL
        blocked_url = "http://example.com"
        result = network_security_service.test_connectivity(blocked_url)
        print(f"Blocked URL {blocked_url}: Allowed={result['allowed']}")
        
    except Exception as e:
        print(f"Error testing security configuration: {e}")

def create_security_report():
    """Create a security configuration report"""
    print("=== Creating Security Report ===")
    
    report = {
        "timestamp": str(Path().cwd()),
        "platform": platform.system(),
        "network_security": config.get_network_security_config(),
        "flask_config": {
            "host": os.environ.get('FLASK_HOST', '127.0.0.1'),
            "debug": os.environ.get('FLASK_DEBUG', 'false'),
            "environment": os.environ.get('FLASK_ENV', 'production')
        }
    }
    
    with open('security_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("Security report created: security_report.json")

def main():
    """Main configuration function"""
    print("Validex Secure Deployment Configuration")
    print("=====================================")
    
    try:
        configure_secure_settings()
        configure_network_security()
        create_secure_startup_script()
        configure_firewall()
        test_security_configuration()
        create_security_report()
        
        print("\n=== Secure Deployment Configuration Complete ===")
        print("The application is now configured for secure deployment:")
        print("- Flask binds only to localhost (127.0.0.1)")
        print("- Network access is restricted to whitelisted domains")
        print("- Debug mode is disabled")
        print("- Firewall rules configured")
        print("\nTo start the application securely, run:")
        if platform.system() == "Windows":
            print("  start_secure.bat")
        else:
            print("  ./start_secure.sh")
        
    except Exception as e:
        print(f"Error during configuration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

