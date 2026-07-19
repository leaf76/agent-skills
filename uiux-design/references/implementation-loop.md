# Implementation Loop

Use this reference when `uiux-design` moves from critique into real code changes.

## Preconditions

- There is actual UI evidence or an approved `handoff` / `prd-ui-spec` document.
- The target repo or workspace is clear enough to edit safely.
- The approved delta is specific about what must change and what must stay untouched.

## Loop

1. Capture the approved delta:
   - screen or component name
   - user-facing goal
   - exact copy, routes, callbacks, and component names that must stay unchanged
   - responsive rules
   - required states
   - explicit non-goals
2. Feed that delta into `scripts/implement_uiux.py`.
3. Require Gemini CLI to read existing code before editing.
4. Keep edits limited to task-related files.
5. Reject unrelated refactors, renamed design-system parts, or behavior changes not covered by the brief.
6. Review the resulting changes for drift before browser testing.
7. Start verification with `agent-browser`; use Chrome DevTools only when `agent-browser` is unavailable or cannot collect the evidence the task needs.

## Implementation brief checklist

- The brief names the target surface clearly.
- Locked copy and route names are listed under preserve rules.
- Existing interaction behavior is marked as preserve-by-default.
- Responsive behavior and edge states are explicit.
- Acceptance checks are concrete enough to verify in a browser.

## Exit criteria

- The code change is narrow and directly tied to the approved delta.
- Existing interaction patterns remain intact unless explicitly changed.
- Validation is ready to move into `agent-browser`, then Chrome DevTools fallback and, when needed, Playwright.
