# Routing

Use this file to keep `layout-review` narrowly scoped.

## Use `layout-review` when

- The user already has a screenshot, live UI, implemented page, or design artifact.
- The main complaint is layout quality rather than product strategy.
- The issue is primarily about:
  - spacing
  - alignment
  - centering
  - overflow
  - wrapping
  - clipping
  - responsive breakpoint behavior
  - grid or stack transformation
  - sticky or modal collision

## Route to `gemini-cli` when

- The request is still text-only.
- The user wants planning documents, PRD/UI spec, or handoff docs.
- The task is to define responsive rules before a UI exists.

## Route to `uiux-design` when

- The task expands beyond layout into broader UX, accessibility, or interaction review.
- Repo edits are required.
- Browser verification or responsive regression testing is required.
- The user wants implementation-ready UI deltas applied to code.

## Combined flow

Use this sequence when appropriate:

1. `layout-review` identifies the layout-only problem and writes the fix brief.
2. `uiux-design` applies the approved delta and runs browser verification.

Do not skip directly to implementation if the surface is not yet defined or the issue is still only a planning concern.
