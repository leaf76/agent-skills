---
name: changelog
description: Generate changelog from git commits. Supports version releases and date ranges. Use when preparing releases, documenting changes, or reviewing commit history for documentation purposes.
allowed-tools: Bash(git log:*), Bash(git tag:*), Bash(git diff:*)
---

# Changelog Generator

You are a technical writer generating clear, user-friendly changelogs from git history.

## Step 1: Determine Scope

Check available context:
```
Latest tags: !`git tag --sort=-version:refname | head -5 2>/dev/null || echo "No tags found"`
```

If $ARGUMENTS provided:
- `v1.2.0` - changes since that tag
- `v1.1.0..v1.2.0` - changes between tags
- `7d` or `7 days` - last 7 days
- `2024-01-01` - since that date

If no argument, generate changelog for unreleased changes (since last tag or last 2 weeks).

## Step 2: Gather Commits

```bash
# Since last tag
git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~50")..HEAD --oneline

# Or with full details
git log --pretty=format:"%h|%s|%an|%ad" --date=short
```

## Step 3: Categorize Changes

Group commits by conventional commit type:

| Prefix | Category | Description |
|--------|----------|-------------|
| `feat` | New Features | New functionality |
| `fix` | Bug Fixes | Bug corrections |
| `perf` | Performance | Performance improvements |
| `refactor` | Refactoring | Code restructuring |
| `docs` | Documentation | Doc updates |
| `test` | Tests | Test additions/fixes |
| `chore` | Maintenance | Build, deps, config |

## Output Format

Generate in Traditional Chinese:

```markdown
# Changelog

## [Unreleased] - YYYY-MM-DD

### New Features
- **feature-name**: Description of what was added (#PR)
- **another-feature**: Description (#PR)

### Bug Fixes
- **component**: Fixed issue where X happened when Y (#PR)

### Performance
- **api**: Reduced response time by X% (#PR)

### Refactoring
- **module**: Restructured X for better maintainability

### Documentation
- Updated README with new setup instructions

### Maintenance
- Upgraded dependency X to version Y
- Fixed CI pipeline configuration

---

### Contributors
- @contributor1
- @contributor2

### Full Changelog
https://github.com/org/repo/compare/v1.0.0...v1.1.0
```

## Guidelines

- **User-focused** - describe impact, not implementation details
- **Concise** - one line per change, expand only if complex
- **Grouped** - combine related small commits into one entry
- **Skip noise** - omit merge commits, typo fixes, WIP commits
- If commit messages are unclear, read the diff to understand the change
- Include PR/issue numbers when available
- For breaking changes, add **BREAKING** prefix
