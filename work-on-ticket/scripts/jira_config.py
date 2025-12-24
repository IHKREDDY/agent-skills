#!/usr/bin/env python3
"""
Configuration Manager for Multiple Jira Sites

Reads from .jira-config file to support multiple Jira instances
"""

import os
import configparser
from typing import Dict, Optional
from pathlib import Path


class JiraConfig:
    def __init__(self, config_file: Optional[str] = None):
        if config_file is None:
            # Look for config file in project root (current working directory)
            # This works when running from any project that includes skills as submodule
            cwd = Path.cwd()
            config_file = cwd / '.jira-config'
            
            # Fallback: check in work-on-ticket directory (for standalone use)
            if not config_file.exists():
                script_dir = Path(__file__).parent.parent
                config_file = script_dir / '.jira-config'
        
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            print(f"⚠️  Config file not found: {self.config_file}")
            print("    Using environment variables instead")
    
    def get_profile(self, profile_name: Optional[str] = None) -> Dict[str, str]:
        """Get Jira credentials for a specific profile."""
        
        # Try config file first
        if self.config_file.exists():
            if profile_name is None:
                # Use default profile
                profile_name = self.config.get('DEFAULT', 'default_profile', fallback='ihkreddy')
            
            if profile_name in self.config:
                profile = self.config[profile_name]
                return {
                    'url': profile.get('url'),
                    'email': profile.get('email'),
                    'token': profile.get('token')
                }
            else:
                print(f"⚠️  Profile '{profile_name}' not found in config")
        
        # Fall back to environment variables
        return {
            'url': os.environ.get('JIRA_URL', 'https://ihkreddy.atlassian.net'),
            'email': os.environ.get('JIRA_EMAIL'),
            'token': os.environ.get('JIRA_API_TOKEN')
        }
    
    def list_profiles(self) -> list:
        """List all available profiles."""
        profiles = []
        for section in self.config.sections():
            if section != 'DEFAULT':
                profiles.append(section)
        return profiles
    
    def validate_profile(self, credentials: Dict[str, str]) -> bool:
        """Validate that all required credentials are present."""
        required = ['url', 'email', 'token']
        for key in required:
            if not credentials.get(key):
                print(f"❌ Missing {key} in configuration")
                return False
        return True


def get_config(profile: Optional[str] = None) -> Dict[str, str]:
    """Convenience function to get Jira configuration."""
    config = JiraConfig()
    credentials = config.get_profile(profile)
    
    if not config.validate_profile(credentials):
        print("\n📝 Set up credentials either:")
        print("1. In work-on-ticket/.jira-config file")
        print("2. As environment variables (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)")
        exit(1)
    
    return credentials


if __name__ == '__main__':
    # Test configuration
    config = JiraConfig()
    
    print("Available Jira profiles:")
    profiles = config.list_profiles()
    
    if profiles:
        for profile in profiles:
            creds = config.get_profile(profile)
            print(f"\n[{profile}]")
            print(f"  URL: {creds['url']}")
            print(f"  Email: {creds['email']}")
            print(f"  Token: {'*' * 20}")
    else:
        print("  No profiles configured")
        print(f"  Create profiles in: {config.config_file}")
