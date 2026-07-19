---
name: fix-bug
description: Use when a user reports incorrect, regressed, flaky, failing, or unexpected software behavior that needs evidence-backed diagnosis and a safe fix.
---

# Fix Bug (Root Cause First)

Goal: fix bugs by addressing the **root cause**, not symptoms. For non-trivial bugs, keep `dev-workflow` as the outer controller and use this skill for reproduction, RCA, bug-specific TDD, and regression verification.

## Trigger Policy

- Apply when behavior is broken, regressed, flaky, failing in tests or production, or inconsistent with expected output.
- Treat bugs as non-trivial by default when they touch business logic, critical paths, auth, permissions, payments, data mutation, public API contracts, shared helpers, or cross-module integrations.
- Do not implement speculative permanent fixes. If evidence is incomplete, add the smallest safe instrumentation or ship only a reversible mitigation.

## Workflow

### 1. Understand + Reproduce

- Collect symptoms: error message, logs, inputs, environment, version, expected vs actual, affected users or surfaces, and known non-goals.
- Reproduce with the smallest reliable case.
- Prefer writing a failing test first to lock the behavior.
- If deterministic tests are not yet possible, capture the smallest reliable reproduction artifact first: script, fixture, log slice, request sample, browser/screenshot scenario, or telemetry query.
- For flaky or production-only bugs, use sampled logs, traces, source inspection, temporary instrumentation, and repeated attempts to separate signal from noise.
- If you cannot reproduce or explain the symptom, do not guess. Ask for missing context, add reversible instrumentation, or propose a reversible mitigation with the evidence gap clearly documented.

### 2. Root Cause Analysis (Mandatory)

Do not code until you can explain the root cause and show evidence.

Use:

- Static analysis: jump-to-def, find refs, type hovers, call hierarchy.
- Search: `rg` for keywords, error codes, feature flags, and state transitions.
- Git history: `git blame`, `git log -p`, and related PR context to learn intent.
- Data-flow tracing: input -> validation -> transformation -> side effect -> output.
- Hypothesis testing: form one hypothesis, verify or falsify it with test/log/source evidence, then continue.
- Instrumentation: temporary JSON logs with `trace_id` when applicable; never log secrets, tokens, passwords, OTPs, or sensitive personal data.

Required RCA output before implementation:

- Bug symptom:
- Reproduction artifact:
- Root cause:
- Evidence:
- Scope / blast radius:

### 3. Design the Fix

- Minimize blast radius; prefer small, atomic, reviewable changes.
- State the fix rationale and why it addresses the root cause rather than only the symptom.
- Preserve existing contracts unless the user explicitly approves a behavior or API change.
- If the fix becomes long, multi-purpose, or hard to explain with one rationale, split it or state why it must remain unified.
- If technical debt caused the bug, do only the smallest refactor that prevents recurrence and can be verified.

### 4. Implement + Verify

- Make the failing test pass, or make the reproduction artifact pass when automated tests are not practical.
- Run targeted tests first, then broader checks proportional to the risk.
- Verify success and failure paths when the bug touches state changes, permissions, schema, transactions, or external integrations.
- If only a mitigation was shipped, verify the mitigation path, document the evidence gap, and leave a clear next-step RCA plan.
- Remove temporary instrumentation before finalizing unless the user explicitly approves keeping it as production-safe observability.

### 5. Review + Document

- Re-review the diff for security, error handling, logging hygiene, compatibility, and hidden scope expansion.
- Confirm unrelated changes remain untouched.
- Update docs, developer notes, or runbooks when behavior, operations, or troubleshooting steps changed.

## Output Contract

- For significant bugs, report sections in this order: `Symptom`, `RCA`, `Fix`, `Verification`, `Risks`.
- Keep the answer concise, but do not omit reproduction evidence, root cause, verification, or remaining risk.
- If automation was skipped, state why and provide reproducible manual verification steps.

## Suggested Short Template

- Symptom:
- Reproduction artifact:
- Root cause:
- Evidence:
- Fix:
- Verified:
- Skipped / blocked:
- Risks / assumptions:
- Rollback:

## Example Snippets

### Reproducible API Bug

- `Symptom`: Retried `POST /invoices` creates duplicate invoices.
- `Reproduction artifact`: Integration test sends the same idempotency key twice and observes two rows.
- `Root cause`: Retry path bypasses the idempotency lookup before the create operation.
- `Fix`: Route retry creates through the existing idempotency guard without changing the public API.
- `Verified`: Failing regression test now passes; targeted invoice tests pass.

### Production-Only Flaky Bug

- `Symptom`: Checkout occasionally returns `500` after payment provider timeout.
- `Reproduction artifact`: Sampled logs with shared `trace_id` show timeout followed by a duplicate state transition.
- `Root cause`: Timeout handler retries a non-idempotent transition without checking current order state.
- `Fix`: Add state guard before retry and keep temporary safe metrics only if approved.
- `Verified`: Targeted state-transition test covers timeout retry; log query confirms no matching failures after mitigation window.
