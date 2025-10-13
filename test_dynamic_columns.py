#!/usr/bin/env python3
"""
Test script to verify dynamic column selection functionality
"""

import requests
import json

def test_dynamic_column_functionality():
    """Test the dynamic column selection functionality"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("Testing Dynamic Column Selection Functionality")
    print("=" * 50)
    
    # Step 1: Access home page
    print("1. Accessing home page...")
    response = session.get('http://127.0.0.1:8000/')
    print(f"   Status: {response.status_code}")
    
    # Step 2: Access role selection page
    print("2. Accessing role selection page...")
    response = session.get('http://127.0.0.1:8000/role-selection')
    print(f"   Status: {response.status_code}")
    
    # Step 3: Select Administrator role
    print("3. Selecting Administrator role...")
    response = session.post('http://127.0.0.1:8000/set-role', data={
        'role': 'admin'
    })
    print(f"   Status: {response.status_code}")
    
    # Step 4: Access test cases page
    print("4. Accessing test cases page...")
    response = session.get('http://127.0.0.1:8000/test-cases')
    print(f"   Status: {response.status_code}")
    print(f"   Contains loadAvailableColumns: {'loadAvailableColumns' in response.text}")
    print(f"   Contains initializeDynamicFilters: {'initializeDynamicFilters' in response.text}")
    
    # Step 5: Test the API endpoint
    print("5. Testing filter-options API...")
    response = session.get('http://127.0.0.1:8000/api/filter-options')
    if response.status_code == 200:
        data = response.json()
        print(f"   Available columns: {len(data.get('available_columns', []))}")
        print(f"   Column mappings: {len(data.get('column_mappings', {}))}")
        print(f"   Available apps: {data.get('apps', [])}")
        
        # Test with specific app
        print("6. Testing API with specific app (Apiservice)...")
        response = session.get('http://127.0.0.1:8000/api/filter-options?apps=Apiservice')
        if response.status_code == 200:
            data = response.json()
            print(f"   Apiservice columns: {len(data.get('available_columns', []))}")
            print(f"   Apiservice mappings: {len(data.get('column_mappings', {}))}")
            
            # Show some sample mappings
            mappings = data.get('column_mappings', {})
            if 'id' in mappings:
                print(f"   ID mappings: {len(mappings['id'])}")
                for mapping in mappings['id'][:2]:  # Show first 2
                    print(f"     - {mapping['column']} (confidence: {mapping['confidence']})")
        else:
            print(f"   Error: {response.status_code}")
    else:
        print(f"   Error: {response.status_code}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_dynamic_column_functionality()
