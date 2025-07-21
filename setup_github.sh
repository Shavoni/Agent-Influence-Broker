#!/bin/bash

# GitHub Setup Script for Agent Influence Broker
# This script helps you set up GitHub connectivity and configuration

set -e

echo "🚀 GitHub Setup for Agent Influence Broker"
echo "==========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: This is not a git repository. Run 'git init' first."
    exit 1
fi

# Check if we have any commits
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "📝 No commits found. Let's create an initial commit..."
    
    # Add all files to staging
    git add .
    
    # Create initial commit
    git commit -m "Initial commit: Agent Influence Broker setup
    
    ✨ Features:
    - FastAPI application with async support
    - Supabase integration for data persistence
    - Agent management and negotiation system
    - Comprehensive test suite and CI/CD pipeline
    - Docker containerization support
    
    🔧 Configuration:
    - GitHub Actions workflows for CI/CD
    - Pre-commit hooks for code quality
    - Environment-based configuration
    - Security and linting checks"
    
    echo "✅ Initial commit created"
else
    echo "✅ Git repository already has commits"
fi

# Check if we have a remote
if git remote -v | grep -q "origin"; then
    echo "✅ GitHub remote 'origin' already configured"
    git remote -v
else
    echo ""
    echo "🔗 GitHub Remote Setup"
    echo "====================="
    echo "Please provide your GitHub repository details:"
    
    read -p "Enter your GitHub username: " github_username
    read -p "Enter your repository name (default: agent-influence-broker): " repo_name
    
    # Use default if no repo name provided
    if [ -z "$repo_name" ]; then
        repo_name="agent-influence-broker"
    fi
    
    # Add GitHub remote
    git remote add origin "https://github.com/$github_username/$repo_name.git"
    
    echo "✅ GitHub remote added: https://github.com/$github_username/$repo_name.git"
fi

# Check current branch and set main as default
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "🌿 Setting main as default branch..."
    git branch -M main
fi

# Push to GitHub
echo ""
echo "🚀 Ready to push to GitHub!"
echo "=========================="
echo "Run the following command to push your code:"
echo ""
echo "    git push -u origin main"
echo ""

# Environment setup reminder
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. 🔑 Set up GitHub Secrets:"
echo "   Go to: https://github.com/$github_username/$repo_name/settings/secrets/actions"
echo "   Add these secrets:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_ANON_KEY" 
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo ""
echo "2. 🔧 Create your .env file:"
echo "   cp .env.template .env"
echo "   # Then edit .env with your actual values"
echo ""
echo "3. 🧪 Test your setup:"
echo "   source .venv/bin/activate"
echo "   python -c \"from app.main import app; print('✅ Setup working!')\"" 
echo ""
echo "4. 🛡️ Enable branch protection (recommended):"
echo "   Go to: https://github.com/$github_username/$repo_name/settings/branches"
echo "   Add rule for 'main' branch with required status checks"
echo ""

echo "🎉 GitHub setup complete! Your Agent Influence Broker is ready for collaboration."
