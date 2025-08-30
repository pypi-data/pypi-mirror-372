#!/usr/bin/env python
"""
Generate comprehensive statistics for all projects in the tenant.

This script analyzes all projects and provides aggregate statistics,
insights, and trends across the entire tenant.

Usage:
    python project_statistics.py [options]
    
Examples:
    # Generate basic statistics
    python project_statistics.py
    
    # Include detailed breakdowns
    python project_statistics.py --detailed
    
    # Export statistics to CSV file
    python project_statistics.py --export stats.csv
"""

import os
import sys
import csv
import requests
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

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

def parse_date(date_str):
    """Parse date string into datetime object."""
    if not date_str:
        return None
    try:
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except:
        return None

def calculate_statistics(projects):
    """Calculate comprehensive statistics from projects."""
    if not projects:
        return {}
    
    stats = {
        'total_projects': len(projects),
        'active_projects': 0,
        'inactive_projects': 0,
        'total_datasets': 0,
        'total_dashboards': 0,
        'total_notebooks': 0,
        'total_users': 0,
        'projects_with_data': 0,
        'empty_projects': 0,
        'avg_datasets_per_project': 0,
        'avg_dashboards_per_project': 0,
        'avg_notebooks_per_project': 0,
        'max_datasets': 0,
        'max_dashboards': 0,
        'max_notebooks': 0,
        'project_types': Counter(),
        'status_distribution': Counter(),
        'creation_dates': [],
        'update_dates': [],
        'dataset_distribution': defaultdict(int),
        'dashboard_distribution': defaultdict(int),
        'top_projects_by_datasets': [],
        'top_projects_by_dashboards': [],
        'recent_projects': [],
        'oldest_projects': []
    }
    
    project_data = []
    
    for project in projects:
        # Extract project data with fallbacks
        name = (project.get('ProjectName') or 
               project.get('project_name') or 
               project.get('Name') or 
               project.get('name') or 
               'Unnamed Project')
        
        is_active = project.get('IsActive') or project.get('is_active')
        dataset_count = project.get('DatasetCount') or project.get('dataset_count') or 0
        dashboard_count = project.get('DashboardCount') or project.get('dashboard_count') or 0
        notebook_count = project.get('NotebookCount') or project.get('notebook_count') or 0
        user_count = project.get('UserCount') or project.get('user_count') or 0
        
        project_type = (project.get('ProjectType') or 
                       project.get('project_type') or 
                       project.get('Type') or 
                       'Unknown')
        
        status = project.get('Status') or project.get('status') or 'Unknown'
        
        created_date = parse_date(project.get('DateCreated') or 
                                project.get('date_created') or 
                                project.get('CreatedDate'))
        
        updated_date = parse_date(project.get('DateUpdated') or 
                                project.get('date_updated') or 
                                project.get('UpdatedDate'))
        
        # Store project data for detailed analysis
        project_info = {
            'name': name,
            'is_active': is_active,
            'dataset_count': dataset_count,
            'dashboard_count': dashboard_count,
            'notebook_count': notebook_count,
            'user_count': user_count,
            'project_type': project_type,
            'status': status,
            'created_date': created_date,
            'updated_date': updated_date
        }
        project_data.append(project_info)
        
        # Update statistics
        if is_active:
            stats['active_projects'] += 1
        else:
            stats['inactive_projects'] += 1
        
        stats['total_datasets'] += dataset_count
        stats['total_dashboards'] += dashboard_count
        stats['total_notebooks'] += notebook_count
        stats['total_users'] += user_count
        
        if dataset_count > 0 or dashboard_count > 0 or notebook_count > 0:
            stats['projects_with_data'] += 1
        else:
            stats['empty_projects'] += 1
        
        stats['max_datasets'] = max(stats['max_datasets'], dataset_count)
        stats['max_dashboards'] = max(stats['max_dashboards'], dashboard_count)
        stats['max_notebooks'] = max(stats['max_notebooks'], notebook_count)
        
        stats['project_types'][project_type] += 1
        stats['status_distribution'][status] += 1
        
        if created_date:
            stats['creation_dates'].append(created_date)
        if updated_date:
            stats['update_dates'].append(updated_date)
        
        # Distribution buckets
        if dataset_count == 0:
            stats['dataset_distribution']['0'] += 1
        elif dataset_count <= 5:
            stats['dataset_distribution']['1-5'] += 1
        elif dataset_count <= 10:
            stats['dataset_distribution']['6-10'] += 1
        elif dataset_count <= 20:
            stats['dataset_distribution']['11-20'] += 1
        else:
            stats['dataset_distribution']['20+'] += 1
        
        if dashboard_count == 0:
            stats['dashboard_distribution']['0'] += 1
        elif dashboard_count <= 10:
            stats['dashboard_distribution']['1-10'] += 1
        elif dashboard_count <= 25:
            stats['dashboard_distribution']['11-25'] += 1
        elif dashboard_count <= 50:
            stats['dashboard_distribution']['26-50'] += 1
        else:
            stats['dashboard_distribution']['50+'] += 1
    
    # Calculate averages
    if stats['total_projects'] > 0:
        stats['avg_datasets_per_project'] = stats['total_datasets'] / stats['total_projects']
        stats['avg_dashboards_per_project'] = stats['total_dashboards'] / stats['total_projects']
        stats['avg_notebooks_per_project'] = stats['total_notebooks'] / stats['total_projects']
    
    # Top projects
    project_data_sorted_datasets = sorted(project_data, key=lambda x: x['dataset_count'], reverse=True)
    stats['top_projects_by_datasets'] = project_data_sorted_datasets[:10]
    
    project_data_sorted_dashboards = sorted(project_data, key=lambda x: x['dashboard_count'], reverse=True)
    stats['top_projects_by_dashboards'] = project_data_sorted_dashboards[:10]
    
    # Recent and oldest projects
    if stats['creation_dates']:
        project_data_with_dates = [p for p in project_data if p['created_date']]
        if project_data_with_dates:
            recent_sorted = sorted(project_data_with_dates, key=lambda x: x['created_date'], reverse=True)
            stats['recent_projects'] = recent_sorted[:5]
            
            oldest_sorted = sorted(project_data_with_dates, key=lambda x: x['created_date'])
            stats['oldest_projects'] = oldest_sorted[:5]
    
    return stats

def display_statistics(stats, detailed=False):
    """Display formatted statistics."""
    print("=" * 80)
    print("mindzie TENANT PROJECT STATISTICS")
    print("=" * 80)
    
    # Overview
    print(f"\n📊 OVERVIEW")
    print("-" * 40)
    print(f"Total Projects:           {stats['total_projects']:>10}")
    print(f"Active Projects:          {stats['active_projects']:>10}")
    print(f"Inactive Projects:        {stats['inactive_projects']:>10}")
    
    if stats['total_projects'] > 0:
        active_pct = (stats['active_projects'] / stats['total_projects']) * 100
        print(f"Active Rate:              {active_pct:>9.1f}%")
    
    # Content Statistics
    print(f"\n📈 CONTENT STATISTICS")
    print("-" * 40)
    print(f"Total Datasets:           {stats['total_datasets']:>10}")
    print(f"Total Dashboards:         {stats['total_dashboards']:>10}")
    print(f"Total Notebooks:          {stats['total_notebooks']:>10}")
    print(f"Total Users:              {stats['total_users']:>10}")
    
    print(f"\nAvg Datasets/Project:     {stats['avg_datasets_per_project']:>10.1f}")
    print(f"Avg Dashboards/Project:   {stats['avg_dashboards_per_project']:>10.1f}")
    print(f"Avg Notebooks/Project:    {stats['avg_notebooks_per_project']:>10.1f}")
    
    print(f"\nMax Datasets (1 project): {stats['max_datasets']:>10}")
    print(f"Max Dashboards (1 project): {stats['max_dashboards']:>8}")
    print(f"Max Notebooks (1 project): {stats['max_notebooks']:>9}")
    
    # Project Health
    print(f"\n🏥 PROJECT HEALTH")
    print("-" * 40)
    print(f"Projects with Data:       {stats['projects_with_data']:>10}")
    print(f"Empty Projects:           {stats['empty_projects']:>10}")
    
    if stats['total_projects'] > 0:
        healthy_pct = (stats['projects_with_data'] / stats['total_projects']) * 100
        print(f"Health Rate:              {healthy_pct:>9.1f}%")
    
    if detailed:
        # Distribution Analysis
        print(f"\n📊 DATASET DISTRIBUTION")
        print("-" * 40)
        for bucket, count in sorted(stats['dataset_distribution'].items()):
            pct = (count / stats['total_projects']) * 100 if stats['total_projects'] > 0 else 0
            print(f"{bucket:>15} datasets: {count:>3} projects ({pct:4.1f}%)")
        
        print(f"\n📊 DASHBOARD DISTRIBUTION")
        print("-" * 40)
        for bucket, count in sorted(stats['dashboard_distribution'].items()):
            pct = (count / stats['total_projects']) * 100 if stats['total_projects'] > 0 else 0
            print(f"{bucket:>15} dashboards: {count:>3} projects ({pct:4.1f}%)")
        
        # Top Projects
        print(f"\n🏆 TOP PROJECTS BY DATASETS")
        print("-" * 40)
        for i, project in enumerate(stats['top_projects_by_datasets'][:5], 1):
            if project['dataset_count'] > 0:
                print(f"{i:>2}. {project['name'][:50]:50} ({project['dataset_count']:>2} datasets)")
        
        print(f"\n🏆 TOP PROJECTS BY DASHBOARDS")
        print("-" * 40)
        for i, project in enumerate(stats['top_projects_by_dashboards'][:5], 1):
            if project['dashboard_count'] > 0:
                print(f"{i:>2}. {project['name'][:50]:50} ({project['dashboard_count']:>2} dashboards)")
        
        # Project Types
        if len(stats['project_types']) > 1:
            print(f"\n🏷️  PROJECT TYPES")
            print("-" * 40)
            for ptype, count in stats['project_types'].most_common():
                pct = (count / stats['total_projects']) * 100 if stats['total_projects'] > 0 else 0
                print(f"{ptype:>20}: {count:>3} projects ({pct:4.1f}%)")
        
        # Recent Activity
        if stats['recent_projects']:
            print(f"\n🆕 RECENTLY CREATED PROJECTS")
            print("-" * 40)
            for project in stats['recent_projects']:
                date_str = project['created_date'].strftime("%Y-%m-%d") if project['created_date'] else "Unknown"
                print(f"{date_str}: {project['name'][:55]}")
    
    # Timeline Analysis
    if stats['creation_dates']:
        earliest = min(stats['creation_dates'])
        latest = max(stats['creation_dates'])
        
        print(f"\n📅 TIMELINE")
        print("-" * 40)
        print(f"Earliest Project:         {earliest.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Latest Project:           {latest.strftime('%Y-%m-%d %H:%M UTC')}")
        
        # Calculate project creation rate
        days_span = (latest - earliest).days
        if days_span > 0:
            rate = len(stats['creation_dates']) / days_span
            print(f"Creation Rate:            {rate:.2f} projects/day")
    
    print("\n" + "=" * 80)

def export_to_csv(stats, filename):
    """Export statistics to CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write summary statistics
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Projects', stats['total_projects']])
            writer.writerow(['Active Projects', stats['active_projects']])
            writer.writerow(['Inactive Projects', stats['inactive_projects']])
            writer.writerow(['Total Datasets', stats['total_datasets']])
            writer.writerow(['Total Dashboards', stats['total_dashboards']])
            writer.writerow(['Total Notebooks', stats['total_notebooks']])
            writer.writerow(['Projects with Data', stats['projects_with_data']])
            writer.writerow(['Empty Projects', stats['empty_projects']])
            writer.writerow(['Avg Datasets per Project', f"{stats['avg_datasets_per_project']:.1f}"])
            writer.writerow(['Avg Dashboards per Project', f"{stats['avg_dashboards_per_project']:.1f}"])
            writer.writerow(['Avg Notebooks per Project', f"{stats['avg_notebooks_per_project']:.1f}"])
            
            # Add distribution data
            writer.writerow([])
            writer.writerow(['Dataset Distribution', 'Project Count'])
            for bucket, count in sorted(stats['dataset_distribution'].items()):
                writer.writerow([f"{bucket} datasets", count])
            
            writer.writerow([])
            writer.writerow(['Dashboard Distribution', 'Project Count'])
            for bucket, count in sorted(stats['dashboard_distribution'].items()):
                writer.writerow([f"{bucket} dashboards", count])
        
        print(f"\n[SUCCESS] Statistics exported to {filename}")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to export to CSV: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive project statistics for mindzie tenant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate basic statistics
    python project_statistics.py
    
    # Include detailed breakdowns and top projects
    python project_statistics.py --detailed
    
    # Export statistics to CSV file
    python project_statistics.py --export tenant_stats.csv
    
    # Both detailed view and CSV export
    python project_statistics.py --detailed --export full_stats.csv
        """
    )
    
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed breakdowns and distributions')
    
    parser.add_argument('--export', metavar='FILE',
                       help='Export statistics to CSV file')
    
    args = parser.parse_args()
    
    print("Fetching all projects...")
    projects = get_all_projects()
    
    if not projects:
        print("[ERROR] Failed to retrieve projects")
        return 1
    
    print(f"Analyzing {len(projects)} projects...")
    stats = calculate_statistics(projects)
    
    # Display statistics
    display_statistics(stats, detailed=args.detailed)
    
    # Export if requested
    if args.export:
        export_to_csv(stats, args.export)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())