#!/bin/bash

# Automated release script for Data File Viewer

set -e

echo "🚀 Data File Viewer - Release Script"
echo "====================================="
echo ""

# Check if version argument is provided
if [ -z "$1" ]; then
    echo "❌ Error: Version number required!"
    echo "Usage: ./release.sh <version>"
    echo "Example: ./release.sh 1.0.1"
    exit 1
fi

VERSION=$1

echo "📝 Releasing version $VERSION"
echo ""

# Update version in package.json
echo "1️⃣ Updating package.json version..."
npm version $VERSION --no-git-tag-version

# Compile
echo "2️⃣ Compiling extension..."
npm run compile

# Run tests (if any)
echo "3️⃣ Running checks..."
npm run lint || true

# Commit changes
echo "4️⃣ Committing changes..."
git add package.json package-lock.json
git commit -m "chore: Bump version to $VERSION"

# Create git tag
echo "5️⃣ Creating git tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push changes and tag
echo "6️⃣ Pushing to GitHub..."
git push origin main
git push origin "v$VERSION"

echo ""
echo "✅ Release process initiated!"
echo ""
echo "GitHub Actions will now:"
echo "  - Build the extension"
echo "  - Create a GitHub release"
echo "  - Publish to Open VSX"
echo ""
echo "Monitor progress at:"
echo "  https://github.com/adityachaudhary99/data-file-viewer/actions"
echo ""
echo "🎉 Done!"
