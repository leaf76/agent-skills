---
name: review-changes
description: Review uncommitted git changes with a security-first, performance-aware, evidence-based workflow that relies on local diff inspection and targeted scans instead of mandatory external LLM analysis. Use before committing code, during code review, or when validating changes before pushing.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Read, Grep, Glob
---

# Git Change Review

You are an expert code reviewer. Review the uncommitted git changes systematically and ground every finding in the actual diff.

## Execution Checklist (MUST follow in order)

- [ ] Step 1: `git status --short`
- [ ] Step 1: `git diff` and `git diff --cached`
- [ ] Step 2: Identify changed files and review high-risk areas first
- [ ] Step 2: Review large/binary artifacts separately
- [ ] Step 2: Run targeted string scans for secrets and risky patterns on changed files when relevant
- [ ] Step 2: Keep the review local and evidence-based; do not require Gemini or other external LLM tools
- [ ] Step 3: Produce findings ordered by severity with file/line references
- [ ] Step 3: Add open questions or assumptions only after the findings

## Step 1: Gather Changes

Start with:

```text
Git status: !`git status --short`
```

Then inspect both staged and unstaged changes:

- `git diff --cached`
- `git diff`

If needed, identify the changed file list first:

```bash
git diff --name-only --cached
git diff --name-only
```

## Step 2: Review Systematically

Use the actual git diff, targeted searches, and direct file inspection as the primary evidence.
Do not block the review on Gemini or any other external LLM command.

Prioritize:

1. Auth, permissions, payments, data mutation, and migrations
2. Request parsing, validation, serialization, and error handling
3. Query paths, caching, loops, and async/concurrency logic
4. UI state handling and user-visible regressions
5. Tests that prove or fail to prove the change

Targeted scans that are often useful:

```bash
# Secret and sensitive marker scan on changed files
rg -n "password|secret|token|api[_-]?key|private key|BEGIN [A-Z ]+PRIVATE KEY" [changed_files]

# Query and command execution hotspots
rg -n "SELECT|INSERT|UPDATE|DELETE|query\\(|execute\\(|exec\\(|spawn\\(" [changed_files]

# Error-handling and logging hotspots
rg -n "catch \\{|except:|except Exception|console\\.error|logger\\.(info|debug|error)" [changed_files]
```

### Large/Binary Artifacts

If large or binary artifacts are changed (for example `*.pen`), review them separately instead of treating them as normal text diffs.

Minimum checks:

- Confirm they do not contain real credentials, tokens, or PII.
- Confirm placeholder values remain placeholders.
- If they are generated artifacts, verify the source-of-truth file was also reviewed.

## What to Look For

### Correctness

- Logic bugs and behavior regressions
- Missing edge-case handling
- Incorrect assumptions about data shape, ordering, or nullability

### Security

- SQL injection and unsafe query construction
- Missing auth or permission checks
- Input validation gaps
- Secret or PII exposure
- Unsafe redirects, XSS, CSRF, SSRF, or command execution issues

### Performance

- N+1 queries
- O(n^2) or repeated expensive work in loops
- Sequential async work that can block latency
- Large allocations or avoidable re-renders

### Reliability and Maintainability

- Silent error swallowing
- Missing or misleading logs
- Unclear branching and duplicated logic
- Missing tests for critical behavior

## Review Output Format

Provide the review in Traditional Chinese with the following structure:

### Findings
List only actionable findings first, ordered by severity. For each finding include:

1. Severity
2. File and line
3. The concrete problem
4. Why it matters
5. The recommended fix

If there are no findings, state that explicitly.

### Open Questions / Assumptions
Only include items that materially affect confidence in the review.

### Brief Summary
Short summary of the change scope and residual risk.

### Commit Suggestion
Suggest a conventional commit message when useful.

## Review Principles

- Prioritize correctness, then security, then maintainability, then performance.
- Do not invent issues that are not supported by the diff.
- Be specific and reference exact files and lines.
- Prefer a small number of high-signal findings over a long generic checklist.
- If evidence is insufficient, state the uncertainty plainly.
- Do not treat external LLM output as a required gate for completing the review.

## Important Notes

- Focus on the uncommitted changes, not the whole codebase.
- Review tests as part of the change, not as an afterthought.
- For frontend work, verify loading, empty, error, disabled, and success states when applicable.
- For server-side work, verify traceability, input validation, and safe error responses when applicable.
- If you optionally consult another tool, keep the final review grounded in the diff and your own verification.
