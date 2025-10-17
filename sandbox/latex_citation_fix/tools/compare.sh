#!/bin/bash
# LaTeX Citation Fix - 比較工具
# 比較 agent_workspace 與 fixed/ 的差異

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_WS="$SANDBOX_ROOT/agent_workspace"
FIXED_DIR="$SANDBOX_ROOT/fixed"

echo "=== LaTeX Citation Fix - Compare Tool ==="
echo ""

# Check if directories exist
if [ ! -d "$AGENT_WS" ]; then
    echo "❌ Error: agent_workspace/ not found"
    exit 1
fi

if [ ! -d "$FIXED_DIR" ]; then
    echo "❌ Error: fixed/ directory not found"
    echo "This sandbox doesn't have a reference solution."
    exit 1
fi

echo "Comparing:"
echo "  Agent:     $AGENT_WS"
echo "  Reference: $FIXED_DIR"
echo ""

# Compare survey.tex
if [ -f "$AGENT_WS/survey.tex" ] && [ -f "$FIXED_DIR/survey.tex" ]; then
    echo "=== survey.tex differences ==="
    if diff -u "$FIXED_DIR/survey.tex" "$AGENT_WS/survey.tex" > /tmp/survey_diff.txt 2>&1; then
        echo "✅ No differences (identical to reference)"
    else
        echo "Found differences:"
        head -50 /tmp/survey_diff.txt
        echo ""
        echo "(Showing first 50 lines, full diff saved to /tmp/survey_diff.txt)"
    fi
    echo ""
fi

# Compare figs/
if [ -d "$AGENT_WS/figs" ] && [ -d "$FIXED_DIR/figs" ]; then
    echo "=== figs/ differences ==="
    
    diff_count=0
    for agent_file in "$AGENT_WS/figs"/*.tex; do
        filename=$(basename "$agent_file")
        fixed_file="$FIXED_DIR/figs/$filename"
        
        if [ -f "$fixed_file" ]; then
            if ! diff -q "$fixed_file" "$agent_file" > /dev/null 2>&1; then
                echo "📝 $filename: differs"
                diff_count=$((diff_count + 1))
            fi
        fi
    done
    
    if [ $diff_count -eq 0 ]; then
        echo "✅ No differences in figs/ (all identical)"
    else
        echo ""
        echo "Found differences in $diff_count file(s)"
        echo "Use 'diff <fixed_file> <agent_file>' for details"
    fi
    echo ""
fi

echo "=== Comparison complete ==="
