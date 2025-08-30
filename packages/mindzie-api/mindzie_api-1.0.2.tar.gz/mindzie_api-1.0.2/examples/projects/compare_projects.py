#!/usr/bin/env python
"""
Compare multiple projects side by side.

This script allows you to compare 2-5 projects by displaying their
key metrics, statistics, and metadata in a side-by-side comparison table.

Usage:
    python compare_projects.py <project_id1> <project_id2> [project_id3] [project_id4] [project_id5]
    
Examples:
    # Compare two projects
    python compare_projects.py 4315075c-b4d9-48c2-9520-cda63f04da7a bc7f6a6d-552d-44bf-b9f7-310adf733dc0
    
    # Compare three projects
    python compare_projects.py 4315075c-b4d9-48c2-9520-cda63f04da7a bc7f6a6d-552d-44bf-b9f7-310adf733dc0 78b05a9c-aa81-4df5-bc0f-5fc055cc4887
    
    # Use project names instead of IDs (will search for matching names)
    python compare_projects.py --by-name "AI Studio" "Insurance Claims" "Python Demo"
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
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return str(date_str)[:16] if len(str(date_str)) > 16 else str(date_str)

def get_all_projects():
    """Get all projects from the API."""
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("[ERROR] Missing credentials!")
        print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
        return None
    
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}")
            return None
        
        data = response.json()
        
        # Handle different response structures
        if 'Projects' in data:
            return data['Projects']
        elif 'projects' in data:
            return data['projects']
        elif isinstance(data, list):
            return data
        else:
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to retrieve projects: {e}")
        return None

def get_project_by_id(project_id):
    """Get a specific project by ID."""
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"[ERROR] Project '{project_id}' not found")
            return None
        else:
            print(f"[ERROR] Failed to get project {project_id}: status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to retrieve project {project_id}: {e}")
        return None

def find_project_by_name(name, all_projects):
    """Find a project by name (case-insensitive partial match)."""
    name_lower = name.lower()
    matches = []
    
    for project in all_projects:
        project_name = (project.get('ProjectName') or 
                       project.get('project_name') or 
                       project.get('Name') or 
                       project.get('name') or '').lower()
        
        if name_lower in project_name:
            matches.append(project)
    
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"[WARNING] Multiple projects match '{name}':")
        for i, match in enumerate(matches[:5], 1):
            match_name = (match.get('ProjectName') or 
                         match.get('project_name') or 
                         match.get('Name') or 
                         match.get('name'))
            print(f"  {i}. {match_name}")
        if len(matches) > 5:
            print(f"  ... and {len(matches) - 5} more")
        print("Please use a more specific name or the project ID")
        return None
    else:
        print(f"[ERROR] No project found matching '{name}'")
        return None

def extract_project_data(project):
    """Extract and normalize project data for comparison."""
    if not project:
        return None
    
    return {
        'name': (project.get('ProjectName') or 
                project.get('project_name') or 
                project.get('Name') or 
                project.get('name') or 'Unnamed'),
        'id': (project.get('ProjectId') or 
              project.get('project_id') or 
              project.get('Id') or 
              project.get('id') or 'N/A'),
        'description': (project.get('Description') or 
                       project.get('description') or 
                       project.get('ProjectDescription') or ''),
        'is_active': project.get('IsActive') or project.get('is_active'),
        'status': project.get('Status') or project.get('status') or 'Unknown',
        'project_type': (project.get('ProjectType') or 
                        project.get('project_type') or 
                        project.get('Type') or 'Unknown'),
        'dataset_count': project.get('DatasetCount') or project.get('dataset_count') or 0,
        'dashboard_count': project.get('DashboardCount') or project.get('dashboard_count') or 0,
        'notebook_count': project.get('NotebookCount') or project.get('notebook_count') or 0,
        'user_count': project.get('UserCount') or project.get('user_count') or 0,
        'created_date': format_date(project.get('DateCreated') or 
                                   project.get('date_created') or 
                                   project.get('CreatedDate')),
        'updated_date': format_date(project.get('DateUpdated') or 
                                   project.get('date_updated') or 
                                   project.get('UpdatedDate'))
    }

def display_comparison(projects_data):
    """Display projects in a comparison table."""
    if not projects_data or len(projects_data) < 2:
        print("[ERROR] Need at least 2 projects to compare")
        return
    
    # Calculate column width based on project names
    max_name_length = max(len(p['name']) for p in projects_data)
    col_width = max(20, min(max_name_length + 2, 25))  # Between 20-25 chars
    
    print("=" * (25 + col_width * len(projects_data)))
    print("PROJECT COMPARISON")
    print("=" * (25 + col_width * len(projects_data)))
    
    # Header row with project names
    header = f"{'Metric':<23}"
    for p in projects_data:
        name = p['name']
        if len(name) > col_width - 2:
            name = name[:col_width-5] + "..."
        header += f" | {name:<{col_width-2}}"
    print(header)
    print("-" * (25 + col_width * len(projects_data)))
    
    # Comparison rows
    rows = [
        ('Project ID', 'id'),
        ('Active Status', lambda p: 'Yes' if p['is_active'] else 'No' if p['is_active'] is not None else 'Unknown'),
        ('Status', 'status'),
        ('Type', 'project_type'),
        ('Datasets', 'dataset_count'),
        ('Dashboards', 'dashboard_count'),
        ('Notebooks', 'notebook_count'),
        ('Users', 'user_count'),
        ('Created', 'created_date'),
        ('Last Updated', 'updated_date')
    ]
    
    for label, field in rows:
        row = f"{label:<23}"
        for p in projects_data:
            if callable(field):
                value = field(p)
            else:
                value = p[field]
            
            # Handle long values
            value_str = str(value)
            if len(value_str) > col_width - 2:
                if field == 'id':
                    # Show first 8 and last 8 chars of ID
                    value_str = f"{value_str[:8]}...{value_str[-8:]}"
                else:
                    value_str = value_str[:col_width-5] + "..."
            
            row += f" | {value_str:<{col_width-2}}"
        print(row)
    
    # Add descriptions if any project has one
    descriptions = [p['description'] for p in projects_data if p['description']]
    if descriptions:
        print("\n" + "=" * (25 + col_width * len(projects_data)))
        print("DESCRIPTIONS")
        print("=" * (25 + col_width * len(projects_data)))
        
        for i, p in enumerate(projects_data, 1):
            if p['description']:
                print(f"\n{i}. {p['name']}")
                print(f"   {p['description']}")
    
    # Analysis
    print("\n" + "=" * (25 + col_width * len(projects_data)))
    print("COMPARISON ANALYSIS")
    print("=" * (25 + col_width * len(projects_data)))
    
    # Find project with most content
    most_datasets = max(projects_data, key=lambda p: p['dataset_count'])
    most_dashboards = max(projects_data, key=lambda p: p['dashboard_count'])
    most_notebooks = max(projects_data, key=lambda p: p['notebook_count'])
    most_users = max(projects_data, key=lambda p: p['user_count'])
    
    print(f"\nMost Datasets:    {most_datasets['name']} ({most_datasets['dataset_count']} datasets)")
    print(f"Most Dashboards:  {most_dashboards['name']} ({most_dashboards['dashboard_count']} dashboards)")
    print(f"Most Notebooks:   {most_notebooks['name']} ({most_notebooks['notebook_count']} notebooks)")
    print(f"Most Users:       {most_users['name']} ({most_users['user_count']} users)")
    
    # Activity analysis
    active_projects = [p for p in projects_data if p['is_active']]
    if len(active_projects) < len(projects_data):
        inactive_count = len(projects_data) - len(active_projects)
        print(f"\nActivity: {len(active_projects)}/{len(projects_data)} projects are active")
        if inactive_count > 0:
            inactive_names = [p['name'] for p in projects_data if not p['is_active']]
            print(f"Inactive: {', '.join(inactive_names)}")
    else:
        print(f"\nActivity: All {len(projects_data)} projects are active")
    
    # Total content summary
    total_datasets = sum(p['dataset_count'] for p in projects_data)
    total_dashboards = sum(p['dashboard_count'] for p in projects_data)
    total_notebooks = sum(p['notebook_count'] for p in projects_data)
    total_users = sum(p['user_count'] for p in projects_data)
    
    print(f"\nCombined Totals:")
    print(f"  Datasets: {total_datasets}")
    print(f"  Dashboards: {total_dashboards}")
    print(f"  Notebooks: {total_notebooks}")
    print(f"  Users: {total_users}")
    
    print("\n" + "=" * (25 + col_width * len(projects_data)))

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Compare multiple mindzie projects side by side",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Compare two projects by ID
    python compare_projects.py 4315075c-b4d9-48c2-9520-cda63f04da7a bc7f6a6d-552d-44bf-b9f7-310adf733dc0
    
    # Compare three projects by ID
    python compare_projects.py 4315075c-b4d9-48c2-9520-cda63f04da7a bc7f6a6d-552d-44bf-b9f7-310adf733dc0 78b05a9c-aa81-4df5-bc0f-5fc055cc4887
    
    # Compare projects by name (partial matches)
    python compare_projects.py --by-name "AI Studio" "Insurance" "Python"
    
    # Mix of IDs and names
    python compare_projects.py --by-name "AI Studio" --by-id bc7f6a6d-552d-44bf-b9f7-310adf733dc0
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument('project_ids', nargs='*',
                       help='Project IDs to compare (2-5 projects)')
    
    group.add_argument('--by-name', nargs='+',
                       help='Project names to search for and compare (2-5 projects)')
    
    parser.add_argument('--by-id', nargs='+',
                       help='Additional project IDs when using --by-name')
    
    args = parser.parse_args()
    
    # Determine which projects to compare
    if args.project_ids:
        project_identifiers = args.project_ids
        by_name = False
    else:
        project_identifiers = args.by_name or []
        if args.by_id:
            project_identifiers.extend(args.by_id)
        by_name = True
    
    # Validate number of projects
    if len(project_identifiers) < 2:
        print("[ERROR] Need at least 2 projects to compare")
        return 1
    elif len(project_identifiers) > 5:
        print("[ERROR] Can compare at most 5 projects")
        return 1
    
    print(f"Comparing {len(project_identifiers)} projects...")
    print("-" * 60)
    
    projects_data = []
    
    if by_name:
        # Get all projects first for name lookup
        all_projects = get_all_projects()
        if not all_projects:
            return 1
        
        for identifier in project_identifiers:
            if len(identifier) == 36 and identifier.count('-') == 4:
                # Looks like a GUID, treat as ID
                project = get_project_by_id(identifier)
            else:
                # Treat as name
                project = find_project_by_name(identifier, all_projects)
            
            if project:
                data = extract_project_data(project)
                if data:
                    projects_data.append(data)
                    print(f"[SUCCESS] Found project: {data['name']}")
                else:
                    print(f"[ERROR] Failed to extract data for project: {identifier}")
                    return 1
            else:
                print(f"[ERROR] Could not find project: {identifier}")
                return 1
    else:
        # Get projects by ID
        for project_id in project_identifiers:
            if len(project_id) != 36 or project_id.count('-') != 4:
                print(f"[ERROR] Invalid project ID format: {project_id}")
                return 1
            
            project = get_project_by_id(project_id)
            if project:
                data = extract_project_data(project)
                if data:
                    projects_data.append(data)
                    print(f"[SUCCESS] Found project: {data['name']}")
                else:
                    print(f"[ERROR] Failed to extract data for project: {project_id}")
                    return 1
            else:
                return 1
    
    if len(projects_data) < 2:
        print(f"[ERROR] Only found {len(projects_data)} valid project(s), need at least 2")
        return 1
    
    # Display comparison
    print()
    display_comparison(projects_data)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())