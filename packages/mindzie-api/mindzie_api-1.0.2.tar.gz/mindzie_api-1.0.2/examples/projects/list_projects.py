#!/usr/bin/env python
"""
List all projects in your mindzie tenant.

This script demonstrates how to retrieve and display all projects
associated with your tenant using the mindzie-api package.
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded credentials from {env_file}")
except ImportError:
    pass

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return "N/A"
    try:
        # Handle different date formats
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return str(date_str)[:19] if len(str(date_str)) > 19 else str(date_str)

def main():
    print("=" * 70)
    print("mindzie Project List")
    print("=" * 70)
    
    # Get credentials from environment
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("\n[ERROR] Missing credentials!")
        print("\nSet environment variables or create .env file with:")
        print("MINDZIE_TENANT_ID=your-tenant-id")
        print("MINDZIE_API_KEY=your-api-key")
        return 1
    
    print(f"\nTenant ID: {tenant_id}")
    print("-" * 70)
    
    # Make direct API call
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        print("\nFetching projects...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return 1
        
        data = response.json()
        
        # Handle different response structures
        if 'Projects' in data:
            projects = data['Projects']
        elif 'projects' in data:
            projects = data['projects']
        elif isinstance(data, list):
            projects = data
        else:
            print(f"[ERROR] Unexpected response structure: {data.keys()}")
            return 1
        
        total = len(projects)
        
        if total == 0:
            print("\nNo projects found in this tenant.")
            return 0
        
        print(f"\nFound {total} project(s):\n")
        print("-" * 70)
        
        # Display each project
        for i, project in enumerate(projects, 1):
            # Handle different naming conventions
            name = (project.get('ProjectName') or 
                   project.get('project_name') or 
                   project.get('Name') or 
                   project.get('name') or 
                   'Unnamed Project')
            
            print(f"\n{i}. {name}")
            print("   " + "=" * 65)
            
            # Project ID
            project_id = (project.get('ProjectId') or 
                         project.get('project_id') or 
                         project.get('Id') or 
                         project.get('id'))
            if project_id:
                print(f"   ID:           {project_id}")
            
            # Description
            desc = (project.get('Description') or 
                   project.get('description') or 
                   project.get('ProjectDescription'))
            if desc:
                if len(desc) > 60:
                    desc = desc[:57] + "..."
                print(f"   Description:  {desc}")
            
            # Dates
            created = (project.get('DateCreated') or 
                      project.get('date_created') or 
                      project.get('CreatedDate'))
            if created:
                print(f"   Created:      {format_date(created)}")
            
            updated = (project.get('DateUpdated') or 
                      project.get('date_updated') or 
                      project.get('UpdatedDate'))
            if updated:
                print(f"   Updated:      {format_date(updated)}")
            
            # Statistics
            stats = []
            
            dataset_count = (project.get('DatasetCount') or 
                           project.get('dataset_count') or 
                           project.get('Datasets'))
            if dataset_count is not None:
                stats.append(f"Datasets: {dataset_count}")
            
            notebook_count = (project.get('NotebookCount') or 
                            project.get('notebook_count') or 
                            project.get('Notebooks'))
            if notebook_count is not None:
                stats.append(f"Notebooks: {notebook_count}")
            
            dashboard_count = (project.get('DashboardCount') or 
                             project.get('dashboard_count') or 
                             project.get('Dashboards'))
            if dashboard_count is not None:
                stats.append(f"Dashboards: {dashboard_count}")
            
            user_count = (project.get('UserCount') or 
                         project.get('user_count') or 
                         project.get('Users'))
            if user_count is not None:
                stats.append(f"Users: {user_count}")
            
            if stats:
                print(f"   Stats:        {' | '.join(stats)}")
            
            # Project type/status
            project_type = (project.get('ProjectType') or 
                           project.get('project_type') or 
                           project.get('Type'))
            if project_type:
                print(f"   Type:         {project_type}")
            
            status = project.get('Status') or project.get('status')
            if status:
                print(f"   Status:       {status}")
        
        print("\n" + "=" * 70)
        print(f"Total: {total} project(s)")
        print("=" * 70)
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Network error: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Failed to retrieve projects: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify your credentials are correct")
        print("3. Ensure you have access to the tenant")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())