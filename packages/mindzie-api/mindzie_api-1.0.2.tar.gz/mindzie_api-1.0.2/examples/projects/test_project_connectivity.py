#!/usr/bin/env python
"""
Test project controller connectivity endpoints.

This script tests both authenticated and unauthenticated ping endpoints
to verify API connectivity and authentication status.

Usage:
    python test_project_connectivity.py
"""

import os
import sys
import time
import requests
from pathlib import Path

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded credentials from {env_file}")
except ImportError:
    pass

def test_unauthenticated_ping():
    """Test the unauthenticated ping endpoint."""
    print("\n" + "=" * 60)
    print("Testing Unauthenticated Project Ping")
    print("=" * 60)
    
    url = "https://dev.mindziestudio.com/api/project/unauthorized-ping"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.2f}ms")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n[SUCCESS] Unauthenticated ping works!")
            return True
        else:
            print(f"\n[ERROR] Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

def test_authenticated_ping():
    """Test the authenticated ping endpoint."""
    print("\n" + "=" * 60)
    print("Testing Authenticated Project Ping")
    print("=" * 60)
    
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("[ERROR] Missing credentials!")
        print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
        return False
    
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project/ping"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"URL: {url}")
        print(f"Headers: Authorization: Bearer ***")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time:.2f}ms")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n[SUCCESS] Authenticated ping works!")
            return True
        elif response.status_code == 401:
            print("\n[ERROR] Authentication failed - check your credentials")
            return False
        else:
            print(f"\n[ERROR] Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

def main():
    """Main test function."""
    print("=" * 70)
    print("mindzie Project Controller Connectivity Test")
    print("=" * 70)
    
    # Test results
    results = []
    
    # Test 1: Unauthenticated ping
    results.append(("Unauthenticated Ping", test_unauthenticated_ping()))
    
    # Test 2: Authenticated ping
    results.append(("Authenticated Ping", test_authenticated_ping()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All connectivity tests passed!")
        print("The project controller is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        print("Check your network connection and credentials.")
    
    print("=" * 70)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())