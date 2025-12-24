# Quick Start: Jira Integration with work-on-ticket

## 🚀 Setup (5 minutes)

### Step 1: Get Your Jira API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name it: `Agent Skills`
4. Copy the token (you won't see it again!)

### Step 2: Configure Project (Edit .jira-config)

**This project is configured for https://ihkreddy.atlassian.net/**

Edit `work-on-ticket/.jira-config` and update your credentials:

```ini
# AgentSkills Project - Jira Configuration
[DEFAULT]
default_profile = ihkreddy

[ihkreddy]
url = https://ihkreddy.atlassian.net
email = your-email@example.com        ← Update this
token = your-api-token-here            ← Paste token here
```

**Note**: This file is in `.gitignore` - your credentials stay local.

### Step 3: Install Dependencies

```bash
pip3 install requests
```

Or run the setup script:
```bash
cd work-on-ticket/scripts
./setup.sh
```

## 📝 Basic Usage

### Fetch a Ticket

```bash
python work-on-ticket/scripts/fetch-ticket.py --ticket PROJ-123
```

### Start Work on a Ticket (Full Workflow)

```bash
python work-on-ticket/scripts/start-work.py --ticket PROJ-123
```

This automatically:
- ✅ Fetches ticket details
- ✅ Creates a feature branch (e.g., `feature/proj-123-add-user-auth`)
- ✅ Updates ticket status to "In Progress"
- ✅ Adds a comment to the ticket

## 🎯 Example Workflow

```bash
# 1. Start work on a ticket
python work-on-ticket/scripts/start-work.py --ticket PROJ-123

# Output:
# 🚀 Starting work on PROJ-123...
# ✓ Fetched ticket
# ✓ Created and checked out branch: feature/proj-123-add-user-authentication
# ✓ Updated status to 'In Progress'
# ✓ Added comment
# ✅ Ready to work on PROJ-123!

# 2. Work on your code
# ... edit files ...

# 3. Commit with ticket ID
git add .
git commit -m "PROJ-123: Implement OAuth authentication"

# 4. Push your branch
git push origin feature/proj-123-add-user-authentication

# 5. Create PR and you're done!
```

## 💡 Tips

### View Ticket in Markdown Format
```bash
python work-on-ticket/scripts/fetch-ticket.py --ticket PROJ-123 --format markdown
```

### Save Ticket Details to File
```bash
python work-on-ticket/scripts/fetch-ticket.py --ticket PROJ-123 --output ticket.md
```

### See Available Status Transitions
```bash
python work-on-ticket/scripts/fetch-ticket.py --ticket PROJ-123 --show-transitions
```

### Custom Branch Type
```bash
python work-on-ticket/scripts/start-work.py --ticket PROJ-456 --branch-type bugfix
```

## 🔍 Testing Your Connection

Quick test to verify your setup:

```bash
# Test 1: Check environment variables
echo "URL: $JIRA_URL"
echo "Email: $JIRA_EMAIL"
echo "Token: ${JIRA_API_TOKEN:0:10}..."

# Test 2: Fetch a ticket (replace with your actual ticket ID)
python work-on-ticket/scripts/fetch-ticket.py --ticket YOUR-TICKET-ID
```

## ❓ Troubleshooting

### "401 Unauthorized"
- Double-check your email and API token
- Ensure no extra spaces in environment variables
- Regenerate API token if needed

### "404 Not Found"
- Verify ticket ID format (must be uppercase: `PROJ-123`)
- Check that the ticket exists in your Jira
- Ensure you have permission to view the ticket

### "Transition not available"
- Some Jira workflows have restricted transitions
- Check available transitions with `--show-transitions` flag
- You may need to update the ticket manually in Jira first

## 🎉 What's Different from Zapier?

**Your local skill:**
- ✅ Fetches ticket details
- ✅ Creates git branches
- ✅ Updates ticket status
- ✅ Adds comments
- ✅ Works with your local git repo
- ✅ **100% under your control**

**Zapier MCP adds:**
- Multi-app orchestration (Jira + Slack + GitHub + etc.)
- Cloud-based execution
- Webhook triggers
- Enterprise features

**Both work great!** Your local version gives you full control and customization. Zapier adds cross-platform automation at scale.

## 🚀 Next Steps

1. **Create aliases** for faster access:
   ```bash
   alias jira-start="python ~/Agents/AgentSkills/work-on-ticket/scripts/start-work.py --ticket"
   alias jira-fetch="python ~/Agents/AgentSkills/work-on-ticket/scripts/fetch-ticket.py --ticket"
   ```

2. **Add to your team's workflow** - share the scripts with your team

3. **Customize** - modify the scripts to match your team's conventions

4. **Extend** - add more features like:
   - Automatic PR creation
   - Slack notifications
   - Time tracking
   - Sprint management

Enjoy your automated Jira workflow! 🎊
