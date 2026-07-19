#!/usr/bin/env python3
"""Run Gemini CLI with a stable prompt contract for UI implementation work."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_CONTEXT_FILE_BYTES = 200_000
MAX_TOTAL_CONTEXT_BYTES = 500_000


@dataclass(frozen=True)
class ContextBlock:
    path: Path
    text: str


def unique_preserve_order(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Use Gemini CLI to implement approved UI/UX changes in the current workspace."
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--brief", help="Inline implementation brief text.")
    input_group.add_argument("--brief-file", help="Path to a UTF-8 text file with the implementation brief.")
    parser.add_argument(
        "--context-file",
        action="append",
        default=[],
        help="Additional UTF-8 text file to embed as context. Repeatable.",
    )
    parser.add_argument(
        "--must-preserve",
        action="append",
        default=[],
        help="Non-negotiable item to preserve exactly, such as copy, routes, or component names. Repeatable.",
    )
    parser.add_argument(
        "--include-directory",
        action="append",
        default=[],
        help="Workspace directory to include for Gemini CLI. Repeatable.",
    )
    parser.add_argument("--model", help="Gemini model name. Leave empty to use the local CLI default.")
    parser.add_argument(
        "--approval-mode",
        default="auto_edit",
        choices=["default", "auto_edit", "plan"],
        help="Gemini CLI approval mode. Defaults to auto_edit for scoped repo edits.",
    )
    parser.add_argument(
        "--extensions",
        default="",
        help="Gemini CLI extensions list. Empty string disables extensions.",
    )
    parser.add_argument(
        "--save-prompt-file",
        help="Optional file to store the generated prompt contract.",
    )
    parser.add_argument(
        "--show-command",
        action="store_true",
        help="Print planned command metadata and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated prompt and exit without invoking Gemini.",
    )
    return parser


def read_text_input(inline_text: str | None, file_path: str | None) -> str:
    if inline_text is not None:
        text = inline_text.strip()
        if not text:
            raise ValueError("--brief cannot be empty.")
        return text

    assert file_path is not None
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Brief file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Brief path is not a file: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Brief file is empty: {path}")
    return text


def read_context_files(raw_paths: list[str]) -> list[ContextBlock]:
    blocks: list[ContextBlock] = []
    total_bytes = 0

    for raw_path in raw_paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {path}")
        if not path.is_file():
            raise ValueError(f"Context path is not a file: {path}")

        file_size = path.stat().st_size
        if file_size <= 0:
            raise ValueError(f"Context file is empty: {path}")
        if file_size > MAX_CONTEXT_FILE_BYTES:
            raise ValueError(
                f"Context file is too large ({file_size} bytes): {path}. "
                f"Keep each file under {MAX_CONTEXT_FILE_BYTES} bytes."
            )

        total_bytes += file_size
        if total_bytes > MAX_TOTAL_CONTEXT_BYTES:
            raise ValueError(
                "Combined context files are too large. "
                f"Keep total size under {MAX_TOTAL_CONTEXT_BYTES} bytes."
            )

        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Context file contains no useful text: {path}")

        blocks.append(ContextBlock(path=path.resolve(), text=text))

    return blocks


def resolve_include_directories(raw_paths: list[str]) -> list[Path]:
    directories: list[Path] = []
    seen: set[Path] = set()

    for raw_path in raw_paths:
        path = Path(raw_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Include directory not found: {path}")
        if not path.is_dir():
            raise ValueError(f"Include path is not a directory: {path}")
        if path in seen:
            continue
        seen.add(path)
        directories.append(path)

    return directories


def build_prompt(
    *,
    brief: str,
    must_preserve: list[str],
    context_blocks: list[ContextBlock],
) -> str:
    must_preserve_lines = "\n".join(f"- {item}" for item in must_preserve)
    parts = [
        "You are a senior UI engineer and design implementation partner.",
        "Task: implement the approved UI/UX changes in the current workspace.",
        "",
        "Execution contract:",
        "- Read the existing code before editing any files.",
        "- Limit edits to task-relevant files only.",
        "- Preserve existing UI behavior, routes, callbacks, and design-system usage unless the brief explicitly changes them.",
        "- Do not perform unrelated refactors, renames, cleanup, or architecture changes.",
        "- Keep the implementation scoped to web page or component work unless the brief explicitly says otherwise.",
        "- If the brief is too ambiguous for a safe edit, stop and explain what is missing instead of guessing.",
        "- After editing, report the files you changed and suggest follow-up browser verification steps.",
        "- Recommend Chrome DevTools checks first, and recommend a Playwright smoke flow only when the change touches a main user flow or responsive interaction.",
        "- Return plain text only. Do not wrap the response in code fences.",
        "",
        "Implementation brief:",
        brief,
    ]

    if must_preserve_lines:
        parts.extend(
            [
                "",
                "Non-negotiable items to preserve:",
                must_preserve_lines,
                "- If these items conflict with general UI best practices, preserve them and call out the tension instead of rewriting them.",
            ]
        )

    for block in context_blocks:
        parts.extend(
            [
                "",
                f"Additional context from {block.path.name}:",
                block.text,
            ]
        )

    return "\n".join(parts).strip() + "\n"


def build_command(
    prompt: str,
    *,
    model: str | None,
    approval_mode: str,
    extensions: str,
    include_directories: list[Path],
) -> list[str]:
    command = [
        "gemini",
        "--prompt",
        prompt,
        "--output-format",
        "text",
        "--approval-mode",
        approval_mode,
        "--extensions",
        extensions,
    ]
    if model:
        command.extend(["--model", model])
    for directory in include_directories:
        command.extend(["--include-directories", str(directory)])
    return command


def write_text(path_str: str, content: str) -> Path:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path.resolve()


def format_command_preview(command: list[str], include_directories: list[Path]) -> str:
    lines = [
        "mode: Gemini CLI UI implementation",
        f"command: {' '.join(command[:9])} ...",
        "include_directories:",
    ]
    if include_directories:
        lines.extend(f"- {directory}" for directory in include_directories)
    else:
        lines.append("- (none)")
    return "\n".join(lines) + "\n"


def normalize_output(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        raise RuntimeError("Gemini CLI returned an empty response.")
    return stripped + "\n"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    brief = read_text_input(args.brief, args.brief_file)
    must_preserve = unique_preserve_order(args.must_preserve)
    context_blocks = read_context_files(args.context_file)
    include_directories = resolve_include_directories(args.include_directory)
    prompt = build_prompt(
        brief=brief,
        must_preserve=must_preserve,
        context_blocks=context_blocks,
    )

    if args.save_prompt_file:
        write_text(args.save_prompt_file, prompt)

    command = build_command(
        prompt,
        model=args.model,
        approval_mode=args.approval_mode,
        extensions=args.extensions,
        include_directories=include_directories,
    )

    if args.show_command:
        sys.stdout.write(format_command_preview(command, include_directories))
        return 0

    if args.dry_run:
        sys.stdout.write(prompt)
        return 0

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or "(no stderr)"
        raise RuntimeError(
            f"Gemini CLI failed with exit code {result.returncode}. stderr: {stderr}"
        )

    sys.stdout.write(normalize_output(result.stdout))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
