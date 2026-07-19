#!/usr/bin/env python3
"""True X search via xAI Responses API (tools: x_search). Requires XAI_API_KEY."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.x.ai/v1/responses"
DEFAULT_MODEL = os.environ.get("GROK_X_API_MODEL", "grok-4.5")


def build_tool(
    handles: list[str] | None,
    excluded: list[str] | None,
    from_date: str | None,
    to_date: str | None,
    images: bool,
    videos: bool,
) -> dict:
    tool: dict = {"type": "x_search"}
    if handles:
        tool["allowed_x_handles"] = handles
    if excluded:
        tool["excluded_x_handles"] = excluded
    if from_date:
        tool["from_date"] = from_date
    if to_date:
        tool["to_date"] = to_date
    if images:
        tool["enable_image_understanding"] = True
    if videos:
        tool["enable_video_understanding"] = True
    return tool


def extract_text(payload: dict) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    chunks: list[str] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") in {"message", "output_message"}:
            for part in item.get("content") or []:
                if not isinstance(part, dict):
                    continue
                text = part.get("text") or part.get("output_text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
        elif item.get("type") == "text" and isinstance(item.get("text"), str):
            chunks.append(item["text"].strip())
    if chunks:
        return "\n".join(chunks)

    # Fallback: pretty JSON for debugging
    return json.dumps(payload, ensure_ascii=False, indent=2)[:8000]


def extract_citations(payload: dict) -> list[str]:
    cites: list[str] = []
    raw = payload.get("citations") or payload.get("sources") or []
    if isinstance(raw, list):
        for c in raw:
            if isinstance(c, str):
                cites.append(c)
            elif isinstance(c, dict):
                url = c.get("url") or c.get("uri") or c.get("id")
                if url:
                    cites.append(str(url))
    return cites


def main() -> int:
    parser = argparse.ArgumentParser(description="xAI x_search via Responses API")
    parser.add_argument("query", nargs="+", help="Search question")
    parser.add_argument("--handles", default="", help="Comma-separated allowed handles (max 20)")
    parser.add_argument("--exclude", default="", help="Comma-separated excluded handles (max 20)")
    parser.add_argument("--from-date", default="", help="YYYY-MM-DD")
    parser.add_argument("--to-date", default="", help="YYYY-MM-DD")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--images", action="store_true")
    parser.add_argument("--videos", action="store_true")
    parser.add_argument("--raw", action="store_true", help="Print full JSON response")
    args = parser.parse_args()

    api_key = os.environ.get("XAI_API_KEY", "").strip()
    if not api_key:
        print(
            "Error: XAI_API_KEY is not set.\n"
            "Get a key at https://console.x.ai and export XAI_API_KEY=...\n"
            "Or use grok-x-search.sh (Grok CLI OAuth path) instead.",
            file=sys.stderr,
        )
        return 1

    handles = [h.strip().lstrip("@") for h in args.handles.split(",") if h.strip()]
    excluded = [h.strip().lstrip("@") for h in args.exclude.split(",") if h.strip()]
    if handles and excluded:
        print("Error: --handles and --exclude cannot be used together", file=sys.stderr)
        return 2

    query = " ".join(args.query).strip()
    body = {
        "model": args.model,
        "input": [{"role": "user", "content": query}],
        "tools": [
            build_tool(
                handles or None,
                excluded or None,
                args.from_date or None,
                args.to_date or None,
                args.images,
                args.videos,
            )
        ],
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {err_body[:2000]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1

    if args.raw:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("## X 搜尋結果")
    print("- **路徑**: xai-x_search")
    print(f"- **模型**: {args.model}")
    print(f"- **查詢**: {query}")
    print()
    print(extract_text(payload))
    cites = extract_citations(payload)
    if cites:
        print()
        print("### Citations")
        for url in cites:
            print(f"- {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
