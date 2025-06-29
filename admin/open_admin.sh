#!/bin/bash

# Admin Interface Launcher Script
# This script helps open the admin interface in the default browser

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADMIN_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(dirname "$ADMIN_DIR")"

echo -e "${BLUE}🛠️  Admin Interface Launcher${NC}"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "$ADMIN_DIR/admin_interface.html" ]; then
    echo "❌ Error: admin_interface.html not found in $ADMIN_DIR"
    echo "Make sure you're running this script from the admin directory"
    exit 1
fi

echo -e "${GREEN}✅ Admin interface found${NC}"
echo ""

# Determine the correct path
if [ -f "$ADMIN_DIR/index.html" ]; then
    ADMIN_URL="file://$ADMIN_DIR/index.html"
    echo "📁 Opening admin panel landing page..."
else
    ADMIN_URL="file://$ADMIN_DIR/admin_interface.html"
    echo "📁 Opening admin interface directly..."
fi

echo "🌐 URL: $ADMIN_URL"
echo ""

# Try to open in browser
if command -v xdg-open > /dev/null 2>&1; then
    # Linux
    echo "🚀 Opening in default browser..."
    xdg-open "$ADMIN_URL"
elif command -v open > /dev/null 2>&1; then
    # macOS
    echo "🚀 Opening in default browser..."
    open "$ADMIN_URL"
elif command -v start > /dev/null 2>&1; then
    # Windows
    echo "🚀 Opening in default browser..."
    start "$ADMIN_URL"
else
    echo "⚠️  Could not automatically open browser"
    echo "Please manually open: $ADMIN_URL"
fi

echo ""
echo -e "${GREEN}✅ Admin interface launched!${NC}"
echo ""
echo "📋 Quick Access:"
echo "  • Landing Page: file://$ADMIN_DIR/index.html"
echo "  • Direct Interface: file://$ADMIN_DIR/admin_interface.html"
echo ""
echo "📚 Documentation: file://$PROJECT_ROOT/docs/"
echo ""
echo "🔒 Remember: Admin access requires proper authentication!" 