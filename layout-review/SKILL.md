---
name: layout-review
description: Review Web/App UI layout issues from existing evidence and turn them into implementation-ready fix briefs. Use when Codex needs a layout-only lane for screenshots, live UI, implemented pages, or design artifacts that show spacing, alignment, centering, overflow, wrapping, breakpoint, grid, sticky, modal, or clipping problems. Do not use for text-only planning documents, broad UX critique, or direct repo implementation; route those to `gemini-cli` or `uiux-design` as appropriate.
---

# Layout Review

## Overview

Use this skill when the problem is specifically about layout quality in an existing Web/App UI surface. Focus on layout-only findings and remediation guidance, then hand the approved fix brief to `uiux-design` when repo edits or browser verification are required.

## Boundaries

- Use this skill for layout-only issues:
  - spacing inconsistency
  - alignment or centering drift
  - overflow, clipping, truncation, or wrapping failures
  - breakpoint or responsive layout regressions
  - grid, stack, column, card, table, toolbar, modal, or sticky element layout problems
- Do not widen the review into general UX critique unless the user explicitly asks for it.
- If the task starts from text-only requirements or planning notes, route to `gemini-cli`.
- If the task needs repo edits, browser automation, or post-build verification, route to `uiux-design` after producing the fix brief.

## Inputs

Prefer existing UI evidence:

- screenshots
- live UI observations
- implemented pages or components
- design artifacts with concrete layout problems

If the evidence is incomplete, ask for the smallest missing artifact needed to identify the layout issue reliably. Do not guess from vague descriptions when the viewport, state, or affected surface is unclear.

## Workflow

### 1. Gather and normalize evidence

- Identify the affected surface, state, and viewport first.
- Note whether the issue appears on mobile, tablet, desktop, or multiple breakpoints.
- Capture only the facts needed for layout diagnosis: component positions, spacing rhythm, overflow behavior, clipped content, sticky overlaps, or blocked actions.

### 2. Classify the layout issue

Use `references/issue-checklist.md` to classify the problem before recommending fixes.

Typical classes:

- spacing rhythm
- alignment and centering
- overflow and wrapping
- responsive transformation failure
- sticky, modal, drawer, or overlay collision
- form field and validation layout instability
- data-heavy layout such as cards, tables, toolbars, or filters

### 3. Write a narrow remediation brief

- Keep the scope layout-only.
- Describe the problem in observable terms instead of aesthetic preference language.
- State the user impact directly, for example hidden CTA, clipped error message, broken scan path, or horizontal scroll.
- Recommend the smallest fix that resolves the issue without changing unrelated behavior.
- Include viewport-specific layout rules when the problem is responsive.

### 4. Add acceptance checks

- Make the acceptance checks browser-testable.
- Name at least one affected viewport and one stable verification scenario.
- Include content safety expectations for long text, helper text, error messages, tables, toolbars, or sticky actions when relevant.
- If the fix depends on implementation or browser validation, explicitly hand off to `uiux-design`.

## Output Contract

Always answer in Traditional Chinese and use the structure from `references/output-template.md`.

Required sections:

- `版面摘要`
- `主要問題`
- `修正 brief`
- `驗收檢查`
- `轉交建議`

Rules:

- Keep each issue concrete: surface, viewport, symptom, impact, and recommended fix.
- Do not prescribe exact CSS unless the user explicitly asks for implementation detail.
- Do not expand into copywriting, feature scope, or general usability unless that directly blocks the layout fix.
- Omit `轉交建議` only when no downstream implementation or verification handoff is needed.

## References

- `references/routing.md`: when to use this skill versus `gemini-cli` or `uiux-design`
- `references/issue-checklist.md`: layout issue categories and what to inspect for each one
- `references/output-template.md`: required report structure and acceptance-check writing pattern
