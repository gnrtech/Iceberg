#!/bin/bash

# PR Dashboard Script for Last 20 Days
# Usage: ./pr_dashboard.sh [REPO_OWNER/REPO_NAME]
# Example: ./pr_dashboard.sh gnrtech/MarketingDataEngineering

REPO=${1:-"gnrtech/Iceberg"}
DAYS=20

echo "🔍 PR Dashboard for Repository: $REPO"
echo "📅 Analyzing last $DAYS days"
echo "=================================================="

# Get date 20 days ago
START_DATE=$(date -d "$DAYS days ago" +%Y-%m-%d)
echo "📊 Date range: $START_DATE to $(date +%Y-%m-%d)"
echo ""

# Check if repo exists
if ! gh repo view "$REPO" >/dev/null 2>&1; then
    echo "❌ Error: Repository '$REPO' not found or not accessible"
    echo ""
    echo "Available repositories in gnrtech:"
    gh repo list gnrtech --limit 20
    exit 1
fi

echo "✅ Repository found: $REPO"
echo ""

# Get PR data for last 20 days
echo "🔄 Fetching PR data..."
PR_DATA=$(gh pr list --repo "$REPO" --state all --limit 200 --json createdAt,number,title,author,state | jq --arg start_date "$START_DATE" '
    [.[] | select(.createdAt >= ($start_date + "T00:00:00Z")) | 
    {
        date: (.createdAt | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d")),
        number: .number,
        title: .title,
        author: .author.login,
        state: .state
    }] | sort_by(.date)
')

if [ "$PR_DATA" = "[]" ] || [ -z "$PR_DATA" ]; then
    echo "📭 No PRs found in the last $DAYS days"
    echo ""
    echo "📈 Overall repository stats:"
    TOTAL_PRS=$(gh pr list --repo "$REPO" --state all --limit 1000 --json number | jq length)
    echo "   Total PRs (all time): $TOTAL_PRS"
    exit 0
fi

echo "📋 PR Summary:"
echo "$PR_DATA" | jq -r '.[] | "   #\(.number) - \(.title) by @\(.author) [\(.state)]"'
echo ""

# Create daily dashboard
echo "📊 DAILY PR CREATION DASHBOARD"
echo "================================"

# Generate date range for last 20 days
for i in $(seq 0 $((DAYS-1))); do
    CURRENT_DATE=$(date -d "$i days ago" +%Y-%m-%d)
    DAY_NAME=$(date -d "$i days ago" +%a)
    
    # Count PRs for this date
    COUNT=$(echo "$PR_DATA" | jq --arg date "$CURRENT_DATE" '[.[] | select(.date == $date)] | length')
    
    # Create visual bar
    BAR=""
    if [ "$COUNT" -gt 0 ]; then
        for j in $(seq 1 $COUNT); do
            BAR="${BAR}█"
        done
    else
        BAR="░"
    fi
    
    printf "%-12s %-3s │ %-3s │ %s\n" "$CURRENT_DATE" "$DAY_NAME" "$COUNT" "$BAR"
done

echo ""
echo "📈 WEEKLY SUMMARY"
echo "=================="

# Last 7 days
LAST_WEEK=$(echo "$PR_DATA" | jq --arg start_date "$(date -d "7 days ago" +%Y-%m-%d)" '[.[] | select(.date >= $start_date)] | length')
# Previous 7 days (8-14 days ago)
PREV_WEEK=$(echo "$PR_DATA" | jq --arg start_date "$(date -d "14 days ago" +%Y-%m-%d)" --arg end_date "$(date -d "7 days ago" +%Y-%m-%d)" '[.[] | select(.date >= $start_date and .date < $end_date)] | length')
# Week before that (15-20 days ago)
OLDER_WEEK=$(echo "$PR_DATA" | jq --arg start_date "$(date -d "20 days ago" +%Y-%m-%d)" --arg end_date "$(date -d "14 days ago" +%Y-%m-%d)" '[.[] | select(.date >= $start_date and .date < $end_date)] | length')

echo "Last 7 days:     $LAST_WEEK PRs"
echo "Previous 7 days: $PREV_WEEK PRs"
echo "Older (6 days):  $OLDER_WEEK PRs"

# Calculate trend
if [ "$PREV_WEEK" -gt 0 ]; then
    TREND=$(echo "scale=1; ($LAST_WEEK - $PREV_WEEK) * 100 / $PREV_WEEK" | bc -l 2>/dev/null || echo "0")
    if (( $(echo "$TREND > 0" | bc -l 2>/dev/null || echo "0") )); then
        echo "📈 Trend: +${TREND}% (increasing)"
    elif (( $(echo "$TREND < 0" | bc -l 2>/dev/null || echo "0") )); then
        echo "📉 Trend: ${TREND}% (decreasing)"
    else
        echo "➡️  Trend: No change"
    fi
else
    echo "📊 Trend: Not enough data"
fi

echo ""
echo "👥 TOP CONTRIBUTORS (Last $DAYS days)"
echo "====================================="
echo "$PR_DATA" | jq -r 'group_by(.author) | map({author: .[0].author, count: length}) | sort_by(-.count) | .[] | "\(.author): \(.count) PRs"'

echo ""
echo "🏷️  PR STATES"
echo "=============="
echo "$PR_DATA" | jq -r 'group_by(.state) | map({state: .[0].state, count: length}) | sort_by(-.count) | .[] | "\(.state): \(.count) PRs"'

echo ""
echo "✨ Dashboard generated on $(date)"