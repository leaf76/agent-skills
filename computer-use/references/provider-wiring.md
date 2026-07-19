# Provider wiring (lazy-desktop-mcp)

Agent-layer skill only. Wiring is optional per client; if tools are absent, fail soft.

## Product paths

| Piece | Location |
|-------|----------|
| Source repo | `~/WorkSpace/sideProject/mcp_projects/lazy_desktop_mcp` |
| npm package | `lazy-desktop-mcp` |
| Dev policy template | `config/policy.dev.json` (from `client-config.json`) |
| Sync clients | `npm run sync:clients` in the repo (Codex + OpenCode by default) |
| Env policy | `LAZY_DESKTOP_POLICY_PATH` |
| Presence install | `npm run install:presence-ui` |

## Codex

1. Build/install: `npm install -g lazy-desktop-mcp` or use repo `npx` / cache under `~/.codex/mcp-cache/lazy-desktop-mcp`.
2. From the product repo: `npm run sync:clients` (or `LAZY_DESKTOP_CLIENTS=codex npm run sync:clients`).
3. Confirm `~/.codex/config.toml` has an MCP server entry for lazy-desktop and policy path points at intended JSON.
4. Restart Codex after config changes.
5. Smoke: call `desktop.runtime` then `desktop.permissions`.

Codex may also ship bundled `computer-use@openai-bundled`. Prefer **lazy-desktop-mcp** for policy + Presence when both exist.

## Grok / Claude

If the client supports MCP stdio servers, register roughly:

```json
{
  "command": "npx",
  "args": ["-y", "lazy-desktop-mcp"],
  "env": {
    "LAZY_DESKTOP_POLICY_PATH": "/absolute/path/to/policy.json"
  }
}
```

- Node 20+ and Rust toolchain required for native host build on install.
- Set a **tight** personal policy; do not point production agents at wide-open `allow_raw_input` without intent.
- After register: restart the agent app/CLI and verify tools appear.

## OpenCode

`npm run sync:clients` upserts OpenCode config when `LAZY_DESKTOP_CLIENTS` includes `opencode`.

## Preflight when tools missing

Tell the user clearly:

1. MCP server not registered or not started
2. `desktop-host` binary missing (package fail-closed)
3. Policy denies the capability
4. OS permissions not granted

Do not fall back to unscoped shell mouse/keyboard automation.
