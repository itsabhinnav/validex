#!/usr/bin/env python3
"""
Check which apps have User test types
"""

import requests

def check_user_test_types():
    """Check which apps have User test types"""
    
    print("Checking User Test Types by App")
    print("=" * 40)
    
    apps = ['App1', 'App2', 'App3', 'Apiservice', 'Bankingapp', 'Dashboard', 'Logistics', 'Webportal']
    
    for app in apps:
        try:
            response = requests.get(f'http://127.0.0.1:8000/api/filter-options?apps={app}')
            if response.status_code == 200:
                data = response.json()
                types = data.get('test_types', [])
                has_user = 'User' in types
                print(f"{app}: User={has_user}, Types={types}")
            else:
                print(f"{app}: Error {response.status_code}")
        except Exception as e:
            print(f"{app}: Exception {e}")

if __name__ == "__main__":
    check_user_test_types()

