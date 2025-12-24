#!/usr/bin/env python3
"""
Test API Endpoint

A simple script to test API endpoints with various HTTP methods,
headers, and request bodies.

Usage:
    python test-endpoint.py --url <URL> --method <METHOD> [OPTIONS]

Examples:
    # GET request
    python test-endpoint.py --url "https://api.example.com/users" --method GET
    
    # POST request with JSON body
    python test-endpoint.py --url "https://api.example.com/users" \
        --method POST \
        --data '{"name": "John", "email": "john@example.com"}'
    
    # With authentication
    python test-endpoint.py --url "https://api.example.com/users" \
        --method GET \
        --headers '{"Authorization": "Bearer your-token"}'
"""

import argparse
import json
import sys
from typing import Optional, Dict
import requests
from requests.exceptions import RequestException


def parse_json_arg(json_str: Optional[str]) -> Optional[Dict]:
    """Parse JSON string argument."""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)


def make_request(
    url: str,
    method: str,
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: int = 30
):
    """Make HTTP request and display results."""
    
    print(f"\n{'='*60}")
    print(f"Testing Endpoint: {method} {url}")
    print(f"{'='*60}\n")
    
    # Display request details
    if headers:
        print("Headers:")
        for key, value in headers.items():
            # Mask sensitive headers
            if key.lower() in ['authorization', 'x-api-key', 'api-key']:
                masked_value = value[:10] + '...' if len(value) > 10 else '***'
                print(f"  {key}: {masked_value}")
            else:
                print(f"  {key}: {value}")
        print()
    
    if params:
        print("Query Parameters:")
        for key, value in params.items():
            print(f"  {key}: {value}")
        print()
    
    if data:
        print("Request Body:")
        print(json.dumps(data, indent=2))
        print()
    
    # Make the request
    try:
        print("Sending request...\n")
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=data,
            params=params,
            timeout=timeout
        )
        
        # Display response
        print(f"Status Code: {response.status_code} {response.reason}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # Display response body
        print(f"\nResponse Body:")
        try:
            json_response = response.json()
            print(json.dumps(json_response, indent=2))
        except json.JSONDecodeError:
            print(response.text)
        
        # Display timing information
        print(f"\nTiming:")
        print(f"  Total time: {response.elapsed.total_seconds():.3f}s")
        
        # Display rate limit info if available
        rate_limit_headers = {
            k: v for k, v in response.headers.items() 
            if 'rate' in k.lower() or 'limit' in k.lower()
        }
        if rate_limit_headers:
            print(f"\nRate Limit Info:")
            for key, value in rate_limit_headers.items():
                print(f"  {key}: {value}")
        
        # Success/failure indicator
        print(f"\n{'='*60}")
        if 200 <= response.status_code < 300:
            print("✅ Request successful!")
        elif 400 <= response.status_code < 500:
            print("⚠️  Client error")
        elif 500 <= response.status_code < 600:
            print("❌ Server error")
        print(f"{'='*60}\n")
        
        return response.status_code
        
    except RequestException as e:
        print(f"❌ Request failed: {e}", file=sys.stderr)
        print(f"{'='*60}\n")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Test API endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--url',
        required=True,
        help='API endpoint URL'
    )
    
    parser.add_argument(
        '--method',
        default='GET',
        choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'],
        help='HTTP method (default: GET)'
    )
    
    parser.add_argument(
        '--headers',
        type=str,
        help='Request headers as JSON string'
    )
    
    parser.add_argument(
        '--data',
        type=str,
        help='Request body as JSON string (for POST/PUT/PATCH)'
    )
    
    parser.add_argument(
        '--params',
        type=str,
        help='Query parameters as JSON string'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Parse JSON arguments
    headers = parse_json_arg(args.headers)
    data = parse_json_arg(args.data)
    params = parse_json_arg(args.params)
    
    # Make request
    status_code = make_request(
        url=args.url,
        method=args.method,
        headers=headers,
        data=data,
        params=params,
        timeout=args.timeout
    )
    
    # Exit with appropriate code
    if status_code is None:
        sys.exit(1)
    elif status_code >= 400:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
