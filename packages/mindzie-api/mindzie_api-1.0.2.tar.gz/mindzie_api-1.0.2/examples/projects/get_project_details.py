#!/usr/bin/env python
"""
Get detailed information for a specific project.

This script retrieves and displays comprehensive information about a project
including metadata, statistics, configuration, and timestamps.

Usage:
    python get_project_details.py <project_id>
    python get_project_details.py 4315075c-b4d9-48c2-9520-cda63f04da7a

Examples:
    # AI Studio Development project
    python get_project_details.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    
    # Insurance Claims project  
    python get_project_details.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
    
    # Python Demo project
    python get_project_details.py 78b05a9c-aa81-4df5-bc0f-5fc055cc4887
"""

import os
import sys
import requests
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return str(date_str)

def get_project_details(project_id):
    """Get detailed project information by ID."""
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("[ERROR] Missing credentials!")
        print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
        return None
    
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            print(f"[ERROR] Project '{project_id}' not found")
            print("Check the project ID and ensure you have access to it")
            return None
        elif response.status_code == 401:
            print("[ERROR] Authentication failed")
            print("Check your credentials")
            return None
        elif response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve project: {e}")
        return None

def display_project_details(project_data):
    """Display formatted project details."""
    if not project_data:
        return
    
    print("=" * 80)
    print("PROJECT DETAILS")
    print("=" * 80)
    
    # Basic Information
    print("\n📋 BASIC INFORMATION")
    print("-" * 40)
    
    name = (project_data.get('ProjectName') or 
           project_data.get('project_name') or 
           project_data.get('Name') or 'Unknown')
    print(f"Name:              {name}")
    
    project_id = (project_data.get('ProjectId') or 
                 project_data.get('project_id') or 
                 project_data.get('Id'))
    if project_id:
        print(f"ID:                {project_id}")
    
    description = (project_data.get('Description') or 
                  project_data.get('description') or 
                  project_data.get('ProjectDescription'))
    if description:
        print(f"Description:       {description}")
    
    # Timestamps
    print("\n📅 TIMESTAMPS")
    print("-" * 40)
    
    created = (project_data.get('DateCreated') or 
              project_data.get('date_created') or 
              project_data.get('CreatedDate'))
    if created:
        print(f"Created:           {format_date(created)}")
    
    updated = (project_data.get('DateUpdated') or 
              project_data.get('date_updated') or 
              project_data.get('UpdatedDate'))
    if updated:
        print(f"Last Updated:      {format_date(updated)}")
    
    # Statistics
    print("\n📊 STATISTICS")
    print("-" * 40)
    
    dataset_count = project_data.get('DatasetCount') or project_data.get('dataset_count') or 0
    notebook_count = project_data.get('NotebookCount') or project_data.get('notebook_count') or 0
    dashboard_count = project_data.get('DashboardCount') or project_data.get('dashboard_count') or 0
    user_count = project_data.get('UserCount') or project_data.get('user_count') or 0
    
    print(f"Datasets:          {dataset_count}")
    print(f"Notebooks:         {notebook_count}")
    print(f"Dashboards:        {dashboard_count}")
    print(f"Users:             {user_count}")
    
    # Status and Configuration
    print("\n⚙️  STATUS & CONFIGURATION")
    print("-" * 40)
    
    status = project_data.get('Status') or project_data.get('status') or 'Unknown'
    print(f"Status:            {status}")
    
    is_active = project_data.get('IsActive') or project_data.get('is_active')
    if is_active is not None:
        print(f"Active:            {'Yes' if is_active else 'No'}")
    
    project_type = (project_data.get('ProjectType') or 
                   project_data.get('project_type') or 
                   project_data.get('Type'))
    if project_type:
        print(f"Type:              {project_type}")
    
    # Additional metadata if available
    print("\n🔧 ADDITIONAL INFORMATION")
    print("-" * 40)
    
    for key, value in project_data.items():
        if key not in ['ProjectName', 'project_name', 'Name', 'ProjectId', 'project_id', 'Id',
                      'Description', 'description', 'ProjectDescription', 
                      'DateCreated', 'date_created', 'CreatedDate',
                      'DateUpdated', 'date_updated', 'UpdatedDate',
                      'DatasetCount', 'dataset_count', 'NotebookCount', 'notebook_count',
                      'DashboardCount', 'dashboard_count', 'UserCount', 'user_count',
                      'Status', 'status', 'IsActive', 'is_active', 
                      'ProjectType', 'project_type', 'Type']:
            if value is not None and value != "":
                # Format the key nicely
                formatted_key = key.replace('_', ' ').title()
                print(f"{formatted_key:<18} {value}")
    
    print("\n" + "=" * 80)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Get detailed information for a specific project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # AI Studio Development project (58 dashboards)
    python get_project_details.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    
    # Insurance Claims project (41 dashboards)
    python get_project_details.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
    
    # Python Demo project (16 datasets)
    python get_project_details.py 78b05a9c-aa81-4df5-bc0f-5fc055cc4887
        """
    )
    
    parser.add_argument('project_id', 
                       help='Project ID (GUID format)')
    
    args = parser.parse_args()
    
    # Validate project ID format (basic GUID check)
    if len(args.project_id) != 36 or args.project_id.count('-') != 4:
        print(f"[ERROR] Invalid project ID format: {args.project_id}")
        print("Project ID should be in GUID format (e.g., 12345678-1234-1234-1234-123456789012)")
        return 1
    
    print(f"Fetching details for project: {args.project_id}")
    print("-" * 60)
    
    # Get project details
    project_data = get_project_details(args.project_id)
    
    if project_data:
        display_project_details(project_data)
        return 0
    else:
        print("\nFailed to retrieve project details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())