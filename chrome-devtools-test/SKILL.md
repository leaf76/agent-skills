---
name: chrome-devtools-test
description: Use the Chrome DevTools MCP tools to do lightweight E2E checks, capture console/network issues, and gather performance traces. Use when asked to “test in browser”, “verify UI”, or “debug in DevTools”.
---

# Chrome DevTools MCP Testing

Goal: quickly verify user flows and collect actionable evidence (console, network, screenshots, traces).

## Prerequisites (no hardcoded secrets)
- Read test env config from environment variables when available:
  - `TEST_BASE_URL`
  - `TEST_EMAIL`
  - `TEST_PASSWORD`
- If any are missing, ask the user (do not invent credentials and do not write them into files).

## Workflow

### 1) Navigate
- Open a page with `mcp__chrome-devtools__new_page` (or `...__navigate_page` for an existing page).
- Prefer going to the login page directly if auth is required.

### 2) Login (if needed)
- Use `mcp__chrome-devtools__take_snapshot` to locate form inputs and buttons.
- Use `mcp__chrome-devtools__fill` / `...__fill_form` and `mcp__chrome-devtools__click`.
- Use `mcp__chrome-devtools__wait_for` for a post-login indicator (URL change, dashboard text, etc.).

### 3) Execute the test scenario
- Interact with the UI via `...__click`, `...__fill`, `...__press_key`.
- If visual verification helps, use `mcp__chrome-devtools__take_screenshot`.
- To check errors, use `mcp__chrome-devtools__list_console_messages`.
- To inspect API calls, use `mcp__chrome-devtools__list_network_requests` + `...__get_network_request`.

### 4) Performance (optional)
- Record a trace with `mcp__chrome-devtools__performance_start_trace` and `...__performance_stop_trace`.
- Summarize CWV/insights relevant to the scenario.

## Safety / Reporting
- Never log or store passwords/tokens in plaintext.
- If a CAPTCHA/Turnstile appears, prompt the user to intervene manually.
- Report: steps executed, pass/fail, console errors, failing network requests, and attached screenshots/traces.

