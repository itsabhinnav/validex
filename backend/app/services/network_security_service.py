"""
Network Security Service

This service provides network isolation and URL whitelisting capabilities
to restrict outbound internet access while allowing specific URLs like Artifactory.
"""

import socket
import urllib.parse
import re
from typing import List, Set, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import logging

class NetworkSecurityService:
    """Service for network security and URL whitelisting"""
    
    def __init__(self):
        self.allowed_domains: Set[str] = set()
        self.allowed_ips: Set[str] = set()
        self.blocked_domains: Set[str] = set()
        self.is_restricted_mode = True
        self.logger = logging.getLogger(__name__)
        
    def configure_security(self, config: dict):
        """Configure network security settings"""
        self.allowed_domains = set(config.get('allowed_domains', []))
        self.allowed_ips = set(config.get('allowed_ips', []))
        self.blocked_domains = set(config.get('blocked_domains', []))
        self.is_restricted_mode = config.get('restricted_mode', True)
        
        self.logger.info(f"Network security configured: {len(self.allowed_domains)} allowed domains, "
                        f"{len(self.allowed_ips)} allowed IPs, restricted mode: {self.is_restricted_mode}")
    
    def is_url_allowed(self, url: str) -> bool:
        """Check if a URL is allowed based on whitelist"""
        if not self.is_restricted_mode:
            return True
            
        try:
            parsed_url = urllib.parse.urlparse(url)
            domain = parsed_url.hostname
            
            if not domain:
                return False
                
            if domain in self.blocked_domains:
                return False
                
            if domain in self.allowed_domains:
                return True
                
            for allowed_domain in self.allowed_domains:
                if self._domain_matches_pattern(domain, allowed_domain):
                    return True
                    
            try:
                ip = socket.gethostbyname(domain)
                if ip in self.allowed_ips:
                    return True
            except socket.gaierror:
                pass
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking URL {url}: {e}")
            return False
    
    def _domain_matches_pattern(self, domain: str, pattern: str) -> bool:
        """Check if domain matches a pattern (supports wildcards)"""
        if '*' in pattern:
            regex_pattern = pattern.replace('*', '.*')
            return re.match(f"^{regex_pattern}$", domain) is not None
        return domain == pattern
    
    def safe_request(self, url: str, **kwargs) -> Optional[bytes]:
        """Make a safe HTTP request with URL whitelist checking"""
        if not self.is_url_allowed(url):
            self.logger.warning(f"Blocked request to non-whitelisted URL: {url}")
            return None
            
        try:
            request = Request(url, **kwargs)
            with urlopen(request, timeout=30) as response:
                return response.read()
        except (URLError, HTTPError) as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error for {url}: {e}")
            return None
    
    def get_security_status(self) -> dict:
        """Get current security configuration status"""
        return {
            'restricted_mode': self.is_restricted_mode,
            'allowed_domains': list(self.allowed_domains),
            'allowed_ips': list(self.allowed_ips),
            'blocked_domains': list(self.blocked_domains),
            'total_allowed': len(self.allowed_domains) + len(self.allowed_ips)
        }
    
    def add_allowed_domain(self, domain: str):
        """Add a domain to the allowed list"""
        self.allowed_domains.add(domain)
        self.logger.info(f"Added allowed domain: {domain}")
    
    def add_allowed_ip(self, ip: str):
        """Add an IP to the allowed list"""
        self.allowed_ips.add(ip)
        self.logger.info(f"Added allowed IP: {ip}")
    
    def remove_allowed_domain(self, domain: str):
        """Remove a domain from the allowed list"""
        self.allowed_domains.discard(domain)
        self.logger.info(f"Removed allowed domain: {domain}")
    
    def test_connectivity(self, url: str) -> dict:
        """Test connectivity to a URL"""
        result = {
            'url': url,
            'allowed': self.is_url_allowed(url),
            'reachable': False,
            'error': None
        }
        
        if not result['allowed']:
            result['error'] = 'URL not in whitelist'
            return result
            
        try:
            response = self.safe_request(url)
            result['reachable'] = response is not None
        except Exception as e:
            result['error'] = str(e)
            
        return result

network_security_service = NetworkSecurityService()

