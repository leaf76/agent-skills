---
name: computer-use
description: >
  Drive native desktop apps via lazy-desktop-mcp (screenshot, click, type, hotkey,
  window control, policy-bound sessions, Presence STOP/PAUSE). Use when the user
  asks for computer use / desktop control / lazy-desktop, or when verifying a
  native desktop shell (Tauri, PyQt, Electron frame, tray, file picker, OS
  permission dialogs) that cannot be done via DOM/CDP. Not the default for web
  pages, product UI debug, or SSO — prefer hermes-chrome, browser-e2e, DevTools,
  or Playwright. Do not steal keyboard/mouse focus while the user works unless
  the task is explicitly desktop control. Use when the user runs /computer-use.
---

# Computer Use (lazy-desktop-mcp)

Local-first desktop automation through **lazy-desktop-mcp** MCP tools.  
Implementer: repo `~/WorkSpace/sideProject/mcp_projects/lazy_desktop_mcp` (npm `lazy-desktop-mcp`).

Load references only as needed:

| File | When |
|------|------|
| `references/routing.md` | Choosing among browser / screenshot / CU |
| `references/tool-loop.md` | MCP tool order and parameters |
| `references/safety.md` | Policy, STOP/PAUSE, forbidden actions |
| `references/provider-wiring.md` | MCP missing / client setup |

## When to use

- User explicitly asks for computer use, desktop control, lazy-desktop, or Presence HUD
- Native desktop app verification: Tauri / PyQt / Electron **shell**, tray, dock, first-run, update dialogs, file pickers, OS permission prompts
- Interaction that crosses WebView boundary and cannot be completed with CDP/DOM tools

## When NOT to use (route away)

| Need | Prefer |
|------|--------|
| Web / local preview / SSO / tabs | `hermes-chrome` → browser-e2e / DevTools / Playwright headless |
| System screenshot only (no click/type) | `screenshot` |
| External black-box website crawl | `browser-use` (only if user asks or no better path) |
| Android UI | `adb-android-app-ops` |

**Not default** for product web debug or CI. Do not use CU as a generic browser driver.

## Hard rules

1. **Announce before control.** If you escalate to CU for a native shell (without the user naming CU), say one short line first: which app, why CU, that Presence STOP can halt you.
2. **Do not steal focus by default.** Forbidden as a web workaround: `osascript` / `tell application "Google Chrome" to activate`, hijacking the user's active tab, headed Playwright, or CU-driving daily Chrome when Hermes/CDP suffices.
3. **Minimal session scope.** Open the smallest capability set and app/window/screen allowlists that fit the task.
4. **Prefer semantic targets over raw pixels.** Order: `app.activate` / `window.focus` → `input.click_target` (OCR text or window-relative) → raw `input.click` coordinates only if policy allows and higher-level targeting fails.
5. **Honor operator STOP / PAUSE.** On `SESSION_STOPPED` or `SESSION_PAUSED`, stop and report; do not retry past STOP. Operator must clear STOP intentionally.
6. **No full-auto on high-risk flows.** OTP, payments, production config, trading/orders → human-in-the-loop; stop and ask.
7. **Destructive actions need explicit approval.** Delete, submit irreversible forms, install/uninstall, power, mass paste secrets — confirm first.
8. **Always close the session** with `session.close` when done (or report why you could not).
9. **Presence teardown is host-owned by default.** After the last `session.close`, `lazy-desktop-host` auto-quits Presence UI (`LAZY_DESKTOP_AUTO_QUIT_PRESENCE_UI`, default on). Still call `session.close` so that path runs. If Presence is still running after close (older host, auto-quit off, or crash), quit it with the commands below. Do not rely on the app’s ~180s idle auto-quit alone. (Exception: user asks to keep Presence open.)
10. **Fail soft if MCP is missing.** Explain missing server / policy / OS permissions; do not invent shell mouse automation as a silent fallback.

## Standard loop

```text
1. Preflight
   desktop.runtime  → policy paths, presence paths, host alive
   if STOP or PAUSE file exists → stop and ask user (PAUSE blocks session.open until cleared)
   desktop.permissions → Accessibility / Screen Recording
   desktop.capabilities → what this backend actually supports
2. Scope
   session.open with minimal capabilities + allowed_apps/windows/screens
   (dry_run=true first if unsure about policy)
3. Observe → Act → Observe
   observe.capture (before/after)
   optional ocr.read / vision.* when configured
   app.activate / window.focus / input.* as needed
4. Teardown (required)
   session.close  → host auto-quit Presence (default)
   presence.ui.quit → always available force-quit if still running / auto-quit off
   report artifacts, STOP/PAUSE, and Presence quit status
```

Detail: `references/tool-loop.md`.

## Presence UI

Host auto-launches **ComputerUsePresence** on session open / gated control (not idle MCP start), and **auto-quits** after the last `session.close` or host exit (default).

- Closing the HUD alone does **not** stop the agent (default).
- **Stop** writes STOP → host denies gated actions.
- **Pause** waits until cleared or STOP.
- Paths under `~/Library/Application Support/dev.lazy.desktop-mcp/artifacts/presence/` (see `desktop.runtime`).
- Runtime flags: `presence_ui_auto_launch`, `presence_ui_auto_quit`, `presence_ui_running`.
- **MCP tool `presence.ui.quit`** — always available; use after `session.close` or when HUD is stuck. Prefer this over shell `osascript`/`pkill`.

Do not try to click the Presence STOP control via the same synthetic input path to “self-approve” continued control.

## Evidence reporting

When CU was used, the final answer should include:

- Target app / window and why CU (not browser)
- Session capabilities used (high level)
- Capture/OCR outcomes that support pass/fail
- Any policy deny, runtime approval, STOP/PAUSE, or permission gap
- Whether **Presence UI was quit** after teardown (or why it was left running)
- Residual risk (e.g. primary display only; no multi-monitor)

## Codex bundled CUA

If OpenAI/Codex bundled `computer-use` plugin is also available: **prefer lazy-desktop-mcp** for local policy, audit, and Presence. Use bundled CUA only when lazy-desktop tools are unavailable and the user accepts that path.
