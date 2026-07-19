# lazy-desktop-mcp tool loop

Tools are MCP-namespaced (exact names may appear as `lazy-desktop__…` depending on host). Use the names below as logical tools.

## Always-available (no policy grant)

| Tool | Purpose |
|------|---------|
| `desktop.capabilities` | Backend support map |
| `desktop.permissions` | OS permission status |
| `desktop.runtime` | Policy paths, presence paths, effective policy |
| `session.open` | Open scoped session |
| `session.close` | Close session |

## Policy-gated (typical)

| Tool | Notes |
|------|-------|
| `app.list` / `app.launch` / `app.activate` / `app.quit` | App-level |
| `window.list` / `window.focus` / `window.move` / `window.resize` | Window-level |
| `observe.capture` | Screenshot artifact (primary display today) |
| `ocr.read` | Needs tesseract + capture permission |
| `vision.describe` / `vision.locate` | Only if local vision adapter configured |
| `input.click` | Coordinates or target_ref |
| `input.click_target` | OCR text or window-relative click |
| `input.type` | Types into focused surface |
| `input.hotkey` | Key combo array |

## Recommended call order

1. **`desktop.runtime`** — confirm `security_policy_path`, presence STOP/PAUSE paths, host alive.
2. **Precheck STOP/PAUSE files** — if `STOP` exists, stop and ask user to clear it. If `PAUSE` exists, tell user to Resume / remove PAUSE (session.open cannot self-clear a pre-existing PAUSE).
3. **`desktop.permissions`** — if Accessibility or Screen Recording missing, tell the user; stop control.
4. **`desktop.capabilities`** — skip unavailable classes instead of thrashing.
5. **`session.open`**
   - `capabilities`: only what you need (e.g. `window_focus`, `input_click`, `input_type`)
   - `allowed_apps` / `allowed_windows` / `allowed_screens`: smallest set
   - Prefer `allow_raw_input: false` unless coordinate clicks are required **and** policy already allows raw input
   - Optional `dry_run: true` to validate scope before real control
6. **Target**
   - `app.activate` when you need the app frontmost without exact window title
   - `window.focus` with `window_id`, `title`, `title_contains`, or `app`
7. **Observe**
   - `observe.capture` → note `artifact_id` / path
   - `ocr.read` when locating labels by text
8. **Act**
   - Prefer `input.click_target` with `text` or window-relative `relative`
   - Fall back to `input.click` + coordinates only when necessary
   - `input.type` / `input.hotkey` for keyboard
9. **Re-observe** after material actions
10. **`session.close`** — host auto-quits Presence when this was the last session (`LAZY_DESKTOP_AUTO_QUIT_PRESENCE_UI`, default on).
11. **`presence.ui.quit`** — always-available MCP tool; call after close (or when HUD stuck / auto-quit off). Prefer over shell `osascript`/`pkill`.
12. Optional: `desktop.runtime` to confirm `presence_ui_running: false`.

Optional hygiene: if a residual `PAUSE` was left only by this session and control is finished, you may remove the PAUSE file; never remove `STOP` without user intent.

## Errors to respect

| Signal | Action |
|--------|--------|
| Policy deny / capability not allowed | Do not widen policy yourself; ask user or shrink request |
| Runtime approval dialog | Wait for user Allow/Deny; retry once after Allow |
| `SESSION_STOPPED` | Halt; user must clear STOP file |
| `SESSION_PAUSED` | Wait or report timeout; do not bypass |
| Missing MCP tools | Fail soft; see `provider-wiring.md` |

## Session hygiene

- One logical task → one session when possible
- Do not leave sessions open across unrelated work
- **Always quit Presence UI when finished** (test smoke, real control, or aborted mid-flow after you started control)
- Report if overlay policy grew (new approved targets)
