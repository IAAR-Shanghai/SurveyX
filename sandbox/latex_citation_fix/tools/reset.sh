#!/bin/bash
# LaTeX Citation Fix - 重置工具
# 將 agent_workspace 重置到初始狀態 (從 broken/ 複製)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_WS="$SANDBOX_ROOT/agent_workspace"
BROKEN_DIR="$SANDBOX_ROOT/broken"

echo "=== LaTeX Citation Fix - Reset Tool ==="
echo ""
echo "This will:"
echo "  1. Delete all files in agent_workspace/"
echo "  2. Copy fresh files from broken/"
echo ""
echo "Current workspace: $AGENT_WS"
echo ""
echo -n "Continue? (y/N): "
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Clear agent workspace
echo ""
echo "📁 Clearing agent workspace..."
rm -rf "$AGENT_WS"/*

# Recreate .gitignore
cat > "$AGENT_WS/.gitignore" << 'EOF'
# Agent workspace - ignore all generated files
*
!.gitignore
EOF

# Check if broken/ exists
if [ ! -d "$BROKEN_DIR" ]; then
    echo "❌ Error: broken/ directory not found at $BROKEN_DIR"
    echo "Please run the setup script first."
    exit 1
fi

# Copy broken files
echo "📋 Copying files from broken/..."
cp -r "$BROKEN_DIR"/* "$AGENT_WS/"

# Remove any .gitignore from broken (keep only workspace's .gitignore)
rm -f "$AGENT_WS/.gitignore"
cat > "$AGENT_WS/.gitignore" << 'EOF'
# Agent workspace - ignore all generated files
*
!.gitignore
EOF

echo ""
echo "✅ Reset complete!"
echo ""
echo "Agent workspace is now ready at:"
echo "  $AGENT_WS"
echo ""
echo "Start working:"
echo "  cd $AGENT_WS"
echo ""
