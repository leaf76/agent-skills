#!/bin/bash
# Generate changelog from git commits
set -e

FROM_REF="${1:-}"
TO_REF="${2:-HEAD}"
OUTPUT="${3:-CHANGELOG.md}"

# Get the range
if [ -z "$FROM_REF" ]; then
    # Find the last tag
    FROM_REF=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)
fi

echo "📝 Generating changelog: ${FROM_REF}..${TO_REF}"
echo ""

# Header
echo "# Changelog" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "## $(git describe --tags 2>/dev/null || echo 'Unreleased') - $(date +%Y-%m-%d)" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Group commits by type
echo "### ✨ Features" >> "$OUTPUT"
git log "${FROM_REF}..${TO_REF}" --pretty=format:"- %s" --grep="^feat" 2>/dev/null >> "$OUTPUT" || true
echo "" >> "$OUTPUT"

echo "### 🐛 Bug Fixes" >> "$OUTPUT"
git log "${FROM_REF}..${TO_REF}" --pretty=format:"- %s" --grep="^fix" 2>/dev/null >> "$OUTPUT" || true
echo "" >> "$OUTPUT"

echo "### 📚 Documentation" >> "$OUTPUT"
git log "${FROM_REF}..${TO_REF}" --pretty=format:"- %s" --grep="^docs" 2>/dev/null >> "$OUTPUT" || true
echo "" >> "$OUTPUT"

echo "### 🔧 Other Changes" >> "$OUTPUT"
git log "${FROM_REF}..${TO_REF}" --pretty=format:"- %s" --invert-grep --grep="^feat" --grep="^fix" --grep="^docs" 2>/dev/null >> "$OUTPUT" || true
echo "" >> "$OUTPUT"

echo "✅ Changelog generated: ${OUTPUT}"
