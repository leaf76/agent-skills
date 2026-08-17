---
name: hermes-chrome
description: Drive the user's daily Chrome via Hermes Chrome (extension + local bridge :19876 + CLI). Use for real cookies/SSO, workspace tabs, capture, cookie-aware download, local URL/file safety checks, light DOM ops without hijacking the active tab. Prefer over headless when live daily Chrome is required.
---

# Hermes Chrome (Grok skill)

## When to use

- Need **user's real Chrome** cookies / SSO / already-open tabs
- Logged-in capture, SSO smoke, already-open workspace tabs
- Download with cookie jar, local URL/file safety checks
- User says hermes-chrome / daily Chrome / bridge 19876

## When NOT to use

- Public pages with no login → Hermes headless `browser_*` / Playwright headless
- Own-app E2E / layout → Chrome DevTools MCP / Playwright / browser-e2e
- Isolated headed browser without daily cookies → Agent Chrome `:9333`

## Hard rules

- Do **not** `osascript` / `tell Google Chrome to activate`
- Do **not** rewrite the user's **active** tab
- Fail-fast: if `ping` times out once, stop the chain; ask user to Reload + click icon
- Gate with health: prefer `extension_connected: true` on `/v1/health`
- Prefer `check-url` before download; do not `--force` block findings without user ask
- No cloud threat APIs by default

## Paths

| Piece | Path |
|-------|------|
| CLI | `~/.hermes/scripts/hermes-chrome.sh` or repo `scripts/hermes-chrome.sh` |
| Repo | local Hermes Chrome checkout (CLI usually under `~/.hermes/scripts/`) |
| Bridge | `http://127.0.0.1:19876` |
| Runtime | `~/.hermes/run/hermes-chrome/` |
| Downloads | `~/.hermes/run/hermes-chrome/downloads/` |

## Ops loop

```bash
CLI=~/.hermes/scripts/hermes-chrome.sh

# 1) Bridge
$CLI bridge-status
# extension_connected should be true; if bridge down: $CLI install-launchd  or bridge-start

# 2) Extension gate (fail-fast)
$CLI ping
# expect: "extension":"hermes-chrome","version":"1.4.1"+ 

# 3) Work
$CLI start 'https://example.com/'
$CLI list-tabs --group
$CLI navigate 'https://example.org/' --tab-id <id>
$CLI capture --prefer active --out /tmp/page.png
$CLI eval --tab-id <id> --expr 'document.title'
$CLI page-assets --tab-id <id>
$CLI check-tab-links --tab-id <id>
$CLI --json ping
$CLI check-url 'https://example.com/report.pdf'
$CLI download 'https://example.com/report.pdf'            # direct
$CLI download 'https://app.example/private' --cookies     # cookie jar
$CLI analyze ~/.hermes/run/hermes-chrome/downloads/report.pdf
$CLI status
$CLI stop   # closes Hermes workspace tabs
```

## Capture / download notes

- `captureVisibleTab` may briefly activate the target tab; put capture targets in a **separate window** when possible
- Optional title filters can target known window titles; do not hardcode product-specific symbols
- `download` runs check → save → analyze unless `--no-check` / `--no-analyze` / `--force`
- `analyze` is local heuristics (not antivirus)

## Version gate

| Version | Capability |
|---------|------------|
| 1.2.0+ | capture, list-tv |
| 1.3.0+ | list-tabs, navigate, eval, click, type, health extension_last_seen |
| 1.4.1+ | fetch_url (cookies download), page-assets, CLI check-url/download/analyze |

If `ping` version lags repo, tell user: Reload unpacked/CWS + click icon.

## Install / recovery

```bash
$CLI install-help
$CLI install-launchd    # macOS login + KeepAlive
# chrome://extensions → Load unpacked → <repo>/extension → click icon
```
