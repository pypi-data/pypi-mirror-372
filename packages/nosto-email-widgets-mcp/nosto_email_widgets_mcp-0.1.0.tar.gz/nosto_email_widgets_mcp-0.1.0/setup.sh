#!/bin/bash

# Nosto Email Widgets MCP Server Setup Script
# This script sets up the project using uv for dependency management

echo "🚀 Setting up Nosto Email Widgets MCP Server..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing dependencies..."
uv sync

echo "🔧 Installing development dependencies..."
uv sync --dev

echo "✅ Setup complete!"
echo ""
echo "To run the server:"
echo "  uv run python main.py"
echo ""
echo "To run tests:"
echo "  uv run pytest"
echo ""
echo "To format code:"
echo "  uv run black ."
echo "  uv run isort ."
echo ""
echo "To check types:"
echo "  uv run mypy ."
