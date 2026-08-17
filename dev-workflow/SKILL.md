---
name: dev-workflow
description: Use when software work is multi-step, multi-file, risky, or validation-heavy, such as feature delivery, bug fixes, refactors, integration changes, or release preparation, and a structured engineering workflow is needed.
---

# Dev Workflow

## Overview

Use this skill as the default workflow controller for non-trivial engineering work. Keep the always-on rules in `AGENTS.md` in force, and use this skill to decide the execution order, required outputs, and when to route to supporting skills.

## Trigger Policy

- Apply when the task is multi-step, multi-file, risky, or requires structured verification.
- Apply when the user explicitly asks for `$dev-workflow`, a workflow, or a structured engineering process.
- Treat tasks as non-trivial by default when they touch business logic, critical paths, auth, permissions, payments, data mutation, public API contracts, shared reusable helpers, or cross-module integrations.
- Prefer changes that are small, self-contained, and easy to review; if a task mixes multiple concerns, split it or state why it must remain unified.
- Treat tasks as trivial only when they are clearly single-step, low-risk, and limited to narrow copy, styling, or other isolated changes that do not affect behavior, contracts, or shared logic.
- Skip only when the task is obviously low-risk and single-step; even then, continue following `AGENTS.md`.

## Routing

- Use `plan-mode` when the user explicitly wants a decision-complete plan before implementation.
- Use `fix-bug` for regressions, broken behavior, error reports, or root-cause-first debugging.
- For non-trivial bug work, keep `dev-workflow` as the outer controller and run `fix-bug` inside it for reproduce, RCA, bug-specific TDD, and regression verification.
- For trivial bug work, `fix-bug` can run alone as long as `AGENTS.md` guardrails still hold.
- Use `uiux-design` when the task depends on screenshots, snapshots, live UI evidence, usability review, or accessibility review; include layout review when layout evidence or responsive risk is present.
- Use `review-changes` when reviewing uncommitted changes or doing a final diff sanity check.
- Keep this skill as the parent workflow; route to supporting skills without giving up overall state tracking.

## Workflow

### 1. Clarify

- Restate the goal, success criteria, constraints, and explicit non-goals.
- Ask concise questions only when the missing information materially affects the change or risk profile.
- If the remaining unknowns do not materially change scope, acceptance criteria, or safety, state the assumption and continue instead of blocking.
- State the change rationale and any cross-change dependencies that reviewers or later maintainers must understand.
- Call out breaking-change, migration, security, or compatibility risk before editing.

### 2. Plan

- Produce a brief implementation plan in Traditional Chinese before making substantial edits.
- Include only what matters: goal, non-goals, likely files/modules, risk notes, test strategy, verification plan, and rollback approach.
- Include a brief reviewability plan when relevant: expected scope size, change rationale, dependency notes, and how the final diff will stay easy to review.
- For trivial tasks, abbreviate the plan rather than skipping it silently.
- For UI-only tasks, keep the plan concise but still spell out the required validation scope, including target viewports, interaction states, and evidence collection.

### 3. Worktree Check

- Inspect tracked, untracked, staged, and unrelated changes before editing.
- State the repo status, staged changes, unstaged changes, untracked files, task-scope files, untouched files, and any conflict risk.
- If the workspace is not a git repository, say so explicitly and still define the intended file scope before editing.
- If the workspace contains multiple concerns or pending dependencies, call out the reviewability risk and narrow the task scope before editing.
- Prefer narrow file scope; do not stash, revert, or clean without explicit approval.

### 4. TDD

- Write tests before implementation for business logic and critical paths.
- Treat auth, permissions, payments, and data mutation as mandatory TDD plus integration-test territory.
- Default to test-first work whenever a change touches public API contracts, shared reusable helpers, cross-module logic, or a bug with a reproducible case.
- Apply stronger test-first discipline when the task is high-risk, regression-prone, or contract-sensitive, but do not treat TDD as a ritual detached from feedback quality, iteration size, and verification value.
- For backend, shared logic, and API contract changes, prefer a failing automated test first.
- For reproducible bugs, start with a failing reproduction before fixing the code.
- For UI layout or visual regressions, create the smallest reliable browser, screenshot, or snapshot-based reproduction artifact before implementing the fix.
- For infrastructure or script changes, use the safest available pre-change proof such as dry-run output, sandbox validation, or a deterministic command sequence.
- If deterministic automated tests are not practical, create the smallest reliable reproduction artifact you can first, then state the manual verification plan and why automation is blocked.
- If TDD is skipped, explicitly state why and how correctness will be verified instead.

### 5. Implement

- Search existing code before adding new logic.
- Assess whether the affected block needs a small extraction or refactor for clarity and testability.
- Keep changes minimal, scoped, and consistent with the local style, types, and formatting rules.
- Stop and reassess when a change becomes long, multi-purpose, or hard to explain with a single rationale; split it or state why it must remain unified.
- Avoid unrelated refactors, dead code, commented-out code, and hidden behavior changes.
- Avoid hidden review burden: do not combine behavior changes, cleanup, renames, and refactors unless they are directly required for the task.
- Do not expand scope to fix adjacent issues unless they directly block the requested task; note them separately instead.
- Preserve existing UI/UX behavior unless the task explicitly requires a change.
- For backend or integration work, keep error handling explicit, avoid logging secrets, and preserve compatibility unless approved otherwise.

### 6. Summary

- Report what changed, where, and why.
- List updated files when useful.
- Include test results, executed checks, or reproducible validation steps.
- Explicitly note skipped checks, residual risks, key assumptions, and the rollback path when they matter.
- Include change rationale, dependency notes, and any residual reviewability risk when they matter.
- Note compatibility impact when relevant.
- Provide rollback notes and follow-up optimizations if they matter.

## Output Contract

- For significant tasks, surface sections in this order: `Clarify`, `Plan`, `Worktree Check`, `TDD`, `Implement`, `Summary`.
- Keep planning and explanations in Traditional Chinese.
- Keep code, comments, config, logs, UI strings, and commit messages in English.
- Keep intermediary updates short, factual, and tied to current progress.

## Suggested Short Templates

- Use compact section bodies by default; do not turn routine tasks into long reports.
- Adapt the template to the task, but keep the section order stable when the work is significant.
- For medium-risk tasks, sections may be brief and some low-signal fields may be merged, but do not silently skip risk, verification, or scope-control information.
- Do not omit `Worktree Check`, `TDD`, or `Summary` when the task touches business logic, auth, permissions, payments, data mutation, public API contracts, shared helpers, cross-module integrations, or a reproducible bug.
- For clearly low-risk implementation tasks, `Clarify` and `Plan` may be combined, and `Implement` may stay as a short progress note instead of a long narrative.
- If a section is abbreviated, keep the heading and state the minimum needed facts rather than dropping the section entirely.

### Clarify

- Goal:
- Success criteria:
- Constraints / non-goals:
- Change rationale / dependencies:
- Key risks:

### Plan

- Scope:
- Files or modules:
- Reviewability plan:
- Test strategy:
- Verification:
- Rollback:

### Worktree Check

- Repo status:
- Staged / unstaged / untracked:
- In scope:
- Explicitly untouched:
- Conflict / dependency risk:

### TDD

- Pre-change proof:
- Planned test or reproduction:
- Why automation is sufficient or blocked:

### Implement

- Current step:
- Intended code path:
- Scope control note:

### Summary

- Changed:
- Verified:
- Skipped / blocked:
- Reviewability / dependency notes:
- Risks / assumptions:
- Rollback:

## Example Snippets

### Low-Risk Change

- `Clarify + Plan`: Goal: update one button label without changing behavior. Scope: one component file. Reviewability plan: single-purpose diff, no adjacent cleanup.
- `Worktree Check`: Repo status: clean or reviewed. In scope: target component only. Explicitly untouched: shared helpers and layout styles.
- `TDD`: Pre-change proof: visual confirmation of current label. Why automation is blocked: copy-only change.
- `Implement`: Current step: update the label constant in the target component. Scope control note: do not combine copy cleanup in nearby files.
- `Summary`: Changed: one UI string. Verified: local spot check. Reviewability / dependency notes: no dependencies, no behavior change.

### Non-Trivial Bugfix

- `Clarify`: Goal: fix duplicated invoice creation after retry. Change rationale / dependencies: retry path and persistence layer must stay consistent.
- `Plan`: Files or modules: retry handler, persistence service, related tests. Reviewability plan: keep bugfix separate from refactor. Test strategy: failing regression test first.
- `Worktree Check`: In scope: retry flow files only. Conflict / dependency risk: avoid mixing unrelated queue cleanup already in workspace.
- `TDD`: Pre-change proof: reproducible request sequence causing duplicate writes. Planned test or reproduction: integration test covering retry idempotency.
- `Implement`: Current step: gate duplicate create on the existing idempotency path. Scope control note: no opportunistic queue refactor in the same diff.
- `Summary`: Changed: retry path now rejects duplicate create on repeated request. Verified: targeted test passes. Reviewability / dependency notes: no schema change; depends on existing idempotency key behavior.

### UI Issue

- `Clarify`: Goal: fix mobile modal close button overlap. Change rationale / dependencies: preserve desktop layout and existing modal behavior.
- `Plan`: Scope: modal shell styles and close button placement. Reviewability plan: keep style fix isolated from broader modal cleanup. Verification: mobile + desktop browser check.
- `Worktree Check`: Explicitly untouched: modal state logic, form validation, unrelated theme styles.
- `TDD`: Pre-change proof: mobile screenshot showing overlap. Planned test or reproduction: browser-based viewport check rather than unit test.
- `Implement`: Current step: adjust close control spacing and safe-area offset in modal shell styles. Scope control note: do not change modal interaction behavior.
- `Summary`: Changed: adjusted modal close control spacing and safe-area handling. Verified: mobile and desktop screenshots checked. Reviewability / dependency notes: layout-only change, no behavior dependency.

## Guardrails

- Keep `AGENTS.md` as the source of always-on rules; do not weaken it.
- Never hardcode secrets, concatenate SQL, swallow errors, or experiment in production.
- Explicitly mitigate common review blockers: oversized changes, mixed concerns, hidden dependencies, missing rationale, missing documentation, and missing tests.
- For user-facing work, cover loading, empty, error, disabled, and success states when they exist, and avoid leaking technical details.
- For API and server-side work, preserve backward compatibility unless approval says otherwise; return client-safe errors with `error`, `code`, and `trace_id`.
- For infrastructure work, state resource, config, permission, and blast-radius changes.

## Completion Criteria

- Only intended files are modified.
- Unrelated changes remain untouched.
- Verification matches the risk of the task.
- Any skipped tests, assumptions, or residual risks are made explicit.
