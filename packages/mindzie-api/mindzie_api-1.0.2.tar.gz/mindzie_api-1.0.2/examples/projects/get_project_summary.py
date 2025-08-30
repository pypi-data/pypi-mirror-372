#!/usr/bin/env python
"""
Get project summary statistics.

This script retrieves and displays summary statistics for a specific project,
including aggregated metrics, usage data, and performance indicators.

Usage:
    python get_project_summary.py <project_id>
    python get_project_summary.py 4315075c-b4d9-48c2-9520-cda63f04da7a

Examples:
    # AI Studio Development project summary
    python get_project_summary.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    
    # Insurance Claims project summary
    python get_project_summary.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
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
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except:
        return str(date_str)

def format_size(size_bytes):
    """Format file size in human readable format."""
    if not size_bytes or size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_project_summary(project_id):
    """Get project summary by ID."""
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    if not tenant_id or not api_key:
        print("[ERROR] Missing credentials!")
        print("Set MINDZIE_TENANT_ID and MINDZIE_API_KEY environment variables")
        return None
    
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project/{project_id}/summary"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            print(f"[ERROR] Project '{project_id}' not found or summary not available")
            print("Note: The summary endpoint may not be implemented in the current API")
            return None
        elif response.status_code == 401:
            print("[ERROR] Authentication failed")
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
        print(f"[ERROR] Failed to retrieve project summary: {e}")
        return None

def get_project_basic_info(project_id):
    """Fallback: Get basic project info if summary endpoint is not available."""
    tenant_id = os.getenv("MINDZIE_TENANT_ID")
    api_key = os.getenv("MINDZIE_API_KEY")
    
    url = f"https://dev.mindziestudio.com/api/{tenant_id}/project/{project_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def display_project_summary(summary_data, project_id):
    """Display formatted project summary."""
    if not summary_data:
        return
    
    print("=" * 80)
    print("PROJECT SUMMARY")
    print("=" * 80)
    
    # Project identification
    name = (summary_data.get('ProjectName') or 
           summary_data.get('project_name') or 
           summary_data.get('Name') or 'Unknown Project')
    
    print(f"\n📊 PROJECT: {name}")
    print(f"ID: {project_id}")
    print("-" * 80)
    
    # Core Statistics
    print("\n📈 CORE STATISTICS")
    print("-" * 40)
    
    dataset_count = summary_data.get('DatasetCount') or summary_data.get('dataset_count') or 0
    notebook_count = summary_data.get('NotebookCount') or summary_data.get('notebook_count') or 0
    dashboard_count = summary_data.get('DashboardCount') or summary_data.get('dashboard_count') or 0
    user_count = summary_data.get('UserCount') or summary_data.get('user_count') or 0
    
    print(f"Total Datasets:        {dataset_count:>10}")
    print(f"Total Notebooks:       {notebook_count:>10}")
    print(f"Total Dashboards:      {dashboard_count:>10}")
    print(f"Active Users:          {user_count:>10}")
    
    # Activity Metrics (if available)
    print("\n🔥 ACTIVITY METRICS")
    print("-" * 40)
    
    total_executions = summary_data.get('TotalExecutions') or summary_data.get('total_executions')
    if total_executions is not None:
        print(f"Total Executions:      {total_executions:>10}")
    
    recent_executions = summary_data.get('RecentExecutions') or summary_data.get('recent_executions')
    if recent_executions is not None:
        print(f"Recent Executions:     {recent_executions:>10}")
    
    avg_execution_time = summary_data.get('AvgExecutionTime') or summary_data.get('avg_execution_time')
    if avg_execution_time is not None:
        print(f"Avg Execution Time:    {avg_execution_time:>10}s")
    
    # Storage Information (if available)
    print("\n💾 STORAGE & DATA")
    print("-" * 40)
    
    total_storage = summary_data.get('TotalStorage') or summary_data.get('total_storage')
    if total_storage is not None:
        print(f"Total Storage Used:    {format_size(total_storage):>15}")
    
    total_records = summary_data.get('TotalRecords') or summary_data.get('total_records')
    if total_records is not None:
        print(f"Total Records:         {total_records:>15,}")
    
    # Performance Metrics (if available)
    print("\n⚡ PERFORMANCE")
    print("-" * 40)
    
    success_rate = summary_data.get('SuccessRate') or summary_data.get('success_rate')
    if success_rate is not None:
        print(f"Success Rate:          {success_rate:>12.1f}%")
    
    error_rate = summary_data.get('ErrorRate') or summary_data.get('error_rate')
    if error_rate is not None:
        print(f"Error Rate:            {error_rate:>12.1f}%")
    
    # Timestamps
    print("\n📅 TIMELINE")
    print("-" * 40)
    
    created = (summary_data.get('DateCreated') or 
              summary_data.get('date_created') or 
              summary_data.get('CreatedDate'))
    if created:
        print(f"Created:               {format_date(created)}")
    
    last_activity = (summary_data.get('LastActivity') or 
                    summary_data.get('last_activity') or
                    summary_data.get('DateUpdated') or
                    summary_data.get('date_updated'))
    if last_activity:
        print(f"Last Activity:         {format_date(last_activity)}")
    
    # Summary Insights
    print("\n💡 INSIGHTS")
    print("-" * 40)
    
    # Calculate some basic insights
    if dataset_count > 0 and dashboard_count > 0:
        ratio = dashboard_count / dataset_count
        print(f"Dashboard/Dataset Ratio: {ratio:.2f}")
    
    if user_count > 0 and dashboard_count > 0:
        dashboards_per_user = dashboard_count / user_count
        print(f"Dashboards per User:     {dashboards_per_user:.1f}")
    
    # Project maturity indicator
    if dataset_count >= 10 and dashboard_count >= 20:
        maturity = "High"
    elif dataset_count >= 5 and dashboard_count >= 10:
        maturity = "Medium"
    elif dataset_count >= 1 and dashboard_count >= 1:
        maturity = "Low"
    else:
        maturity = "Starting"
    
    print(f"Project Maturity:        {maturity}")
    
    print("\n" + "=" * 80)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Get summary statistics for a specific project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # AI Studio Development project (58 dashboards)
    python get_project_summary.py 4315075c-b4d9-48c2-9520-cda63f04da7a
    
    # Insurance Claims project (41 dashboards)  
    python get_project_summary.py bc7f6a6d-552d-44bf-b9f7-310adf733dc0
        """
    )
    
    parser.add_argument('project_id', 
                       help='Project ID (GUID format)')
    
    args = parser.parse_args()
    
    # Validate project ID format
    if len(args.project_id) != 36 or args.project_id.count('-') != 4:
        print(f"[ERROR] Invalid project ID format: {args.project_id}")
        print("Project ID should be in GUID format")
        return 1
    
    print(f"Fetching summary for project: {args.project_id}")
    print("-" * 60)
    
    # Try to get project summary
    summary_data = get_project_summary(args.project_id)
    
    # If summary endpoint not available, fall back to basic project info
    if not summary_data:
        print("\n[INFO] Summary endpoint not available, using basic project information...")
        summary_data = get_project_basic_info(args.project_id)
        
        if not summary_data:
            print(f"[ERROR] Could not retrieve any information for project {args.project_id}")
            print("Check the project ID and ensure you have access to it")
            return 1
    
    display_project_summary(summary_data, args.project_id)
    return 0

if __name__ == "__main__":
    sys.exit(main())