#!/usr/bin/env bash
# Headless Grok Build CLI helper for X/Twitter-oriented search.
# Uses existing grok login/OAuth session (or XAI_API_KEY fallback inside grok).
set -euo pipefail

GROK_BIN="${GROK_BIN:-$HOME/.grok/bin/grok}"
MAX_TURNS="${GROK_X_MAX_TURNS:-10}"
MODEL="${GROK_X_MODEL:-}"
HANDLES=""
FROM_DATE=""
TO_DATE=""
QUERY=""

usage() {
  cat <<'EOF'
Usage:
  grok-x-search.sh [options] <query...>

Options:
  --handles a,b,c   Prefer posts from these X handles (prompt-level filter)
  --from YYYY-MM-DD Time window start (prompt-level)
  --to YYYY-MM-DD   Time window end (prompt-level)
  --max-turns N     Agent turns (default 10)
  --model ID        Optional model override
  -h, --help        Show help

Env:
  GROK_BIN          Path to grok binary (default ~/.grok/bin/grok)
  GROK_X_MAX_TURNS  Default max turns
  GROK_X_MODEL      Default model
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --handles)
      HANDLES="${2:-}"; shift 2 ;;
    --from|--from-date)
      FROM_DATE="${2:-}"; shift 2 ;;
    --to|--to-date)
      TO_DATE="${2:-}"; shift 2 ;;
    --max-turns)
      MAX_TURNS="${2:-}"; shift 2 ;;
    --model)
      MODEL="${2:-}"; shift 2 ;;
    -h|--help)
      usage; exit 0 ;;
    --)
      shift; break ;;
    -*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2 ;;
    *)
      if [[ -n "$QUERY" ]]; then
        QUERY+=" $1"
      else
        QUERY="$1"
      fi
      shift ;;
  esac
done

if [[ $# -gt 0 ]]; then
  if [[ -n "$QUERY" ]]; then
    QUERY+=" $*"
  else
    QUERY="$*"
  fi
fi

if [[ -z "${QUERY// }" ]]; then
  echo "Error: query required" >&2
  usage >&2
  exit 2
fi

if [[ ! -x "$GROK_BIN" ]]; then
  if command -v grok >/dev/null 2>&1; then
    GROK_BIN="$(command -v grok)"
  else
    echo "Error: grok binary not found at $GROK_BIN" >&2
    echo "Install Grok Build CLI or set GROK_BIN." >&2
    exit 1
  fi
fi

TMP_DIR="${TMPDIR:-/tmp}"
PROMPT_FILE="$(mktemp "$TMP_DIR/grok-x-search.XXXXXX.md")"
cleanup() { rm -f "$PROMPT_FILE"; }
trap cleanup EXIT

{
  cat <<EOF
You are performing an X (Twitter) research task for another coding agent.

Task:
Search for recent, public X/Twitter posts and discussions relevant to the query.
Prefer primary sources on x.com (status URLs, handle profiles). Use web_search / web_fetch as needed.
Do not edit files. Do not run shell commands. Do not spawn subagents.

Query:
${QUERY}
EOF

  if [[ -n "$HANDLES" ]]; then
    echo
    echo "Prefer or focus on these handles (comma-separated): $HANDLES"
  fi
  if [[ -n "$FROM_DATE" || -n "$TO_DATE" ]]; then
    echo
    echo "Time window: from=${FROM_DATE:-any} to=${TO_DATE:-any}"
  fi

  cat <<'EOF'

Output format (Markdown):
## Summary
- 3-6 bullets of findings

## Sources
- Full https://x.com/... URLs (status links when possible)

## Limits
- Note freshness / indexing limits if results may be incomplete

Rules:
- Cite real URLs only. If none found, say so.
- Do not invent posts, metrics, or quotes.
- Keep the answer concise and factual.
EOF
} >"$PROMPT_FILE"

ARGS=(
  --prompt-file "$PROMPT_FILE"
  --always-approve
  --max-turns "$MAX_TURNS"
  --no-memory
  --no-plan
  --no-subagents
  --disallowed-tools "run_terminal_cmd,search_replace,write_file,edit_file,Agent"
  --output-format plain
)

if [[ -n "$MODEL" ]]; then
  ARGS+=(--model "$MODEL")
fi

echo "<!-- path: grok-cli bin=$GROK_BIN -->" >&2
"$GROK_BIN" "${ARGS[@]}"
