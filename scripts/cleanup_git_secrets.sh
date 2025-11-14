#!/bin/bash

# Git Secrets Cleanup Script
# This script removes sensitive data from Git history

set -e

echo "🚨 GIT SECRETS CLEANUP SCRIPT 🚨"
echo "================================"
echo ""
echo "⚠️  WARNING: This will rewrite Git history!"
echo "⚠️  Make sure you have a backup before proceeding."
echo ""

# Check if git filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo is not installed."
    echo ""
    echo "Install it with:"
    echo "  pip install git-filter-repo"
    echo ""
    echo "Or on macOS:"
    echo "  brew install git-filter-repo"
    exit 1
fi

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="../temporal-order-orchestrator-backup-$(date +%Y%m%d-%H%M%S)"
cp -r . "$BACKUP_DIR"
echo "✅ Backup created at: $BACKUP_DIR"
echo ""

# Create replacements file
echo "📝 Creating replacements file..."
cat > /tmp/git-replacements.txt << 'EOF'
# Replace exposed passwords
trellis===>***REMOVED***
# Add any other exposed secrets here
EOF

echo "✅ Replacements file created"
echo ""

# Show what will be replaced
echo "🔍 The following patterns will be replaced:"
cat /tmp/git-replacements.txt
echo ""

# Confirm
read -p "Continue with cleanup? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo ""
echo "🧹 Cleaning Git history..."
echo "This may take a few minutes..."
echo ""

# Run git filter-repo
git filter-repo \
    --replace-text /tmp/git-replacements.txt \
    --force

echo ""
echo "✅ Git history cleaned!"
echo ""

# Cleanup reflog
echo "🗑️  Cleaning up reflog..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the changes: git log --all --oneline | head -20"
echo "2. Force push to remote: git push origin --force --all"
echo "3. Force push tags: git push origin --force --tags"
echo "4. Notify team members to re-clone the repo"
echo ""
echo "⚠️  Remember to:"
echo "   - Change your database password"
echo "   - Update .env file with new password"
echo "   - Enable GitHub secret scanning"
echo ""

# Cleanup temp file
rm /tmp/git-replacements.txt
