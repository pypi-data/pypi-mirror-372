#!/bin/bash
set -e

# Release script for laneful
# Usage: ./scripts/release.sh 1.0.0

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.0"
    exit 1
fi

VERSION=$1

echo "🚀 Preparing release $VERSION"

# Validate version format
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Version must be in format x.y.z (e.g., 1.0.0)"
    exit 1
fi

# Check if we're on main branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "❌ Must be on main branch to release"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "❌ There are uncommitted changes"
    exit 1
fi

# Update version
echo "📝 Setting version to $VERSION"
python scripts/bump_version.py --release $VERSION

# Update CHANGELOG if it exists
if [ -f "CHANGELOG.md" ]; then
    echo "📝 Please update CHANGELOG.md with release notes"
    echo "Press Enter when ready to continue..."
    read
fi

# Commit version change
echo "💾 Committing version change"
git add pyproject.toml
if [ -f "CHANGELOG.md" ]; then
    git add CHANGELOG.md
fi
git commit -m "Release v$VERSION"

# Create and push tag
echo "🏷️  Creating tag v$VERSION"
git tag -a "v$VERSION" -m "Release v$VERSION"

echo "⬆️  Pushing changes and tag"
git push origin main
git push origin "v$VERSION"

echo "✅ Release $VERSION initiated!"
echo ""
echo "📦 GitHub Actions will now:"
echo "   1. Run tests"
echo "   2. Build package"
echo "   3. Publish to PyPI"
echo "   4. Create GitHub release"
echo ""
echo "🔗 Monitor progress at:"
echo "   https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/actions"
