#!/bin/bash

# Publishing script for Data File Viewer extension

echo "🚀 Data File Viewer - Publishing Helper"
echo "========================================"
echo ""

# Check if publisher name is updated
if grep -q "your-publisher-name" package.json; then
    echo "❌ Error: Please update 'publisher' in package.json first!"
    echo "   Open package.json and change 'your-publisher-name' to your actual publisher name"
    exit 1
fi

echo "✅ Publisher name is set"
echo ""

# Check if icon exists
if [ ! -f "icon.png" ]; then
    echo "⚠️  Warning: icon.png not found"
    echo "   Consider creating a 128x128 PNG icon, or remove 'icon' field from package.json"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Compile
echo "📦 Compiling extension..."
npm run compile
if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi
echo "✅ Compilation successful"
echo ""

# Package
echo "📦 Packaging extension..."
npx vsce package
if [ $? -ne 0 ]; then
    echo "❌ Packaging failed!"
    exit 1
fi
echo "✅ Packaging successful"
echo ""

# Get version from package.json
VERSION=$(node -p "require('./package.json').version")
VSIX_FILE="data-file-viewer-${VERSION}.vsix"

echo "✅ Created: $VSIX_FILE"
echo ""
echo "Next steps:"
echo "1. Test locally: code --install-extension $VSIX_FILE"
echo "2. Create GitHub repo and push code"
echo "3. Publish to Open VSX: ovsx publish $VSIX_FILE"
echo ""
echo "See NEXT_STEPS.md for detailed instructions"
