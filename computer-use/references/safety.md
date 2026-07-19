# Computer Use safety

## Trust model

- **Host policy file** is the server-owned boundary. Session requests may only **narrow** what the host policy allows.
- Package default is **deny-by-default** for control capabilities until the operator configures policy.
- Runtime approval (macOS) may add app/window/screen **targets** to a local overlay — it must **not** enable new capability classes or raw input by itself.
- Audit: sensitive fields hashed; screenshots stay local under host app data.

## Operator controls

| Control | Effect |
|---------|--------|
| Presence **Stop** / `STOP` file | Deny gated actions; close live sessions |
| Presence **Pause** / `PAUSE` file | Host waits (poll, up to ~300s) until cleared or STOP |
| Closing Presence HUD | Does **not** stop agent by default |

**Important:** `session.open` is **gated by PAUSE** — the host waits for PAUSE to clear *before* opening. PAUSE is only cleared *after* a successful `SessionOpened`. A stale PAUSE therefore deadlocks control until the operator deletes the file or uses Presence Resume. Always precheck `presence_pause_path` / `presence_stop_path` via `desktop.runtime` (or filesystem) before gated tools.

`session.open` does **not** clear STOP.

Paths (confirm via `desktop.runtime`):

```text
~/Library/Application Support/dev.lazy.desktop-mcp/artifacts/presence/
  current.json
  events.jsonl
  STOP
  PAUSE
```

## Forbidden by default (agent behavior)

- Using CU to drive the user's **daily Chrome** when Hermes Chrome / CDP / Playwright can do the job
- `osascript` activate / force-front daily apps as a CU substitute
- Full-auto OTP, payment, production config changes, trading/order entry
- Expanding host policy or setting `allow_raw_input: true` without user intent
- Ignoring STOP/PAUSE or click-looping to defeat the Presence HUD
- Pasting secrets into audit-visible fields unnecessarily; never store secrets in vault or skill logs

## Require explicit user approval

- Destructive file or system actions
- Installers, privilege prompts, security settings
- Actions that send messages, money, or orders
- Broad allowlists (“all apps”) or permanent policy looseness

## Least privilege checklist

- [ ] Smallest capability list on `session.open`
- [ ] Named app(s) only when possible
- [ ] Prefer click_target / window-relative over raw screen coordinates
- [ ] Capture only what you need for evidence
- [ ] Close session when done
- [ ] **`session.close` then `presence.ui.quit`** so HUD/glow does not look like AI is still active
- [ ] Mention residual risk (primary display only; vision optional)

## Incident / stuck

1. Stop further input tools
2. Report last successful observe + error code
3. Suggest: clear STOP, grant OS permissions, review policy path, or finish manually
4. Do not invent alternative HID injection paths
