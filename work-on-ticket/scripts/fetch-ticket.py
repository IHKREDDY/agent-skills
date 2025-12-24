#!/usr/bin/env python3
"""
Fetch Jira Ticket Details

Retrieves comprehensive information about a Jira ticket including
description, acceptance criteria, comments, and related issues.

Usage:
    python fetch-ticket.py --ticket PROJ-123
    python fetch-ticket.py --ticket PROJ-123 --format markdown
    python fetch-ticket.py --ticket PROJ-123 --include-comments
"""

import argparse
import os
import sys
import json
from typing import Dict, Any, Optional
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
        self.session.headers.update({'Accept': 'application/json'})
    
    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Fetch issue details from Jira."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        params = {
            'fields': 'summary,description,status,priority,assignee,reporter,issuetype,created,updated,comment,subtasks,parent'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("❌ Authentication failed. Check your JIRA_EMAIL and JIRA_API_TOKEN")
            elif e.response.status_code == 404:
                print(f"❌ Ticket {issue_key} not found")
            else:
                print(f"❌ HTTP Error: {e}")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error connecting to Jira: {e}")
            sys.exit(1)
    
    def get_transitions(self, issue_key: str) -> list:
        """Get available status transitions for the issue."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json().get('transitions', [])
        except:
            return []


def extract_acceptance_criteria(description: str) -> Optional[str]:
    """Extract acceptance criteria from description."""
    if not description:
        return None
    
    # Look for common AC markers
    markers = ['acceptance criteria', 'ac:', 'acceptance:', 'criteria:']
    desc_lower = description.lower()
    
    for marker in markers:
        if marker in desc_lower:
            idx = desc_lower.index(marker)
            # Get text after marker
            ac_text = description[idx:]
            return ac_text
    
    return None


def format_json(issue_data: Dict[str, Any]) -> str:
    """Format issue as JSON."""
    return json.dumps(issue_data, indent=2)


def format_markdown(issue_data: Dict[str, Any]) -> str:
    """Format issue as Markdown."""
    fields = issue_data['fields']
    issue_key = issue_data['key']
    
    # Basic info
    summary = fields.get('summary', 'No summary')
    issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
    status = fields.get('status', {}).get('name', 'Unknown')
    priority = fields.get('priority', {}).get('name', 'None')
    
    # People
    assignee = fields.get('assignee')
    assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
    
    reporter = fields.get('reporter')
    reporter_name = reporter.get('displayName', 'Unknown') if reporter else 'Unknown'
    
    # Description
    description = fields.get('description', '')
    if isinstance(description, dict):
        # Handle Atlassian Document Format
        description_text = extract_text_from_adf(description)
    else:
        description_text = description or 'No description'
    
    # Comments
    comments = fields.get('comment', {}).get('comments', [])
    
    # Build markdown
    md = f"# [{issue_key}] {summary}\n\n"
    md += f"**Type:** {issue_type}  \n"
    md += f"**Status:** {status}  \n"
    md += f"**Priority:** {priority}  \n"
    md += f"**Assignee:** {assignee_name}  \n"
    md += f"**Reporter:** {reporter_name}  \n"
    md += f"\n## Description\n\n{description_text}\n"
    
    # Try to extract acceptance criteria
    ac = extract_acceptance_criteria(description_text)
    if ac:
        md += f"\n## Acceptance Criteria\n\n{ac}\n"
    
    # Add comments if any
    if comments:
        md += f"\n## Comments ({len(comments)})\n\n"
        for comment in comments[:5]:  # Show last 5 comments
            author = comment.get('author', {}).get('displayName', 'Unknown')
            body = comment.get('body', '')
            if isinstance(body, dict):
                body = extract_text_from_adf(body)
            md += f"**{author}:**\n{body}\n\n"
    
    # Subtasks
    subtasks = fields.get('subtasks', [])
    if subtasks:
        md += f"\n## Subtasks ({len(subtasks)})\n\n"
        for subtask in subtasks:
            sub_key = subtask.get('key')
            sub_summary = subtask.get('fields', {}).get('summary', 'No summary')
            sub_status = subtask.get('fields', {}).get('status', {}).get('name', 'Unknown')
            md += f"- [{sub_key}] {sub_summary} ({sub_status})\n"
    
    return md


def extract_text_from_adf(adf: dict) -> str:
    """Extract plain text from Atlassian Document Format."""
    if not isinstance(adf, dict):
        return str(adf)
    
    text_parts = []
    
    def extract(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                text_parts.append(node.get('text', ''))
            elif 'content' in node:
                for child in node['content']:
                    extract(child)
        elif isinstance(node, list):
            for item in node:
                extract(item)
    
    extract(adf)
    return ' '.join(text_parts)


def format_plain(issue_data: Dict[str, Any]) -> str:
    """Format issue as plain text."""
    fields = issue_data['fields']
    issue_key = issue_data['key']
    
    summary = fields.get('summary', 'No summary')
    issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
    status = fields.get('status', {}).get('name', 'Unknown')
    
    output = f"Ticket: {issue_key}\n"
    output += f"Summary: {summary}\n"
    output += f"Type: {issue_type}\n"
    output += f"Status: {status}\n"
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description='Fetch Jira ticket details',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--ticket', '-t', required=True, help='Jira ticket ID (e.g., PROJ-123)')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'plain'], default='markdown', help='Output format')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--show-transitions', action='store_true', help='Show available status transitions')
    parser.add_argument('--profile', '-p', help='Jira profile to use (from .jira-config)')
    
    args = parser.parse_args()
    
    # Initialize client
    if args.profile:
        print(f"🔍 Using profile: {args.profile}")
    print(f"🔍 Fetching ticket {args.ticket}...\n")
    client = JiraClient(args.profile)
    
    # Fetch issue
    issue_data = client.get_issue(args.ticket)
    
    # Format output
    if args.format == 'json':
        output = format_json(issue_data)
    elif args.format == 'markdown':
        output = format_markdown(issue_data)
    else:
        output = format_plain(issue_data)
    
    # Show transitions if requested
    if args.show_transitions:
        transitions = client.get_transitions(args.ticket)
        output += "\n\n## Available Transitions\n\n"
        for trans in transitions:
            output += f"- {trans['name']} (ID: {trans['id']})\n"
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"✓ Saved to {args.output}")
    else:
        print(output)
    
    print(f"\n✓ Ticket {args.ticket} fetched successfully")


if __name__ == '__main__':
    main()
