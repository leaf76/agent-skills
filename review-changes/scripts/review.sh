#!/bin/bash
# Git change review helper
set -e

echo "📝 Git Change Review"
echo "===================="
echo ""

# Show summary
echo "📊 Summary"
echo "----------"
git status --short
echo ""

# Large/binary artifacts (e.g. Pencil .pen) should be reviewed separately.
PEN_CHANGED=$( { git diff --name-only -- '*.pen'; git diff --cached --name-only -- '*.pen'; } | sort -u )
if [ -n "$PEN_CHANGED" ]; then
    echo "🧩 Large artifacts detected (*.pen)"
    echo "-------------------------------"
    echo "$PEN_CHANGED"
    echo ""
    echo "NOTE: Review *.pen files separately for placeholder-only values and secret leakage."
    echo "  Minimum checks: placeholder URLs only, no real tokens, no private keys, no passwords."
    echo ""
fi

# Show stats
echo "📈 Stats"
echo "--------"
git diff --stat HEAD 2>/dev/null || git diff --stat
echo ""

# Staged changes
STAGED=$(git diff --cached --name-only)
if [ -n "$STAGED" ]; then
    echo "✅ Staged Changes"
    echo "-----------------"
    git diff --cached --stat
    echo ""
fi

# Unstaged changes
UNSTAGED=$(git diff --name-only)
if [ -n "$UNSTAGED" ]; then
    echo "⚠️  Unstaged Changes"
    echo "--------------------"
    git diff --stat
    echo ""
fi

# Untracked files
UNTRACKED=$(git ls-files --others --exclude-standard)
if [ -n "$UNTRACKED" ]; then
    echo "❓ Untracked Files"
    echo "------------------"
    echo "$UNTRACKED"
    echo ""
fi

# Show detailed diff for specific file
if [ -n "$1" ]; then
    echo "🔍 Detailed Diff: $1"
    echo "--------------------"
    git diff "$1"
fi

echo ""
echo "Commands:"
echo "  View full diff:  git diff"
echo "  Stage all:       git add -A"
echo "  Commit:          git commit -m 'message'"
echo "  Reset file:      git checkout -- <file>"
