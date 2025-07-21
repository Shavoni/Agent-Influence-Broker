# Branch Protection Setup for Agent Influence Broker

This guide helps you set up branch protection rules to enforce the Pull Request workflow.

## 🛡️ Recommended Branch Protection Rules

### For `main` branch:

1. **Go to Repository Settings**
   - Navigate to: `https://github.com/YOUR_USERNAME/agent-influence-broker/settings/branches`

2. **Add Rule for `main` branch:**
   ```
   Branch name pattern: main
   ```

3. **Enable these protections:**
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1
     - ✅ Dismiss stale PR approvals when new commits are pushed
     - ✅ Require review from code owners (if you add CODEOWNERS file)
   
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Required status checks:
       - `pr-validation`
       - `pr-size-check`
   
   - ✅ **Require conversation resolution before merging**
   - ✅ **Require signed commits** (optional, but recommended)
   - ✅ **Include administrators** (applies rules to admin users too)
   - ✅ **Restrict pushes that create files that exceed a given file size limit**: 100 MB

4. **Advanced Settings:**
   - ✅ **Allow force pushes**: ❌ (disabled for security)
   - ✅ **Allow deletions**: ❌ (disabled for safety)

## 🔄 Pull Request Workflow

With these settings, your workflow becomes:

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/new-agent-capability
   git push -u origin feature/new-agent-capability
   ```

2. **Make Changes & Commit:**
   ```bash
   git add .
   git commit -m "✨ Add new agent capability"
   git push
   ```

3. **Create Pull Request:**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Fill out the PR template
   - Submit for review

4. **Automated Checks Run:**
   - Code formatting validation
   - Linting and security scans
   - Tests execution
   - Build verification
   - PR size analysis

5. **Code Review Process:**
   - Team members review the code
   - Address feedback and make changes
   - All status checks must pass

6. **Merge to Main:**
   - Once approved and all checks pass
   - Use "Squash and merge" (recommended)
   - Delete feature branch after merge

## 👥 Code Owners (Optional)

Create a `.github/CODEOWNERS` file to automatically request reviews:

```
# Global owners
* @your-username

# API endpoints
/app/api/ @your-username @api-team

# Core configuration
/app/core/ @your-username @backend-team

# Database models
/app/models/ @your-username @database-team

# GitHub workflows
/.github/ @your-username @devops-team
```

## 🚀 Quick Setup Commands

After creating your GitHub repository, run:

```bash
# Push your main branch
git push -u origin main

# Create a development branch
git checkout -b develop
git push -u origin develop

# Create your first feature branch
git checkout -b feature/setup-pr-workflow
git add .
git commit -m "🔧 Add GitHub PR workflow configuration"
git push -u origin feature/setup-pr-workflow
```

Then create your first PR to test the workflow!

## 🎯 Benefits of This Setup

- ✅ **Code Quality**: Automated formatting and linting
- ✅ **Security**: Automated security scanning
- ✅ **Testing**: All tests must pass before merge
- ✅ **Review Process**: Required code reviews
- ✅ **Documentation**: Standardized PR templates
- ✅ **Visibility**: Clear status checks and summaries
- ✅ **Protection**: Main branch protected from direct pushes

## 🔧 Troubleshooting

**If status checks don't appear:**
1. Ensure GitHub Actions are enabled
2. Check that workflow files are in `.github/workflows/`
3. Verify branch names match workflow triggers

**If PR template doesn't show:**
1. Ensure file is at `.github/pull_request_template.md`
2. Template will show when creating new PRs

**If checks fail:**
1. Review the Actions tab for detailed logs
2. Fix issues and push new commits
3. Checks will automatically re-run
