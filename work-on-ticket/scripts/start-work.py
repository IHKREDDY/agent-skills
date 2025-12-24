#!/usr/bin/env python3
"""
Start Work on Jira Ticket

Complete automated workflow:
- Fetches ticket details
- Creates feature branch with proper naming
- Updates ticket status to "In Progress"
- Adds comment that work has started

Usage:
    python start-work.py --ticket PROJ-123
    python start-work.py --ticket PROJ-123 --branch-type bugfix
"""

import argparse
import os
import sys
import subprocess
import re
from typing import Optional
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

# Import config manager
sys.path.insert(0, str(Path(__file__).parent))
from jira_config import get_config


class JiraClient:
    def __init__(self, profile: Optional[str] = None):
        # Get credentials from config file or environment
        credentials = get_config(profile)
        
        self.base_url = credentials['url'].rstrip('/')
        self.email = credentials['email']
        self.api_token = credentials['token']
        
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_issue(self, issue_key: str):
        """Fetch issue details."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_transitions(self, issue_key: str):
        """Get available transitions."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json().get('transitions', [])
    
    def transition_issue(self, issue_key: str, transition_name: str):
        """Transition issue to new status."""
        transitions = self.get_transitions(issue_key)
        
        transition_id = None
        for trans in transitions:
            if trans['name'].lower() == transition_name.lower():
                transition_id = trans['id']
                break
        
        if not transition_id:
            print(f"⚠️  Transition '{transition_name}' not available")
            return False
        
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        data = {'transition': {'id': transition_id}}
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return True
    
    def add_comment(self, issue_key: str, comment: str):
        """Add comment to issue."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
        data = {
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [
                    {
                        'type': 'paragraph',
                        'content': [
                            {
                                'type': 'text',
                                'text': comment
                            }
                        ]
                    }
                ]
            }
        }
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return True


def slugify(text: str) -> str:
    """Convert text to slug format for branch names."""
    # Remove special characters
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # Replace spaces with hyphens
    text = re.sub(r'[-\s]+', '-', text)
    # Trim hyphens from ends
    text = text.strip('-')
    # Limit length
    return text[:50]


def create_branch(ticket_key: str, summary: str, branch_type: str = 'feature') -> str:
    """Create git branch."""
    # Generate branch name
    slug = slugify(summary)
    branch_name = f"{branch_type}/{ticket_key.lower()}-{slug}"
    
    try:
        # Check if we're in a git repo
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      check=True, capture_output=True)
        
        # Check if branch already exists
        result = subprocess.run(['git', 'branch', '--list', branch_name],
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print(f"⚠️  Branch '{branch_name}' already exists")
            # Checkout existing branch
            subprocess.run(['git', 'checkout', branch_name], check=True)
            return branch_name
        
        # Create and checkout new branch
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
        print(f"✓ Created and checked out branch: {branch_name}")
        return branch_name
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        return None


def display_ticket_info(issue_data: dict):
    """Display ticket information."""
    fields = issue_data['fields']
    issue_key = issue_data['key']
    
    summary = fields.get('summary', 'No summary')
    issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
    status = fields.get('status', {}).get('name', 'Unknown')
    priority = fields.get('priority', {}).get('name', 'None')
    
    assignee = fields.get('assignee')
    assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
    
    # Get description
    description = fields.get('description', '')
    if isinstance(description, dict):
        desc_text = extract_text_from_adf(description)
    else:
        desc_text = description or 'No description'
    
    print(f"\n{'='*60}")
    print(f"📋 [{issue_key}] {summary}")
    print(f"{'='*60}")
    print(f"Type: {issue_type}")
    print(f"Status: {status}")
    print(f"Priority: {priority}")
    print(f"Assignee: {assignee_name}")
    print(f"\nDescription:")
    print(desc_text[:200] + ('...' if len(desc_text) > 200 else ''))
    print(f"{'='*60}\n")


def extract_text_from_adf(adf: dict) -> str:
    """Extract text from Atlassian Document Format."""
    text_parts = []
    
    def extract(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                text_parts.append(node.get('text', ''))
            elif 'content' in node:
                for child in node['content']:
                    extract(child)
    
    extract(adf)
    return ' '.join(text_parts)


def determine_branch_type(issue_type: str) -> str:
    """Determine branch type from issue type."""
    type_map = {
        'bug': 'bugfix',
        'story': 'feature',
        'task': 'feature',
        'epic': 'feature',
        'subtask': 'feature',
        'improvement': 'feature'
    }
    return type_map.get(issue_type.lower(), 'feature')


def main():
    parser = argparse.ArgumentParser(
        description='Start work on Jira ticket - full automated workflow'
    )
    
    parser.add_argument('--ticket', '-t', required=True, help='Jira ticket ID (e.g., PROJ-123)')
    parser.add_argument('--branch-type', choices=['feature', 'bugfix', 'hotfix', 'refactor'], 
                       help='Branch type (auto-detected if not specified)')
    parser.add_argument('--no-status-update', action='store_true', 
                       help='Skip updating ticket status')
    parser.add_argument('--no-comment', action='store_true',
    parser.add_argument('--profile', '-p', help='Jira profile to use (from .jira-config)')
    
    args = parser.parse_args()
    
    if args.profile:
        print(f"🔍 Using profile: {args.profile}")
    print(f"🚀 Starting work on {args.ticket}...\n")
    
    # Initialize Jira client
    try:
        client = JiraClient(args.profile
        client = JiraClient()
    except Exception as e:
        print(f"❌ Failed to initialize Jira client: {e}")
        sys.exit(1)
    
    # Fetch ticket
    try:
        print(f"📥 Fetching ticket details...")
        issue_data = client.get_issue(args.ticket)
        print(f"✓ Fetched ticket")
    except Exception as e:
        print(f"❌ Failed to fetch ticket: {e}")
        sys.exit(1)
    
    # Display ticket info
    display_ticket_info(issue_data)
    
    # Determine branch type
    fields = issue_data['fields']
    issue_type = fields.get('issuetype', {}).get('name', 'Story')
    branch_type = args.branch_type or determine_branch_type(issue_type)
    
    # Create branch
    summary = fields.get('summary', 'no-summary')
    branch_name = create_branch(args.ticket, summary, branch_type)
    
    if not branch_name:
        print("❌ Failed to create branch")
        sys.exit(1)
    
    # Update ticket status
    if not args.no_status_update:
        try:
            print(f"🔄 Updating ticket status...")
            if client.transition_issue(args.ticket, 'In Progress'):
                print(f"✓ Updated status to 'In Progress'")
            else:
                print(f"⚠️  Could not update status (may already be in progress)")
        except Exception as e:
            print(f"⚠️  Status update failed: {e}")
    
    # Add comment
    if not args.no_comment:
        try:
            print(f"💬 Adding comment to ticket...")
            comment = f"Started working on this ticket in branch: {branch_name}"
            client.add_comment(args.ticket, comment)
            print(f"✓ Added comment")
        except Exception as e:
            print(f"⚠️  Failed to add comment: {e}")
    
    # Success summary
    print(f"\n{'='*60}")
    print(f"✅ Ready to work on {args.ticket}!")
    print(f"{'='*60}")
    print(f"Branch: {branch_name}")
    print(f"\nNext steps:")
    print(f"  1. Start coding")
    print(f"  2. Commit with: git commit -m '{args.ticket}: your message'")
    print(f"  3. Push when ready: git push origin {branch_name}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
