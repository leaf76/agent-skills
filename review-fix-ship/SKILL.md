---
name: review-fix-ship
description: >-
  Coordinate end-to-end repository delivery: inspect local changes, review and
  repair actionable issues, verify the result, then commit, push, open a PR,
  and deploy through the project-approved release path. Use when the user
  explicitly wants one guarded flow such as review-and-ship, fix-and-deploy,
  take the current diff to release, or move a branch through validation and
  deployment. Stop and ask before unapproved production deploys, unclear
  environments, risky release actions, or missing acceptance criteria.
---

# Review Fix Ship

## Overview

Use this skill as an orchestration layer for repository work that must move from local changes to a releasable outcome. Reuse existing skills for review, bug fixing, lint repair, git publishing, and platform-specific deploys instead of duplicating their detailed procedures.

## Workflow

### 1. Clarify the target release lane

- Confirm the requested stop point: `review only`, `review + fix`, `ready to commit`, `push + PR`, `deploy`, or `full lane`.
- Confirm acceptance criteria, target environment, and whether production deploy is explicitly approved.
- If the user explicitly requested deploy and named the target environment in the current request or current release lane, treat that as deploy approval for the same final diff, deploy path, and target environment.
- Do not ask for deploy approval again after verification unless the scope, final diff, deploy path, target environment, database lane, infrastructure/config/permission blast radius, or rollback risk changes.
- If the user asks for an end-to-end flow but the environment, blast radius, or success criteria are unclear, stop and ask before modifying or shipping anything.

### 2. Inspect repository readiness

- Confirm the working directory is inside a git repository before proceeding.
- Inspect branch, remotes, worktree state, and any staged, unstaged, or unrelated changes.
- State which existing changes will remain untouched and which files are in scope.
- Read `references/deploy-discovery.md` when the deployment path is not already obvious from the repository.
- Inspect whether the diff changes schema, migrations, repositories, or data-access code that may require a database rollout step.
- If the worktree is dirty in ways that could create merge or release risk, stop and ask instead of force-cleaning or overwriting changes.

### 3. Review the current diff

- For non-trivial work, keep the execution discipline from `$dev-workflow`: clarify, plan, worktree check, validation-first implementation, and final summary.
- Use `review-changes` to review staged and unstaged changes before commit or push.
- Prioritize correctness, security, compatibility, and missing verification over style commentary.
- If the user asked for shipping but not for a review, still perform a focused release review before continuing.

### 4. Route fixes to the right helper skill

- Use `fix-bug` when the task is a bug, regression, broken behavior, or failure that needs RCA-first handling.
- Use `fix-lint` when the blockers are lint, formatting, or type-check issues.
- Apply direct edits only when the fix is small, local, and does not need a dedicated helper workflow.
- Keep fixes scoped to actionable findings that block the requested release lane. Do not broaden scope into unrelated cleanup.

### 5. Verify before shipping

- Run deterministic tests or the smallest reliable automated checks that match the risk of the change.
- For bug work, preserve the reproduce -> root cause -> fix -> regression verification order.
- For release work touching business logic, shared helpers, public contracts, auth, permissions, or data mutation, do not skip meaningful verification.
- If the diff changes migrations, schema, repository-layer SQL, or DB-backed invariants, verify the target database state explicitly instead of assuming code deploy is sufficient.
- For database-backed releases, check whether remote migrations are pending before deploy, and treat pending migrations as a release checklist item rather than an optional follow-up.
- If automation is not practical, provide a reproducible manual verification plan with concrete scenarios, inputs, and actual outcomes.
- Do not move to commit, push, or deploy while verification is missing, red, or materially incomplete.

### 6. Ship through the approved git path

- Only commit, push, or open a PR when the user asked for shipping or explicitly approved it.
- Prefer `github:yeet` or `yeet` for the branch, commit, push, and draft-PR flow.
- Keep commit messages and PR text aligned with the actual diff and validation evidence.
- If final review still finds blocking issues, stop before publishing.

### 7. Deploy through the approved platform path

- Use the repository's existing release path instead of inventing a new one.
- Prefer an existing deploy command, release script, CI workflow, or platform-specific skill.
- Use `cloudflare-deploy` for Cloudflare Workers, Pages, or related Cloudflare products.
- If the repository deploy path is unclear, read `references/deploy-discovery.md`, inspect the repo, and stop if the target path is still ambiguous.
- Never deploy to production without explicit user approval in the current release lane.
- Reuse earlier approval from the same release lane when the target environment, final diff, deploy path, database lane, blast radius, and rollback risk still match what was approved.
- If the release includes database changes, perform the database lane explicitly: discover pending remote migrations, apply them through the approved path, and verify the remote database is caught up before calling the deploy complete.
- When the code deploy and database rollout are separate commands, do not assume one implies the other; run and verify both lanes.
- When a deploy changes infrastructure, data, config, or permissions, state the blast radius and rollback path before running it.

### 8. Report the result clearly

- State where the flow stopped: review complete, fixes complete, committed, pushed, PR opened, deployed, or blocked.
- Summarize what changed, what was verified, and what remains risky or unverified.
- Include rollback notes when code was published or deployed.
- Call out any approvals that were required, obtained, or still missing.

## Routing

- Treat this skill as the parent controller for full release-lane work.
- Reuse `$dev-workflow` discipline for non-trivial engineering changes.
- Reuse `review-changes` for release review.
- Reuse `fix-bug` for RCA-first bug repair.
- Reuse `fix-lint` for lint, formatting, and type-check blockers.
- Reuse `github:yeet` or `yeet` for git publishing and PR creation.
- Reuse `cloudflare-deploy` when the deployment target is Cloudflare.

## Guardrails

- Keep existing `AGENTS.md` and project-specific guardrails in force at all times.
- Do not assume the user wants to commit, push, or deploy just because they asked for a review or a fix.
- Do not auto-deploy after a successful push unless the repository's approved path does that by design and the user approved the target environment.
- Do not require duplicate approval at the final deploy step when the user already approved that target environment for the same release lane and no material deploy risk changed.
- Do not ship schema-dependent code to production while remote migrations are still pending or unverified.
- Do not ship if there are unresolved blocking findings, unclear blast radius, or missing rollback notes for risky release actions.
- Prefer stopping with a precise explanation over guessing the deploy path or environment.

## References

- Read `references/gates.md` before commit, push, PR, or deploy actions.
- Read `references/deploy-discovery.md` when the repository's release path is not obvious.
