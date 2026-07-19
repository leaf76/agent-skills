#!/bin/bash
# Parallel development worktree helper
# Usage: 
#   worktree.sh create <feature-name>  - Create new worktree
#   worktree.sh list                   - List all worktrees
#   worktree.sh remove <feature-name>  - Remove worktree
#   worktree.sh status                 - Show all scratchpad statuses

set -e

PROJECT_NAME=$(basename "$PWD")
PROJECT_DIR="$PWD"

create_worktree() {
    local feature="$1"
    local worktree_path="../${PROJECT_NAME}-${feature}"
    local branch="feature/${feature}"
    
    # Create worktree
    git worktree add "$worktree_path" -b "$branch" 2>/dev/null || \
    git worktree add "$worktree_path" "$branch"
    
    # Initialize scratchpad
    mkdir -p "${worktree_path}/.claude"
    cat > "${worktree_path}/.claude/scratchpad.md" << EOF
## Current Task
Working on: ${feature}
Files being modified: 
Blocked on: none
Last updated: $(date '+%Y-%m-%d %H:%M')
EOF
    
    echo "✓ Worktree created: $worktree_path"
    echo ""
    echo "Next step - open new terminal and run:"
    echo "  cd $worktree_path && claude"
}

list_worktrees() {
    echo "Active worktrees:"
    git worktree list
}

remove_worktree() {
    local feature="$1"
    local worktree_path="../${PROJECT_NAME}-${feature}"
    
    git worktree remove "$worktree_path"
    git branch -d "feature/${feature}" 2>/dev/null || true
    
    echo "✓ Worktree removed: $worktree_path"
}

show_status() {
    echo "Scratchpad statuses:"
    echo "===================="
    
    for scratchpad in ../*/.claude/scratchpad.md; do
        if [ -f "$scratchpad" ]; then
            local dir=$(dirname $(dirname "$scratchpad"))
            echo ""
            echo "[$dir]"
            cat "$scratchpad"
        fi
    done
}

case "${1:-}" in
    create)
        [ -z "${2:-}" ] && { echo "Usage: $0 create <feature-name>"; exit 1; }
        create_worktree "$2"
        ;;
    list)
        list_worktrees
        ;;
    remove)
        [ -z "${2:-}" ] && { echo "Usage: $0 remove <feature-name>"; exit 1; }
        remove_worktree "$2"
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {create|list|remove|status} [feature-name]"
        exit 1
        ;;
esac
