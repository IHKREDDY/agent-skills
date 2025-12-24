# Jira API Reference

## Authentication

Jira Cloud uses **Basic Authentication** with API tokens.

```python
from requests.auth import HTTPBasicAuth
import requests

auth = HTTPBasicAuth(email, api_token)
headers = {'Accept': 'application/json'}

response = requests.get(url, auth=auth, headers=headers)
```

### Getting an API Token

1. Visit: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Agent Skills")
4. Copy and save the token securely
5. Never commit tokens to version control

## Common Endpoints

### Base URL
```
https://your-domain.atlassian.net
```

### Get Issue
```
GET /rest/api/3/issue/{issueIdOrKey}
```

**Parameters:**
- `fields`: Comma-separated list of fields to return
- `expand`: Additional data to include (changelog, renderedFields)

**Example:**
```python
url = f"{base_url}/rest/api/3/issue/PROJ-123"
params = {
    'fields': 'summary,description,status,assignee',
    'expand': 'changelog'
}
response = requests.get(url, auth=auth, params=params)
```

### Update Issue
```
PUT /rest/api/3/issue/{issueIdOrKey}
```

**Body:**
```json
{
  "fields": {
    "summary": "New summary",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [...]
    }
  }
}
```

### Transition Issue
```
POST /rest/api/3/issue/{issueIdOrKey}/transitions
```

**Get available transitions first:**
```
GET /rest/api/3/issue/{issueIdOrKey}/transitions
```

**Body:**
```json
{
  "transition": {
    "id": "21"
  }
}
```

### Add Comment
```
POST /rest/api/3/issue/{issueIdOrKey}/comment
```

**Body (Atlassian Document Format):**
```json
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "This is a comment"
          }
        ]
      }
    ]
  }
}
```

### Log Work
```
POST /rest/api/3/issue/{issueIdOrKey}/worklog
```

**Body:**
```json
{
  "timeSpent": "3h 20m",
  "comment": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "Work description"
          }
        ]
      }
    ]
  }
}
```

### Search Issues (JQL)
```
GET /rest/api/3/search
```

**Parameters:**
- `jql`: JQL query string
- `maxResults`: Max number of results (default 50)
- `startAt`: Starting index for pagination

**Example:**
```python
params = {
    'jql': 'assignee = currentUser() AND status = "To Do"',
    'maxResults': 50,
    'fields': 'summary,status,priority'
}
response = requests.get(f"{base_url}/rest/api/3/search", auth=auth, params=params)
```

### Assign Issue
```
PUT /rest/api/3/issue/{issueIdOrKey}/assignee
```

**Body:**
```json
{
  "accountId": "5b10ac8d82e05b22cc7d4ef5"
}
```

### Get User
```
GET /rest/api/3/user
```

**Parameters:**
- `accountId`: User's account ID
- `emailAddress`: User's email (deprecated)

## Atlassian Document Format (ADF)

Jira Cloud uses ADF for rich text fields like descriptions and comments.

### Basic Text
```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "This is a paragraph"
        }
      ]
    }
  ]
}
```

### Heading
```json
{
  "type": "heading",
  "attrs": { "level": 1 },
  "content": [
    { "type": "text", "text": "Heading Text" }
  ]
}
```

### Bullet List
```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [
            { "type": "text", "text": "Item 1" }
          ]
        }
      ]
    }
  ]
}
```

### Code Block
```json
{
  "type": "codeBlock",
  "attrs": { "language": "python" },
  "content": [
    { "type": "text", "text": "print('Hello')" }
  ]
}
```

## JQL (Jira Query Language)

### Basic Queries

**Your assigned tickets:**
```
assignee = currentUser()
```

**Open tickets:**
```
status = "To Do" OR status = "In Progress"
```

**High priority:**
```
priority = High
```

**Created recently:**
```
created >= -7d
```

**Specific project:**
```
project = PROJ
```

### Complex Queries

**Your open high-priority tickets:**
```
assignee = currentUser() AND status != Done AND priority = High
```

**Tickets updated this week:**
```
updated >= startOfWeek() ORDER BY updated DESC
```

**Tickets with specific label:**
```
labels = "backend" AND status = "In Progress"
```

### Useful Functions

- `currentUser()` - Current logged-in user
- `now()` - Current time
- `startOfDay()`, `startOfWeek()`, `startOfMonth()`
- `endOfDay()`, `endOfWeek()`, `endOfMonth()`

### Operators

- `=`, `!=` - Equality
- `>`, `>=`, `<`, `<=` - Comparison
- `~` - Contains (text search)
- `IN`, `NOT IN` - List membership
- `IS EMPTY`, `IS NOT EMPTY` - Null checks
- `WAS`, `WAS IN` - Historical values
- `CHANGED` - Field changed

## Rate Limits

Jira Cloud has rate limits:
- **Standard:** ~150 requests per second per IP
- **Bulk operations:** Lower limits apply

**Best practices:**
- Cache responses when possible
- Use bulk operations where available
- Implement exponential backoff for retries
- Monitor `X-RateLimit-*` headers

## Error Codes

- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (bad credentials)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (issue doesn't exist)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Response Headers

**Useful headers:**
```
X-RateLimit-Limit: 150
X-RateLimit-Remaining: 149
X-RateLimit-Reset: 1640000000
X-AREQUESTID: Request ID for support
```

## Pagination

Most list endpoints use pagination:

```python
start_at = 0
max_results = 50

while True:
    params = {
        'startAt': start_at,
        'maxResults': max_results
    }
    response = requests.get(url, auth=auth, params=params)
    data = response.json()
    
    issues = data['issues']
    if not issues:
        break
    
    # Process issues
    for issue in issues:
        process(issue)
    
    start_at += max_results
```

## Webhooks

Register webhooks to receive real-time updates:

```
POST /rest/api/3/webhook
```

**Events:**
- `jira:issue_created`
- `jira:issue_updated`
- `jira:issue_deleted`
- `comment_created`
- `worklog_created`

## Best Practices

1. **Use field filtering** to reduce response size
2. **Implement retries** with exponential backoff
3. **Cache data** where appropriate
4. **Use bulk APIs** for multiple operations
5. **Monitor rate limits** via headers
6. **Handle errors gracefully**
7. **Log API calls** for debugging
8. **Rotate API tokens** periodically
9. **Use specific permissions** (don't request admin)
10. **Test against sandbox** environment first

## Python Example: Complete Client

```python
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List

class JiraClient:
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(email, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_issue(self, issue_key: str) -> Dict:
        """Get issue details."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict]:
        """Search issues with JQL."""
        url = f"{self.base_url}/rest/api/3/search"
        params = {'jql': jql, 'maxResults': max_results}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()['issues']
    
    def add_comment(self, issue_key: str, text: str) -> Dict:
        """Add comment to issue."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        body = {
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [{
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': text}]
                }]
            }
        }
        response = self.session.post(url, json=body)
        response.raise_for_status()
        return response.json()
```

## Resources

- [Jira Cloud REST API Docs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [JQL Reference](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [API Token Management](https://id.atlassian.com/manage-profile/security/api-tokens)
