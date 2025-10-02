#!/usr/bin/env python3
"""
Network Security Configuration Script

This script allows you to configure network security settings for the Validex application.
It manages the whitelist of allowed domains and IPs, and can test connectivity.

Copyright 2025 Validex Project
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import config
from app.services.network_security_service import network_security_service

def show_current_config():
    """Display current network security configuration"""
    print("=== Current Network Security Configuration ===")
    security_config = config.get_network_security_config()
    
    print(f"Restricted Mode: {security_config.get('restricted_mode', True)}")
    print(f"Allowed Domains: {security_config.get('allowed_domains', [])}")
    print(f"Allowed IPs: {security_config.get('allowed_ips', [])}")
    print(f"Blocked Domains: {security_config.get('blocked_domains', [])}")
    print()

def add_allowed_domain(domain):
    """Add a domain to the allowed list"""
    current_domains = config.get_allowed_domains()
    if domain not in current_domains:
        current_domains.append(domain)
        config.set('network_security.allowed_domains', current_domains)
        print(f"Added domain to whitelist: {domain}")
    else:
        print(f"Domain already in whitelist: {domain}")

def remove_allowed_domain(domain):
    """Remove a domain from the allowed list"""
    current_domains = config.get_allowed_domains()
    if domain in current_domains:
        current_domains.remove(domain)
        config.set('network_security.allowed_domains', current_domains)
        print(f"Removed domain from whitelist: {domain}")
    else:
        print(f"Domain not found in whitelist: {domain}")

def add_allowed_ip(ip):
    """Add an IP to the allowed list"""
    current_ips = config.get_allowed_ips()
    if ip not in current_ips:
        current_ips.append(ip)
        config.set('network_security.allowed_ips', current_ips)
        print(f"Added IP to whitelist: {ip}")
    else:
        print(f"IP already in whitelist: {ip}")

def test_connectivity(url):
    """Test connectivity to a URL"""
    print(f"Testing connectivity to: {url}")
    
    # Configure network security service
    network_security_service.configure_security(config.get_network_security_config())
    
    result = network_security_service.test_connectivity(url)
    
    print(f"URL: {result['url']}")
    print(f"Allowed: {result['allowed']}")
    print(f"Reachable: {result['reachable']}")
    if result['error']:
        print(f"Error: {result['error']}")

def set_restricted_mode(enabled):
    """Enable or disable restricted mode"""
    config.set('network_security.restricted_mode', enabled)
    mode = "enabled" if enabled else "disabled"
    print(f"Restricted mode {mode}")

def main():
    parser = argparse.ArgumentParser(description='Configure network security settings')
    parser.add_argument('--show', action='store_true', help='Show current configuration')
    parser.add_argument('--add-domain', help='Add domain to whitelist')
    parser.add_argument('--remove-domain', help='Remove domain from whitelist')
    parser.add_argument('--add-ip', help='Add IP to whitelist')
    parser.add_argument('--test-url', help='Test connectivity to URL')
    parser.add_argument('--enable-restricted', action='store_true', help='Enable restricted mode')
    parser.add_argument('--disable-restricted', action='store_true', help='Disable restricted mode')
    
    args = parser.parse_args()
    
    if args.show:
        show_current_config()
    elif args.add_domain:
        add_allowed_domain(args.add_domain)
    elif args.remove_domain:
        remove_allowed_domain(args.remove_domain)
    elif args.add_ip:
        add_allowed_ip(args.add_ip)
    elif args.test_url:
        test_connectivity(args.test_url)
    elif args.enable_restricted:
        set_restricted_mode(True)
    elif args.disable_restricted:
        set_restricted_mode(False)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

