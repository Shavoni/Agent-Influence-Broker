#!/bin/bash

# Script to create a test Pull Request for Agent Influence Broker
# This helps verify that your PR workflow is working correctly

set -e

echo "🔧 Creating Test Pull Request for Agent Influence Broker"
echo "======================================================"

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️ Warning: You're not on main branch. Switching to main..."
    git checkout main
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Create test branch
test_branch="feature/test-pr-workflow-$(date +%Y%m%d-%H%M%S)"
echo "🌿 Creating test branch: $test_branch"
git checkout -b "$test_branch"

# Make a small test change
echo "📝 Making test changes..."
echo "
## 🧪 Test PR Workflow - $(date)

This is a test PR created to verify the Pull Request workflow is functioning correctly.

### Changes Made:
- Added this test documentation
- Verified branch protection rules
- Tested automated CI/CD pipeline

### Expected Behavior:
- ✅ PR validation should run
- ✅ Code quality checks should pass
- ✅ Security scans should complete
- ✅ PR size analysis should show 'small'
- ✅ Automated comment should appear

**This PR can be safely merged or closed after testing.**
" > TEST_PR_WORKFLOW.md

# Add and commit the test change
git add TEST_PR_WORKFLOW.md
git commit -m "🧪 Test PR workflow setup

This commit tests the Pull Request workflow including:
- Automated CI/CD pipeline validation
- Code quality checks (formatting, linting)
- Security scanning (Bandit, Safety)
- PR size analysis
- Automated status reporting

The test file can be removed after verification."

# Push the test branch
echo "🚀 Pushing test branch..."
git push -u origin "$test_branch"

# Instructions for creating the PR
echo ""
echo "✅ Test branch created and pushed!"
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Go to your GitHub repository"
echo "2. You should see a banner to create a PR for '$test_branch'"
echo "3. Click 'Compare & pull request'"
echo "4. Fill out the PR template"
echo "5. Submit the PR"
echo "6. Watch the automated checks run!"
echo ""
echo "📍 Direct link:"
echo "https://github.com/YOUR_USERNAME/agent-influence-broker/compare/main...$test_branch"
echo ""
echo "🔍 What to look for:"
echo "- PR validation workflow should start automatically"
echo "- Code quality checks should pass"
echo "- Security scans should complete"
echo "- PR size should be marked as 'small'"
echo "- Automated summary comment should appear"
echo ""
echo "🧹 Cleanup:"
echo "After testing, you can:"
echo "- Delete the test PR"
echo "- Delete the test branch"
echo "- Remove TEST_PR_WORKFLOW.md file"
echo ""
echo "🎉 Happy coding with Pull Requests!"
