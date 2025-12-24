#!/bin/bash
# Setup script for work-on-ticket skill

echo "🔧 Setting up work-on-ticket skill for Jira integration"
echo ""

# Check if environment variables are set
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "📝 You need to set up your Jira credentials"
    echo ""
    echo "1. Get your API token from:"
    echo "   https://id.atlassian.com/manage-profile/security/api-tokens"
    echo ""
    echo "2. Set environment variables:"
    echo "   export JIRA_URL='https://ihkreddy.atlassian.net'"
    echo "   export JIRA_EMAIL='your-email@example.com'"
    echo "   export JIRA_API_TOKEN='your-api-token'"
    echo ""
    echo "3. Add to your ~/.zshrc or ~/.bashrc to make permanent:"
    echo "   echo 'export JIRA_URL=\"https://ihkreddy.atlassian.net\"' >> ~/.zshrc"
    echo "   echo 'export JIRA_EMAIL=\"your-email@example.com\"' >> ~/.zshrc"
    echo "   echo 'export JIRA_API_TOKEN=\"your-api-token\"' >> ~/.zshrc"
    echo ""
    exit 1
fi

echo "✓ JIRA_URL: $JIRA_URL"
echo "✓ JIRA_EMAIL: $JIRA_EMAIL"
echo "✓ JIRA_API_TOKEN: [SET]"
echo ""

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing requests library..."
    pip3 install requests
fi

echo "✓ All dependencies installed"
echo ""
echo "🎉 Setup complete! You can now use:"
echo "   python scripts/fetch-ticket.py --ticket YOUR-TICKET-ID"
echo "   python scripts/start-work.py --ticket YOUR-TICKET-ID"
