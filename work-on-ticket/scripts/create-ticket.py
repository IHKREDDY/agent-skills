#!/usr/bin/env python3
"""
Create a Jira Ticket and set up development workflow

Usage: python create-ticket.py --project SAM1 --summary "Ticket summary" --description "Detailed description"
"""

import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
import subprocess
import re
from jira_config import get_config


def create_jira_ticket(config, project_key, summary, description, issue_type="Task"):
    """Create a new Jira ticket."""
    auth = HTTPBasicAuth(config['email'], config['token'])
    url = f"{config['url']}/rest/api/3/issue"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Atlassian Document Format for description
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }
    
    response = requests.post(url, headers=headers, auth=auth, json=payload)
    
    if response.status_code == 201:
        data = response.json()
        return {
            "key": data["key"],
            "id": data["id"],
            "url": f"{config['url']}/browse/{data['key']}"
        }
    else:
        print(f"❌ Failed to create ticket: {response.status_code}")
        print(response.text)
        return None


def create_branch(ticket_key, summary):
    """Create a git branch for the ticket."""
    # Sanitize summary for branch name
    branch_name = summary.lower()
    branch_name = re.sub(r'[^a-z0-9\s-]', '', branch_name)
    branch_name = re.sub(r'\s+', '-', branch_name)
    branch_name = branch_name[:50]  # Limit length
    
    full_branch_name = f"feature/{ticket_key.lower()}-{branch_name}"
    
    # Create and checkout branch
    subprocess.run(["git", "checkout", "-b", full_branch_name], check=True)
    
    return full_branch_name


def push_branch(branch_name):
    """Push branch to remote."""
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)


def create_pull_request(branch_name, ticket_key, summary, ticket_url):
    """Create a pull request using GitHub CLI."""
    title = f"[{ticket_key}] {summary}"
    body = f"""## Jira Ticket
{ticket_url}

## Description
Implementing changes for {ticket_key}

## Changes
- [ ] Implementation complete
- [ ] Tests added
- [ ] Documentation updated
"""
    
    result = subprocess.run(
        ["gh", "pr", "create", "--title", title, "--body", body, "--base", "master"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        print(f"⚠️  PR creation failed: {result.stderr}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Create Jira ticket and development branch")
    parser.add_argument("--project", "-p", default="SAM1", help="Jira project key (default: SAM1)")
    parser.add_argument("--summary", "-s", required=True, help="Ticket summary/title")
    parser.add_argument("--description", "-d", default="", help="Ticket description")
    parser.add_argument("--type", "-t", default="Task", help="Issue type (default: Task)")
    parser.add_argument("--no-branch", action="store_true", help="Don't create git branch")
    parser.add_argument("--no-pr", action="store_true", help="Don't create pull request")
    
    args = parser.parse_args()
    
    # Get Jira config
    config = get_config()
    
    print(f"📝 Creating Jira ticket in {args.project}...")
    ticket = create_jira_ticket(
        config,
        args.project,
        args.summary,
        args.description or args.summary,
        args.type
    )
    
    if not ticket:
        exit(1)
    
    print(f"✓ Created ticket: {ticket['key']}")
    print(f"  URL: {ticket['url']}")
    
    if args.no_branch:
        return
    
    print(f"\n🌿 Creating git branch...")
    try:
        branch_name = create_branch(ticket['key'], args.summary)
        print(f"✓ Created branch: {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create branch: {e}")
        exit(1)
    
    print(f"\n📤 Pushing to GitHub...")
    try:
        push_branch(branch_name)
        print(f"✓ Pushed to origin/{branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push: {e}")
        exit(1)
    
    if args.no_pr:
        return
    
    print(f"\n🔀 Creating Pull Request...")
    pr_url = create_pull_request(branch_name, ticket['key'], args.summary, ticket['url'])
    
    if pr_url:
        print(f"✓ Created PR: {pr_url}")
    else:
        print("⚠️  Skipping PR creation (install GitHub CLI: brew install gh)")
    
    print(f"\n✅ Complete!")
    print(f"   Ticket: {ticket['url']}")
    print(f"   Branch: {branch_name}")
    if pr_url:
        print(f"   PR: {pr_url}")


if __name__ == "__main__":
    main()
