"""
Secure HTTP Client

This module provides a secure HTTP client that respects network security policies
and only allows connections to whitelisted URLs.
"""

import urllib.request
import urllib.error
from typing import Optional, Dict, Any
import json
from app.services.network_security_service import network_security_service

class SecureHTTPClient:
    """HTTP client with network security restrictions"""
    
    def __init__(self):
        self.timeout = 30
        self.user_agent = "Validex-SecureClient/1.0"
    
    def get(self, url: str, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Make a secure GET request"""
        if not network_security_service.is_url_allowed(url):
            raise SecurityError(f"URL not allowed by security policy: {url}")
        
        try:
            request = urllib.request.Request(url, headers=headers or {})
            request.add_header('User-Agent', self.user_agent)
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = response.read()
                return {
                    'status_code': response.getcode(),
                    'headers': dict(response.headers),
                    'data': data,
                    'url': response.geturl()
                }
        except urllib.error.HTTPError as e:
            raise HTTPError(f"HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise NetworkError(f"Network error: {e.reason}")
        except Exception as e:
            raise RequestError(f"Request failed: {str(e)}")
    
    def post(self, url: str, data: bytes = None, headers: Dict[str, str] = None) -> Optional[Dict[str, Any]]:
        """Make a secure POST request"""
        if not network_security_service.is_url_allowed(url):
            raise SecurityError(f"URL not allowed by security policy: {url}")
        
        try:
            request = urllib.request.Request(url, data=data, headers=headers or {})
            request.add_header('User-Agent', self.user_agent)
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_data = response.read()
                return {
                    'status_code': response.getcode(),
                    'headers': dict(response.headers),
                    'data': response_data,
                    'url': response.geturl()
                }
        except urllib.error.HTTPError as e:
            raise HTTPError(f"HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise NetworkError(f"Network error: {e.reason}")
        except Exception as e:
            raise RequestError(f"Request failed: {str(e)}")
    
    def download_file(self, url: str, local_path: str) -> bool:
        """Download a file securely"""
        if not network_security_service.is_url_allowed(url):
            raise SecurityError(f"URL not allowed by security policy: {url}")
        
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                with open(local_path, 'wb') as f:
                    f.write(response.read())
            return True
        except Exception as e:
            raise DownloadError(f"Download failed: {str(e)}")
    
    def test_connectivity(self, url: str) -> Dict[str, Any]:
        """Test connectivity to a URL"""
        return network_security_service.test_connectivity(url)

# Custom exceptions
class SecurityError(Exception):
    """Raised when a security policy violation occurs"""
    pass

class HTTPError(Exception):
    """Raised when an HTTP error occurs"""
    pass

class NetworkError(Exception):
    """Raised when a network error occurs"""
    pass

class RequestError(Exception):
    """Raised when a general request error occurs"""
    pass

class DownloadError(Exception):
    """Raised when a download error occurs"""
    pass

# Global instance
secure_client = SecureHTTPClient()

