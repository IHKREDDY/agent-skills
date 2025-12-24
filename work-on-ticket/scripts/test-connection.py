#!/usr/bin/env python3
"""Quick test to verify Jira connection"""
import requests
from requests.auth import HTTPBasicAuth
import json
from jira_config import get_config

# Get credentials from project config
config = get_config()
base_url = config['url']
email = config['email']
api_token = config['token']

auth = HTTPBasicAuth(email, api_token)

print(f"Testing connection to: {base_url}")
print(f"Using email: {email}\n")

# Test 1: Check myself endpoint (simplest test)
print("Test 1: Authenticating...")
try:
    url = f"{base_url}/rest/api/3/myself"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    user_data = response.json()
    print(f"✓ Authentication successful!")
    print(f"  User: {user_data.get('displayName')}")
    print(f"  Account ID: {user_data.get('accountId')}\n")
except Exception as e:
    print(f"❌ Authentication failed: {e}\n")
    exit(1)

# Test 2: List projects
print("Test 2: Fetching projects...")
try:
    url = f"{base_url}/rest/api/3/project"
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    projects = response.json()
    
    if projects:
        print(f"✓ Found {len(projects)} project(s):")
        for proj in projects:
            print(f"  - {proj['key']}: {proj['name']}")
        print()
    else:
        print("⚠️  No projects found\n")
except Exception as e:
    print(f"❌ Error fetching projects: {e}\n")

# Test 3: Search for issues
print("Test 3: Searching for recent issues...")
try:
    url = f"{base_url}/rest/api/3/search"
    params = {
        'jql': 'order by created DESC',
        'maxResults': 5,
        'fields': 'summary,status,issuetype,key'
    }
    response = requests.get(url, auth=auth, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Search successful! Found {data['total']} total issue(s)")
        
        if data['issues']:
            print("\nRecent issues:")
            for issue in data['issues']:
                key = issue['key']
                summary = issue['fields']['summary']
                status = issue['fields']['status']['name']
                issue_type = issue['fields']['issuetype']['name']
                print(f"  [{key}] {summary}")
                print(f"      Type: {issue_type}, Status: {status}")
        else:
            print("\nNo issues found. Create your first ticket in Jira!")
    else:
        print(f"⚠️  Search returned status {response.status_code}")
        print(f"    This might mean no issues exist yet")
        
except Exception as e:
    print(f"ℹ️  Could not search issues: {e}")
    print("    This is OK if your Jira is empty")

print("\n" + "="*60)
print("✅ Connection test complete!")
print("="*60)
