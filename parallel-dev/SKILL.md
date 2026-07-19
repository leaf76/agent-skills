---
name: parallel-dev
description: Parallel development workflow using Git worktrees to run multiple Codex sessions without conflicts. Use when user mentions "parallel", "concurrent", "multiple sessions", "avoid conflicts", or wants to work on multiple features simultaneously.
---

# Parallel Development Skill

Enable conflict-free parallel Codex sessions using Git worktrees.

## When to Use

- User wants to develop multiple features simultaneously
- User experiences merge conflicts or git stash issues with multiple sessions
- User asks about running parallel Codex instances

## Setup Parallel Session

### Step 1: Create Worktree

```bash
# Get project name and create worktree
PROJECT_NAME=$(basename $PWD)
FEATURE_NAME="<feature>"
git worktree add "../${PROJECT_NAME}-${FEATURE_NAME}" "feature/${FEATURE_NAME}"
```

### Step 2: Initialize Scratchpad

Create coordination file in the new worktree:

```bash
mkdir -p "../${PROJECT_NAME}-${FEATURE_NAME}/.Codex"
cat > "../${PROJECT_NAME}-${FEATURE_NAME}/.Codex/scratchpad.md" << 'EOF'
## Current Task
Working on: <feature name>
Files being modified: <none yet>
Blocked on: <none>
Last updated: <timestamp>
EOF
```

### Step 3: Instruct User

Tell user:
```
Worktree created. Open a new terminal and run:
  cd ../<project>-<feature> && Codex
```

## Coordination Protocol

### Before Editing Shared Files

1. Read all `.Codex/scratchpad.md` files in sibling worktrees
2. Check if any session is modifying the same file
3. If conflict risk exists, wait or coordinate
4. Update own scratchpad before proceeding

### Shared File Examples
- Main entry points: `app.py`, `main.py`, `index.ts`
- Configuration: `pyproject.toml`, `package.json`
- Database models: `models.py`, `schema.prisma`
- Routing: `routes.py`, `urls.py`

### Safe to Parallel Edit
- Feature-specific modules in separate directories
- Test files for specific features
- Static assets and templates

## Merge Back to Main

```bash
# In the worktree
git add . && git commit -m "[<feature>] <description>"

# Return to main project
cd <main-project-dir>
git merge feature/<feature>

# Cleanup
git worktree remove ../<project>-<feature>
git branch -d feature/<feature>
```

## File Ownership Rules

When multiple sessions exist, each session should:
- Only modify files within its designated feature directory
- Create NEW files rather than editing shared ones when possible
- Use feature flags or separate endpoints instead of modifying core routing
- Complete isolated work first, integration changes last

## Scratchpad Update Protocol

Update `.Codex/scratchpad.md` when:
- Starting a new task
- Beginning to edit a file
- Completing a task
- Encountering a blocker

Format:
```markdown
## Current Task
Working on: <feature name>
Files being modified: <comma-separated list>
Blocked on: <description or "none">
Last updated: <YYYY-MM-DD HH:MM>
```
