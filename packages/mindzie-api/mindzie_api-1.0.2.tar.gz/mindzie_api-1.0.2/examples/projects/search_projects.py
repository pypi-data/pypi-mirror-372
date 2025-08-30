#!/usr/bin/env python
"""
Search projects with various filters.

This script demonstrates how to search and filter projects by name,
activity status, and dataset count using command line options.

Usage:
    python search_projects.py [options]
    
Examples:
    # Search for projects containing "demo" in the name
    python search_projects.py --name demo
    
    # Find only active projects  
    python search_projects.py --active
    
    # Find projects with at least 10 datasets
    python search_projects.py --min-datasets 10
    
    # Combine filters: active projects with "ai" in name and 5+ datasets
    python search_projects.py --name ai --active --min-datasets 5
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
        return str(date_str)[:19] if len(str(date_str)) > 19 else str(date_str)

def get_all_projects():
    """Get all projects from the API."""
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    base_url = os.getenv("MINDZIE_API_URL", "https://dev.mindziestudio.com").rstrip("/")
    
    if not tenant_id or not api_key:
        print("[ERROR] Missing credentials!")
        print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
        print("Optionally set MINDZIE_API_URL (defaults to https://dev.mindziestudio.com)")
        return None
    
    url = f"{base_url}/api/{tenant_id}/project"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}")
            print(f"Response: {response.text}")
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
            print(f"[ERROR] Unexpected response structure: {data.keys()}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to retrieve projects: {e}")
        return None

def filter_projects(projects, name_filter=None, active_filter=None, min_datasets=None):
    """Apply filters to the project list."""
    filtered = projects
    
    # Filter by name
    if name_filter:
        name_lower = name_filter.lower()
        filtered = [
            p for p in filtered
            if name_lower in (
                p.get('ProjectName') or 
                p.get('project_name') or 
                p.get('Name') or 
                p.get('name') or ''
            ).lower()
        ]
    
    # Filter by active status
    if active_filter is not None:
        filtered = [
            p for p in filtered
            if (p.get('IsActive') or p.get('is_active')) == active_filter
        ]
    
    # Filter by minimum dataset count
    if min_datasets is not None:
        filtered = [
            p for p in filtered
            if (p.get('DatasetCount') or p.get('dataset_count') or 0) >= min_datasets
        ]
    
    return filtered

def display_project_summary(project, index):
    """Display a summary of a single project."""
    name = (project.get('ProjectName') or 
           project.get('project_name') or 
           project.get('Name') or 
           project.get('name') or 
           'Unnamed Project')
    
    print(f"\n{index}. {name}")
    print("   " + "=" * 65)
    
    # Project ID
    project_id = (project.get('ProjectId') or 
                 project.get('project_id') or 
                 project.get('Id') or 
                 project.get('id'))
    if project_id:
        print(f"   ID:           {project_id}")
    
    # Description (truncated)
    desc = (project.get('Description') or 
           project.get('description') or 
           project.get('ProjectDescription'))
    if desc:
        if len(desc) > 60:
            desc = desc[:57] + "..."
        print(f"   Description:  {desc}")
    
    # Statistics in one line
    stats = []
    
    dataset_count = (project.get('DatasetCount') or 
                   project.get('dataset_count') or 0)
    if dataset_count > 0:
        stats.append(f"Datasets: {dataset_count}")
    
    dashboard_count = (project.get('DashboardCount') or 
                     project.get('dashboard_count') or 0)
    if dashboard_count > 0:
        stats.append(f"Dashboards: {dashboard_count}")
    
    notebook_count = (project.get('NotebookCount') or 
                    project.get('notebook_count') or 0)
    if notebook_count > 0:
        stats.append(f"Notebooks: {notebook_count}")
    
    if stats:
        print(f"   Stats:        {' | '.join(stats)}")
    
    # Status and activity
    is_active = project.get('IsActive') or project.get('is_active')
    status = project.get('Status') or project.get('status')
    
    status_parts = []
    if is_active is not None:
        status_parts.append(f"Active: {'Yes' if is_active else 'No'}")
    if status:
        status_parts.append(f"Status: {status}")
    
    if status_parts:
        print(f"   Status:       {' | '.join(status_parts)}")
    
    # Created date
    created = (project.get('DateCreated') or 
              project.get('date_created') or 
              project.get('CreatedDate'))
    if created:
        print(f"   Created:      {format_date(created)}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Search and filter mindzie projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Search for projects containing "demo" in the name
    python search_projects.py --name demo
    
    # Find only active projects
    python search_projects.py --active
    
    # Find inactive projects
    python search_projects.py --inactive
    
    # Find projects with at least 10 datasets
    python search_projects.py --min-datasets 10
    
    # Combine filters: active projects with "ai" in name and 5+ datasets
    python search_projects.py --name ai --active --min-datasets 5
    
    # List all projects (no filters)
    python search_projects.py
        """
    )
    
    parser.add_argument('--name', 
                       help='Filter by project name (case-insensitive partial match)')
    
    parser.add_argument('--active', action='store_true',
                       help='Show only active projects')
    
    parser.add_argument('--inactive', action='store_true',
                       help='Show only inactive projects')
    
    parser.add_argument('--min-datasets', type=int,
                       help='Show projects with at least this many datasets')
    
    parser.add_argument('--max-results', type=int, default=50,
                       help='Maximum number of results to display (default: 50)')
    
    args = parser.parse_args()
    
    # Validate conflicting arguments
    if args.active and args.inactive:
        print("[ERROR] Cannot specify both --active and --inactive")
        return 1
    
    # Determine active filter
    active_filter = None
    if args.active:
        active_filter = True
    elif args.inactive:
        active_filter = False
    
    print("=" * 70)
    print("mindzie Project Search")
    print("=" * 70)
    
    # Display active filters
    filters_applied = []
    if args.name:
        filters_applied.append(f"Name contains: '{args.name}'")
    if active_filter is not None:
        filters_applied.append(f"Active: {'Yes' if active_filter else 'No'}")
    if args.min_datasets:
        filters_applied.append(f"Min datasets: {args.min_datasets}")
    
    if filters_applied:
        print(f"\nFilters: {' | '.join(filters_applied)}")
    else:
        print("\nNo filters applied - showing all projects")
    
    print("-" * 70)
    
    # Get all projects
    print("\nFetching projects...")
    all_projects = get_all_projects()
    
    if not all_projects:
        print("[ERROR] Failed to retrieve projects")
        return 1
    
    # Apply filters
    filtered_projects = filter_projects(
        all_projects, 
        name_filter=args.name,
        active_filter=active_filter,
        min_datasets=args.min_datasets
    )
    
    total_found = len(filtered_projects)
    total_all = len(all_projects)
    
    if total_found == 0:
        print(f"\nNo projects found matching your criteria.")
        print(f"Total projects in tenant: {total_all}")
        return 0
    
    # Limit results if requested
    display_projects = filtered_projects[:args.max_results]
    display_count = len(display_projects)
    
    print(f"\nFound {total_found} project(s) matching criteria")
    if display_count < total_found:
        print(f"Displaying first {display_count} results (use --max-results to show more)")
    print()
    
    # Display projects
    for i, project in enumerate(display_projects, 1):
        display_project_summary(project, i)
    
    print("\n" + "=" * 70)
    print(f"Results: {display_count} displayed / {total_found} found / {total_all} total")
    
    # Suggest refinements if too many results
    if total_found > 20 and not any([args.name, active_filter is not None, args.min_datasets]):
        print("\nTip: Use filters to narrow down results:")
        print("  --name <text>      Filter by name")
        print("  --active/--inactive Filter by status")
        print("  --min-datasets <n> Filter by dataset count")
    
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())