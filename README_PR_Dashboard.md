# 📊 PR Dashboard for Last 20 Days

## 🎯 Purpose
This dashboard provides daily pull request creation statistics for any GitHub repository over the last 20 days, perfect for tracking development activity and team productivity.

## 🚀 Quick Start

### For MarketingDataEngineering Repository:
```bash
# Run dashboard for your specific repository
./pr_dashboard.sh OWNER/MarketingDataEngineering

# Examples:
./pr_dashboard.sh gnrtech/MarketingDataEngineering
./pr_dashboard.sh yourorg/MarketingDataEngineering
```

### For Any Repository:
```bash
# General usage
./pr_dashboard.sh [OWNER/REPO_NAME]

# If no repository specified, defaults to current repo
./pr_dashboard.sh
```

## 📋 What You Get

### 1. Daily Breakdown (20 days)
```
2025-10-21   Mon │ 3   │ ███
2025-10-20   Sun │ 1   │ █
2025-10-19   Sat │ 0   │ ░
2025-10-18   Fri │ 5   │ █████
```

### 2. Weekly Summary
- Last 7 days: X PRs
- Previous 7 days: Y PRs  
- Trend analysis (% change)

### 3. Top Contributors
- Author rankings by PR count
- Activity distribution

### 4. PR State Analysis
- Open vs Closed vs Merged counts
- Success rates

## 🔧 Setup Requirements

The script automatically checks for required tools:
- `gh` (GitHub CLI) - for API access
- `jq` - for JSON parsing
- `bc` - for calculations

## 📝 Sample Output

```
🔍 PR Dashboard for Repository: gnrtech/MarketingDataEngineering
📅 Analyzing last 20 days
==================================================
📊 Date range: 2025-10-01 to 2025-10-21

✅ Repository found: gnrtech/MarketingDataEngineering

📋 PR Summary:
   #123 - Add new data pipeline by @john_doe [merged]
   #124 - Fix ETL bug by @jane_smith [open]
   #125 - Update documentation by @dev_team [closed]

📊 DAILY PR CREATION DASHBOARD
================================
2025-10-21   Mon │ 2   │ ██
2025-10-20   Sun │ 0   │ ░
2025-10-19   Sat │ 1   │ █
2025-10-18   Fri │ 3   │ ███
2025-10-17   Thu │ 1   │ █
2025-10-16   Wed │ 0   │ ░
2025-10-15   Tue │ 2   │ ██
...

📈 WEEKLY SUMMARY
==================
Last 7 days:     8 PRs
Previous 7 days: 5 PRs
📈 Trend: +60.0% (increasing)

👥 TOP CONTRIBUTORS (Last 20 days)
=====================================
john_doe: 5 PRs
jane_smith: 3 PRs
dev_team: 2 PRs

🏷️  PR STATES
==============
merged: 7 PRs
open: 2 PRs
closed: 1 PR
```

## 🎯 Use Cases

### Daily Standup
- Quick overview of yesterday's PR activity
- Identify busy/quiet periods

### Sprint Planning
- Analyze team velocity trends
- Plan capacity based on historical data

### Team Management
- Track individual contributor activity
- Identify collaboration patterns

### Project Health
- Monitor development momentum
- Spot potential bottlenecks

## 🔍 Troubleshooting

### Repository Not Found
If you get "Repository not found":
1. Check the repository name spelling
2. Ensure you have access to the repository
3. Verify the organization/owner name
4. Try: `gh repo list OWNER` to see available repos

### Authentication Issues
```bash
# Login to GitHub CLI
gh auth login

# Check current authentication
gh auth status
```

### Missing Tools
The script will guide you to install missing dependencies:
- Ubuntu/Debian: `sudo apt-get install jq bc`
- macOS: `brew install jq bc`

## 📊 Dashboard Legend

- `█` = 1 PR created
- `░` = No PRs created
- Numbers show exact count
- Dates in YYYY-MM-DD format
- Day abbreviations (Mon, Tue, etc.)

## 🔄 Automation

### Daily Reports
```bash
# Add to crontab for daily reports
0 9 * * * /path/to/pr_dashboard.sh owner/repo > /path/to/daily_report.txt
```

### Slack Integration
```bash
# Send to Slack channel
./pr_dashboard.sh owner/repo | curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"```'$(cat)'```"}' YOUR_SLACK_WEBHOOK_URL
```

## 🎨 Customization

Edit the script to:
- Change the number of days (modify `DAYS=20`)
- Add more PR states or filters
- Customize the visual representation
- Add email notifications
- Export to CSV/JSON formats

---
*Generated on $(date) - Update this dashboard anytime by running the script*