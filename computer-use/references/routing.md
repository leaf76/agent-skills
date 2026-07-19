# Computer Use routing

## Decision tree

```text
Is the surface a normal web page / web app?
  YES → hermes-chrome (real cookies/SSO) OR Playwright headless / browser-e2e / DevTools
  NO  → continue

Is it Android?
  YES → adb-android-app-ops
  NO  → continue

Only need a still image of the screen/app (no click/type)?
  YES → screenshot skill (or observe.capture if MCP already up for other work)
  NO  → continue

Native desktop shell, OS dialog, tray, file picker, or user asked for computer use?
  YES → computer-use (this skill)
  NO  → prefer browser stack; do not open CU “just in case”
```

## Escalation from web tools

Escalate **to** computer-use only when:

- WebView/browser tools cannot reach the control (native chrome, OS sheet, tray)
- Task is explicitly desktop app QA
- User names computer use / lazy-desktop

Do **not** escalate because a web selector is hard — fix selectors, use CDP/eval, or ask.

## De-escalation from CU

If you discover the app is mostly web content inside a browser window:

1. Prefer Hermes / Playwright for the web part
2. Keep CU only for the native frame pieces that still require it
3. Prefer two short sessions over one long raw-input session

## Related skills

| Skill | Role |
|-------|------|
| `hermes-chrome` | Daily Chrome cookies/SSO without CU |
| `browser-e2e` | Own-app browser E2E / layout |
| `browser-use` | External black-box sites only |
| `screenshot` | OS-level capture without control |
| `uiux-design` | UX review; web evidence via browser tools first |
| `adb-android-app-ops` | Android device UI |
