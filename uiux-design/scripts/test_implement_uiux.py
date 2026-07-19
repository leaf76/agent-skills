#!/usr/bin/env python3
"""Basic tests for implement_uiux.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent / "implement_uiux.py"
SPEC = importlib.util.spec_from_file_location("implement_uiux", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load module from {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ImplementUiuxTests(unittest.TestCase):
    def test_parser_defaults_to_safe_cli_settings(self) -> None:
        parser = MODULE.build_parser()
        args = parser.parse_args(["--brief", "Adjust the dashboard hero spacing."])
        self.assertEqual(args.approval_mode, "auto_edit")
        self.assertEqual(args.extensions, "")

    def test_build_prompt_contains_guardrails(self) -> None:
        prompt = MODULE.build_prompt(
            brief="Implement the approved dashboard hero spacing and preserve the CTA copy.",
            must_preserve=["CTA label must stay exactly `Start free trial`."],
            context_blocks=[],
        )
        self.assertIn("- Read the existing code before editing any files.", prompt)
        self.assertIn("- Limit edits to task-relevant files only.", prompt)
        self.assertIn("- Do not perform unrelated refactors, renames, cleanup, or architecture changes.", prompt)
        self.assertIn("CTA label must stay exactly `Start free trial`.", prompt)
        self.assertIn("Recommend Chrome DevTools checks first", prompt)

    def test_build_command_includes_expected_defaults(self) -> None:
        command = MODULE.build_command(
            "Prompt body",
            model=None,
            approval_mode="auto_edit",
            extensions="",
            include_directories=[Path("/tmp/demo-app")],
        )
        self.assertIn("--approval-mode", command)
        self.assertIn("auto_edit", command)
        self.assertIn("--extensions", command)
        self.assertIn("", command)
        self.assertIn("--include-directories", command)
        self.assertIn("/tmp/demo-app", command)

    def test_read_context_files_rejects_large_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            context_path = Path(tmp_dir) / "too-large.md"
            context_path.write_text("x" * (MODULE.MAX_CONTEXT_FILE_BYTES + 1), encoding="utf-8")

            with self.assertRaises(ValueError):
                MODULE.read_context_files([str(context_path)])

    def test_resolve_include_directories_rejects_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "note.txt"
            file_path.write_text("hello", encoding="utf-8")

            with self.assertRaises(ValueError):
                MODULE.resolve_include_directories([str(file_path)])


if __name__ == "__main__":
    unittest.main()
