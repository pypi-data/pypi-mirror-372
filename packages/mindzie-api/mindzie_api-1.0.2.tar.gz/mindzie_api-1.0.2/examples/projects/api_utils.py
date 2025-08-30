#!/usr/bin/env python
"""
Shared utility functions for mindzie API examples.

This module provides common functionality used across multiple example scripts
including credential management, API URL configuration, and error handling.
"""

import os
import requests
from pathlib import Path

def load_credentials():
    """Load and validate API credentials from environment variables.
    
    Returns:
        tuple: (tenant_id, api_key, base_url) or (None, None, None) if invalid
    """
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY") 
    base_url = os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com").rstrip("/")
    
    if not tenant_id or not api_key:
        return None, None, None
    
    return tenant_id, api_key, base_url

def print_credential_error():
    """Print helpful error message for missing credentials."""
    print("[ERROR] Missing credentials!")
    print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
    print("Optionally set MINDZIE_API_URL (defaults to https://dev.mindziestudio.com)")

def make_api_request(endpoint, tenant_id=None, api_key=None, base_url=None, **kwargs):
    """Make a secure API request with proper error handling.
    
    Args:
        endpoint: API endpoint path (without base URL)
        tenant_id: Tenant ID (will load from env if not provided)
        api_key: API key (will load from env if not provided)
        base_url: Base URL (will load from env if not provided)
        **kwargs: Additional arguments for requests.get()
    
    Returns:
        dict: Response data or None on error
    """
    # Load credentials if not provided
    if not all([tenant_id, api_key, base_url]):
        tenant_id, api_key, base_url = load_credentials()
        if not all([tenant_id, api_key, base_url]):
            print_credential_error()
            return None
    
    # Build URL
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    url = f"{base_url}{endpoint}"
    
    # Prepare headers
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Set default timeout if not provided
    kwargs.setdefault('timeout', 30)
    
    try:
        response = requests.get(url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            print("[ERROR] Authentication failed - check your credentials")
            return None
        elif response.status_code == 404:
            print(f"[ERROR] Endpoint not found: {endpoint}")
            return None
        elif response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}")
            # Don't print full response as it might contain sensitive data
            return None
        
        return response.json()
        
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out")
        return None
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection failed - check your network connection")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {type(e).__name__}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}")
        return None

def get_all_projects():
    """Get all projects from the API.
    
    Returns:
        list: List of projects or None on error
    """
    tenant_id, api_key, base_url = load_credentials()
    if not all([tenant_id, api_key, base_url]):
        print_credential_error()
        return None
    
    data = make_api_request(f"/api/{tenant_id}/project", tenant_id, api_key, base_url)
    if not data:
        return None
    
    # Handle different response structures
    if 'Projects' in data:
        return data['Projects']
    elif 'projects' in data:
        return data['projects']
    elif isinstance(data, list):
        return data
    else:
        print(f"[ERROR] Unexpected response structure")
        return None

def get_project_by_id(project_id):
    """Get a specific project by ID.
    
    Args:
        project_id: Project ID (GUID format)
    
    Returns:
        dict: Project data or None on error
    """
    tenant_id, api_key, base_url = load_credentials()
    if not all([tenant_id, api_key, base_url]):
        print_credential_error()
        return None
    
    return make_api_request(f"/api/{tenant_id}/project/{project_id}", tenant_id, api_key, base_url)