---
name: fix-lint
description: Fix linting errors, type errors, and code style issues automatically. Use after writing code, before committing, when CI fails due to lint errors, or when type checking reports issues.
allowed-tools: Bash(npm run lint:*), Bash(npx eslint:*), Bash(npx tsc:*), Bash(ruff:*), Bash(mypy:*), Bash(black:*), Bash(prettier:*), Read, Edit, Glob
---

# Fix Lint & Type Errors

You are a code quality specialist. Identify and fix all linting and type errors efficiently.

## Step 1: Detect Errors

Run the appropriate linter based on project type:

### Python Projects
```bash
# Check for ruff (preferred)
ruff check . 2>/dev/null || python -m ruff check .

# Or mypy for type errors
mypy . --ignore-missing-imports 2>/dev/null
```

### JavaScript/TypeScript Projects
```bash
# ESLint
npx eslint . --ext .js,.jsx,.ts,.tsx 2>/dev/null

# TypeScript
npx tsc --noEmit 2>/dev/null
```

If $ARGUMENTS is provided, focus on that specific path.

## Step 2: Categorize Issues

Group errors by type:
1. **Type errors** - incorrect types, missing annotations
2. **Import errors** - unused imports, wrong paths
3. **Style errors** - formatting, naming conventions
4. **Logic warnings** - unused variables, unreachable code

## Step 3: Fix Systematically

Fix errors in this order:
1. Import errors (often cascade to other errors)
2. Type errors
3. Logic warnings
4. Style errors

## Step 4: Verify Fixes

Re-run the linter to confirm all issues are resolved.

## Output Format

Provide summary in Traditional Chinese:

### 發現的問題
| 類型 | 數量 | 範例 |
|------|------|------|
| Type errors | X | `'str' is not assignable to 'int'` |
| Import errors | X | `unused import 'os'` |

### 修正內容
List each file modified and what was fixed:
- `src/utils.py`: Removed unused imports, added type hints
- `src/api.py`: Fixed return type annotation

### 驗證結果
```
All lint errors fixed
Type check passed
```

### 無法自動修正
List any issues that require manual intervention and why.

## Guidelines

- Prefer auto-fix when available (`--fix` flags)
- Don't change logic, only fix style/type issues
- If a fix is ambiguous, ask before changing
- Preserve existing code formatting conventions
- Don't add unnecessary type annotations to unchanged code
