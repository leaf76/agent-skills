---
name: frontend-ui-guardrails
description: Use when frontend, UI, browser automation, live UI, screenshot, snapshot, responsive layout, accessibility, modal, form, navigation, or user-facing state work is in scope.
---

# Frontend UI Guardrails

This is a domain-specific expansion of the project's `AGENTS.md` (or equivalent agent rules). It may add frontend and UI requirements, but it must never weaken `AGENTS.md`, `SECURITY`, secrets handling, production safety, or destructive-command restrictions.

## Core Rules

- Preserve existing UI/UX behavior, accessibility, design system, copy, and interaction patterns unless the task explicitly requires a change.
- Do not expose technical details in user-facing messages.
- Do not hardcode secrets, auth headers, environment-specific values, or profile-specific browser config.
- Prefer project-level `agent-browser.json` or `AGENT_BROWSER_*` environment variables when such config is already part of the project.

## Evidence Priority

- **Web / browser UI:** prefer Hermes Chrome (real cookies/SSO), then browser-e2e / agent-browser / Playwright headless / Chrome DevTools — **not** computer-use and **not** browser-use by default.
- **browser-use:** only for external black-box sites (or explicit user request). Avoid full-auto for OTP, payments, production config, trading.
- **Native desktop shell only** (Tauri / PyQt / Electron frame, tray, OS dialogs, file pickers) or explicit user request → `computer-use` skill (`lazy-desktop-mcp`). Announce before control; honor Presence STOP/PAUSE; do not use CU as a daily-Chrome driver.
- **Screenshot-only** (no click/type) → `screenshot` skill.
- Escalate to deeper DOM/console/network/performance tooling (Chrome DevTools) when more evidence is needed.
- Add a `Playwright` smoke flow only when a reproducible interaction or responsive regression check adds real value.
- Do not steal keyboard/mouse focus while the user works (`osascript` activate, headed Playwright, hijacking the active tab).

## Layout And Interaction Checks

- When a task includes screen evidence or responsive risk, check layout, spacing, alignment, centering, overflow, wrapping, clipping, safe-area, CTA visibility, and overlay obstruction.
- Verify mobile and desktop primary breakpoints; include tablet when the component or flow can reasonably break there.
- Check text alignment, long text, dynamic content, localized strings, sticky/fixed/modal/overlay surfaces, corner controls, forms, keyboard navigation, focus order, and focus visibility.
- Cover loading, empty, error, disabled, and success states when they exist.
- For layout review output, clearly separate evidence from static screenshots and evidence that still requires browser validation.

## Common Mistakes

- Do not treat a desktop screenshot as proof that mobile works.
- Do not change modal state logic, validation, routing, or copy while fixing a layout issue unless the task requires it.
- Do not call a UI change done without browser or screenshot evidence when observable behavior was affected.
