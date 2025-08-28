#!/bin/bash

# Release script for Nosto Email Widgets MCP Server
# This script builds the package and prepares it for distribution

set -e

echo "🚀 Preparing release for Nosto Email Widgets MCP Server..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Get current version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 Current version: $VERSION"

# Build the package
echo "🔨 Building package..."
uv build

# Create dist directory if it doesn't exist
mkdir -p dist

# The built wheel is already in dist directory
echo "📁 Built package location: dist/"
ls -la dist/

echo "✅ Package built successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create a GitHub release with tag v$VERSION"
echo "2. Upload the wheel file from dist/ to the release"
echo "3. Update Cursor MCP config to use:"
echo "   uvx nosto-email-widgets-mcp@latest"
echo ""
echo "📁 Built package location: dist/"
