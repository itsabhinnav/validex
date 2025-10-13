#!/usr/bin/env python3
"""
Debug script to check App1 stress test filtering
"""

import requests
import json

def debug_app1_stress_tests():
    """Debug why App1 stress tests are not showing up in filters"""
    
    print("Debugging App1 Stress Test Filtering")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Step 1: Authenticate
        session.get('http://127.0.0.1:8000/role-selection')
        session.post('http://127.0.0.1:8000/set-role', data={'role': 'admin'})
        
        # Step 2: Get all test cases for App1
        print("1. Getting all test cases for App1...")
        response = session.get('http://127.0.0.1:8000/test-cases?app=App1')
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)}")
        
        # Step 3: Check if stress tests are in the response
        print("2. Checking for stress test content...")
        stress_indicators = ['STR001', 'STR002', 'STR003', 'STR004', 'Stress', 'stress']
        found_indicators = []
        for indicator in stress_indicators:
            if indicator in response.text:
                found_indicators.append(indicator)
        print(f"   Found stress indicators: {found_indicators}")
        
        # Step 4: Get filter options for App1
        print("3. Getting filter options for App1...")
        response = session.get('http://127.0.0.1:8000/api/filter-options?apps=App1')
        if response.status_code == 200:
            data = response.json()
            print(f"   App1 test types: {data.get('test_types', [])}")
            print(f"   App1 apps: {data.get('apps', [])}")
            print(f"   Available columns: {data.get('available_columns', [])}")
        
        # Step 5: Try to get stress tests specifically
        print("4. Trying to get stress tests specifically...")
        response = session.get('http://127.0.0.1:8000/test-cases?app=App1&test_type=Stress')
        print(f"   Status: {response.status_code}")
        print(f"   Response length: {len(response.text)}")
        
        # Step 6: Check if any test cases are being returned
        print("5. Checking if any test cases are returned...")
        test_case_indicators = ['TC ID', 'Test Case ID', 'Summary']
        found_test_cases = []
        for indicator in test_case_indicators:
            if indicator in response.text:
                found_test_cases.append(indicator)
        print(f"   Found test case indicators: {found_test_cases}")
        
        # Step 7: Check the actual test case data structure
        print("6. Checking test case data structure...")
        if 'test-cases' in response.text.lower():
            print("   Test cases page is being rendered")
        else:
            print("   Test cases page is NOT being rendered")
            print("   First 200 chars of response:")
            print(response.text[:200])
        
    except Exception as e:
        print(f"Error during debugging: {e}")
    
    print("\nDebug completed!")

if __name__ == "__main__":
    debug_app1_stress_tests()

