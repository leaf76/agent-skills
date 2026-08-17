# agent-skills

Shared [Agent Skills](https://docs.cursor.com) library for Cursor, Claude Code, Codex, and similar tools.

Each top-level directory is one skill (`SKILL.md` plus optional `scripts/`, `references/`, and templates).

## Install

```bash
git clone https://github.com/leaf76/agent-skills.git ~/.agents/skills
```

Point other clients at the same tree, or copy individual skill folders into:

- `~/.cursor/skills/<skill-name>/`
- `~/.claude/skills/<skill-name>/`
- `~/.codex/skills/<skill-name>/`
- a project-local `.cursor/skills/` directory

Do not commit `.env`, API keys, or `auth.json`.

## Original skills

Workflow and quality:

- `dev-workflow`, `fix-bug`, `fix-lint`, `write-tests`, `qa-tester`
- `review-changes`, `review-fix-ship`, `security-audit`, `optimize`
- `deep-init`, `plan-mode`, `refactor`, `explain`, `deploy`

Domain guardrails:

- `backend-api-auth-guardrails`
- `database-data-guardrails`
- `frontend-ui-guardrails`
- `infra-ops-mobile-guardrails`

UI / mobile / files:

- `frontend-mobile-uiux-designer`, `uiux-design`, `layout-review`
- `adb-android-app-ops`, `image-file-reader`, `multimodal-looker`
- `rust-programmer`, `firmware-feature-writer`

## Local-only skills

These are documented here but need software on the machine. Skip them if the tools are not installed.

| Skill | Needs |
|-------|--------|
| `hermes-chrome` | Hermes Chrome extension + local bridge |
| `computer-use` | `lazy-desktop-mcp` |
| `grok-x-search` | Grok CLI or `XAI_API_KEY` |
| `source-command-collab-start` | session-collab MCP |
| `gemini-cli` | local Gemini CLI |
| `chronicle` | Chronicle screen history |

## Third-party copies

Cloudflare and OpenAI/Codex skills are included for convenience. They are not original work. See [NOTICE](NOTICE) and any `LICENSE.txt` inside the skill folder.

`guizang-ppt-skill/` is not in git. Clone it from [op7418/guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) if you need it.

## Suggested routing

1. Planning: `plan-mode` → `deep-init` when bootstrapping `AGENTS.md`.
2. Non-trivial implementation: `dev-workflow` as the outer controller.
3. Bugs: `fix-bug` (keep `dev-workflow` around it when the change is large).
4. Web UI evidence: browser E2E / Chrome DevTools / Playwright. Use `computer-use` only for native desktop shells.
5. Native mobile UX specs: `frontend-mobile-uiux-designer`. Web UX review: `uiux-design` / `layout-review`.
6. Before commit or ship: `review-changes`, then `review-fix-ship` if you need the full release path.

## License

Original skills and docs: [MIT](LICENSE). Third-party skills: their upstream licenses ([NOTICE](NOTICE)).
