#!/usr/bin/env python3
"""Tests for project_inventory.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("project_inventory.py")
SPEC = importlib.util.spec_from_file_location("project_inventory", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ProjectInventoryTests(unittest.TestCase):
    def test_node_frontend_repo_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "web-app",
                        "packageManager": "pnpm@9.0.0",
                        "scripts": {
                            "dev": "next dev",
                            "build": "next build",
                            "test": "vitest run",
                            "lint": "eslint .",
                        },
                        "dependencies": {
                            "next": "15.0.0",
                            "react": "19.0.0",
                        },
                        "devDependencies": {
                            "typescript": "5.0.0",
                        },
                    }
                )
            )
            (root / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'")
            (root / "AGENTS.md").write_text("# Existing guidance\n")
            (root / "Dockerfile").write_text("FROM node:20\n")
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")
            (root / "app").mkdir()
            (root / "app" / "page.tsx").write_text("export default function Page() { return null; }\n")
            (root / "src").mkdir()
            (root / "src" / "util.ts").write_text("export const value = 1;\n")

            inventory = MODULE.collect_inventory(root)

            self.assertEqual(inventory["package_manager"], "pnpm")
            self.assertIn("Next.js", inventory["framework_hints"])
            self.assertIn("frontend-ui", inventory["detected_surfaces"])
            self.assertIn("infra-ops", inventory["detected_surfaces"])
            self.assertEqual(inventory["commands"]["build"], ["pnpm run build"])
            self.assertIn("AGENTS.md", inventory["existing_guidance"])
            self.assertIn(".github/workflows/ci.yml", inventory["ci_files"])

    def test_python_backend_repo_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text(
                """
[project]
name = "api-service"
dependencies = ["fastapi>=0.115.0", "pytest>=8.0.0", "ruff>=0.6.0", "mypy>=1.0.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
""".strip()
                + "\n"
            )
            (root / "uv.lock").write_text("version = 1\n")
            (root / "api").mkdir()
            (root / "api" / "main.py").write_text("from fastapi import FastAPI\n")
            (root / "tests").mkdir()
            (root / "tests" / "test_main.py").write_text("def test_ok():\n    assert True\n")

            inventory = MODULE.collect_inventory(root)

            self.assertIn("FastAPI", inventory["framework_hints"])
            self.assertIn("backend-api", inventory["detected_surfaces"])
            self.assertEqual(inventory["commands"]["test"], ["uv run pytest"])
            self.assertEqual(inventory["commands"]["lint"], ["uv run ruff check ."])
            self.assertEqual(inventory["commands"]["typecheck"], ["uv run mypy ."])
            self.assertIn("Backend/API guardrails", inventory["recommended_sections"])


if __name__ == "__main__":
    unittest.main()
