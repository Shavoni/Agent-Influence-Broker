#!/bin/bash

# IMMEDIATE GitHub Backup Script for Agent Influence Broker
# Run this IMMEDIATELY after creating your GitHub repository

echo "🚀 PUSHING AGENT INFLUENCE BROKER TO GITHUB"
echo "=============================================="

# Check if we have commits
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "❌ Error: No commits found. Something went wrong."
    exit 1
fi

echo "✅ Found $(git rev-list --count HEAD) commits ready to push"

# Prompt for GitHub repository URL
echo ""
echo "📋 Please provide your GitHub repository details:"
read -p "Enter your GitHub username: " github_username
read -p "Enter repository name (press Enter for 'agent-influence-broker'): " repo_name

# Use default repo name if empty
if [ -z "$repo_name" ]; then
    repo_name="agent-influence-broker"
fi

# Construct repository URL
repo_url="https://github.com/$github_username/$repo_name.git"

echo ""
echo "🔗 Repository URL: $repo_url"
echo ""

# Check if remote already exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "⚠️ Remote 'origin' already exists. Updating URL..."
    git remote set-url origin "$repo_url"
else
    echo "🔗 Adding GitHub remote..."
    git remote add origin "$repo_url"
fi

# Verify remote
echo "✅ Remote configured:"
git remote -v

# Ensure we're on main branch
echo ""
echo "🌿 Ensuring main branch..."
git branch -M main

# Push to GitHub
echo ""
echo "🚀 PUSHING TO GITHUB..."
echo "======================="

if git push -u origin main; then
    echo ""
    echo "🎉 SUCCESS! Your Agent Influence Broker is now on GitHub!"
    echo "==============================================="
    echo ""
    echo "📍 Repository URL: https://github.com/$github_username/$repo_name"
    echo "📊 Files pushed: $(git ls-files | wc -l) files"
    echo "📝 Commits: $(git rev-list --count HEAD) commits"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Visit your repository: https://github.com/$github_username/$repo_name"
    echo "2. Set up branch protection: https://github.com/$github_username/$repo_name/settings/branches"
    echo "3. Add Supabase secrets: https://github.com/$github_username/$repo_name/settings/secrets/actions"
    echo "4. Test PR workflow: ./create-test-pr.sh"
    echo ""
    echo "🔐 Don't forget to add these secrets:"
    echo "- SUPABASE_URL"
    echo "- SUPABASE_ANON_KEY"
    echo "- SUPABASE_SERVICE_ROLE_KEY"
    echo ""
    echo "🎉 YOUR AGENT INFLUENCE BROKER IS LIVE!"
else
    echo ""
    echo "❌ Push failed. Possible issues:"
    echo "1. Repository doesn't exist at: $repo_url"
    echo "2. No access permissions to the repository"
    echo "3. Network connectivity issues"
    echo ""
    echo "📋 Double-check:"
    echo "- Repository exists and is accessible"
    echo "- You have push permissions"
    echo "- Repository URL is correct"
    echo ""
    echo "🔄 Try again or check GitHub repository settings"
fi
