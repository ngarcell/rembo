#!/bin/bash

# GitHub Repository Setup Commands
# Run these commands after creating the repository on GitHub

echo "🚀 Pushing code to GitHub repository..."

# Push the code to GitHub
git push -u origin main

echo "✅ Code pushed successfully!"

echo "🔧 Next steps:"
echo "1. Go to https://github.com/ngarcell/rembo/settings/branches"
echo "2. Set up branch protection rules (see instructions below)"
echo "3. Configure repository settings"
echo "4. Set up GitHub Actions secrets if needed"

echo ""
echo "📋 Branch Protection Rules to Configure:"
echo "- Require pull request reviews before merging"
echo "- Require status checks to pass before merging"
echo "- Require branches to be up to date before merging"
echo "- Include administrators in restrictions"
echo "- Allow force pushes: NO"
echo "- Allow deletions: NO"
