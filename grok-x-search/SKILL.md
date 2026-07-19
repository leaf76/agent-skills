---
name: grok-x-search
description: Use local Grok Build CLI (headless) or xAI Responses API x_search to fetch live X/Twitter posts, threads, handle timelines, and social sentiment. Use when the user asks about X/Twitter, @handles, recent posts, viral threads, or Grok X search; prefer this over Brave for X-native questions.
---

# Grok X Search

## Overview

Fetch **live X (Twitter)** context for the current agent session using:

1. **Primary — Grok Build CLI** (`~/.grok/bin/grok`) headless mode with `web_search` (works with your existing `grok login` / OAuth session).
2. **Optional — True X Search** via xAI Responses API `x_search` when `XAI_API_KEY` is set (server-side X index; better citations and handle filters).

Treat results as **time-sensitive social evidence**, not ground truth. Cite URLs. Do not invent posts.

## When to Use

- User asks what people are saying on X about a topic, product, model, or company.
- Need recent posts from `@handle` or a short list of handles.
- Need thread / viral post summary with source links.
- User explicitly asks to use Grok CLI or Grok X search.

Do **not** use for:

- Library API docs (use Context7).
- General web research unrelated to X (use Brave).
- Private DMs, paywalled, or non-public content.

## Prerequisites

| Path | Requirement |
|------|-------------|
| Grok CLI | `~/.grok/bin/grok` on PATH or absolute path; `grok login` already done (or `XAI_API_KEY`) |
| True `x_search` | `export XAI_API_KEY=...` from https://console.x.ai |

Check CLI:

```bash
command -v grok || test -x "$HOME/.grok/bin/grok"
```

## Safety Rules

- Never put secrets, tokens, cookies, or private keys in the search query or saved prompt files.
- Prefer public handles and public topics only.
- Cap agent turns (`--max-turns`); do not allow file writes or shell when only searching.
- Label uncertainty: web-indexed X posts may lag the live timeline.
- Do not claim "official X API firehose" when using Grok CLI `web_search` path.

## Quick Start (Grok CLI)

Use the wrapper (recommended):

```bash
"$HOME/.agents/skills/grok-x-search/scripts/grok-x-search.sh" "What is @xai posting about this week?"
```

With handle filter (prompt-level; CLI path):

```bash
"$HOME/.agents/skills/grok-x-search/scripts/grok-x-search.sh" \
  --handles xai,elonmusk \
  "Summarize the latest public posts and themes"
```

Manual equivalent:

```bash
GROK_BIN="${GROK_BIN:-$HOME/.grok/bin/grok}"
"$GROK_BIN" -p "Search X/Twitter (prefer x.com sources). Query: <QUERY>. Return: bullets with post theme, approximate date, and status URLs. No file edits." \
  --always-approve \
  --max-turns 10 \
  --no-memory \
  --no-plan \
  --no-subagents \
  --disallowed-tools "run_terminal_cmd,search_replace,write_file,edit_file,Agent" \
  --output-format plain
```

## True X Search (xAI API, optional)

When `XAI_API_KEY` is set:

```bash
"$HOME/.agents/skills/grok-x-search/scripts/xai-x-search.py" "What are people saying about OpenCode on X?"
"$HOME/.agents/skills/grok-x-search/scripts/xai-x-search.py" --handles elonmusk,xai "Latest product announcements"
"$HOME/.agents/skills/grok-x-search/scripts/xai-x-search.py" --from-date 2026-07-01 --to-date 2026-07-15 "Grok 4.5 reactions"
```

This calls `POST https://api.x.ai/v1/responses` with `tools: [{ "type": "x_search", ... }]`.

## Workflow for the Agent

### 1. Pick path

| Situation | Path |
|-----------|------|
| Default / user has Grok login only | `grok-x-search.sh` (Grok CLI) |
| Need handle allow/exclude + date range + stronger X grounding | `xai-x-search.py` if `XAI_API_KEY` present |
| No Grok CLI and no API key | Tell user to `grok login` or set `XAI_API_KEY`; do not fake results |

### 2. Run search

- Write a focused query (topic + time window + language).
- Prefer the wrapper scripts over ad-hoc prompts.
- Timeout: allow up to 3 minutes for CLI path.

### 3. Present results

Always return:

1. Short answer (繁體中文 unless user asks otherwise)
2. Bullet findings with **source URLs** (`https://x.com/...`)
3. Path used: `grok-cli` vs `xai-x_search`
4. Limits / freshness caveats

### 4. Do not

- Edit repo files as part of a search.
- Chain into unrelated coding work unless the user asked.
- Dump full raw JSON to the user unless they want debug output.

## Output Template

```markdown
## X 搜尋結果
- **路徑**: grok-cli | xai-x_search
- **查詢**: ...

### 重點
- ...
- ...

### 來源
- https://x.com/...
```

## Verification

- At least one `x.com` / `twitter.com` URL when claims are specific.
- If no posts found, say so; do not invent.
- If CLI fails with auth, instruct: `grok login` or set `XAI_API_KEY`.

## Common Mistakes

- Using Brave only for X questions when this skill is available.
- Letting Grok CLI edit files during a pure search (`--disallowed-tools` required).
- Confusing Grok **model** inside OpenCode with Grok **CLI tools** (OpenCode model ≠ automatic X access).
- Expecting private or deleted posts.
