#!/usr/bin/env python3
"""Collect repo signals to help plan a project-specific AGENTS.md."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    ".turbo",
    ".pnpm-store",
    ".venv",
    "venv",
    "target",
    "bin",
    "obj",
    "vendor",
}

DOC_NAMES = {
    "README.md",
    "README.txt",
    "CONTRIBUTING.md",
    "ARCHITECTURE.md",
}

GUIDANCE_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "COPILOT.md",
    "GEMINI.md",
    "CONTRIBUTING.md",
}

MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Gemfile",
    "pubspec.yaml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
}

LOCK_TO_PACKAGE_MANAGER = {
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "package-lock.json": "npm",
    "npm-shrinkwrap.json": "npm",
    "bun.lockb": "bun",
    "bun.lock": "bun",
}

LANGUAGE_BY_SUFFIX = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".dart": "Dart",
    ".go": "Go",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".lua": "Lua",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".sql": "SQL",
    ".swift": "Swift",
    ".tf": "Terraform",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}

NODE_FRAMEWORKS = {
    "next": "Next.js",
    "react": "React",
    "vue": "Vue",
    "svelte": "Svelte",
    "@angular/core": "Angular",
    "vite": "Vite",
    "express": "Express",
    "@nestjs/core": "NestJS",
    "koa": "Koa",
    "fastify": "Fastify",
    "hono": "Hono",
    "react-native": "React Native",
    "expo": "Expo",
    "electron": "Electron",
}

PYTHON_FRAMEWORKS = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "starlette": "Starlette",
    "sqlalchemy": "SQLAlchemy",
    "pytest": "Pytest",
    "ruff": "Ruff",
}

CANONICAL_SCRIPT_NAMES = [
    "dev",
    "start",
    "build",
    "test",
    "lint",
    "typecheck",
    "format",
    "e2e",
    "storybook",
]


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def read_toml(path: Path) -> dict[str, Any]:
    if tomllib is None:
        return {}
    try:
        return tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def is_ignored_dir(name: str) -> bool:
    return name in IGNORE_DIRS


def iter_repo_files(root: Path, *, max_depth: int = 4, max_files: int = 4000):
    seen = 0
    for current_root, dirnames, filenames in os.walk(root):
        current_path = Path(current_root)
        relative = current_path.relative_to(root)
        depth = len(relative.parts)
        dirnames[:] = [name for name in dirnames if not is_ignored_dir(name)]
        if depth >= max_depth:
            dirnames[:] = []
        for filename in filenames:
            if seen >= max_files:
                return
            seen += 1
            yield current_path / filename


def detect_git(root: Path) -> dict[str, Any]:
    command = ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return {"is_repo": False}

    if result.returncode != 0 or result.stdout.strip() != "true":
        return {"is_repo": False}

    branch_result = subprocess.run(
        ["git", "-C", str(root), "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=False,
    )
    status_result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    dirty_entries = [
        line
        for line in status_result.stdout.splitlines()
        if line.strip()
    ]
    return {
        "is_repo": True,
        "branch": branch_result.stdout.strip() or None,
        "is_dirty": bool(dirty_entries),
        "dirty_entries_preview": dirty_entries[:10],
    }


def detect_package_manager(root: Path, package_json: dict[str, Any]) -> str | None:
    package_manager = package_json.get("packageManager")
    if isinstance(package_manager, str) and package_manager.strip():
        return package_manager.split("@", 1)[0].strip()

    for filename, manager in LOCK_TO_PACKAGE_MANAGER.items():
        if (root / filename).exists():
            return manager

    if (root / "package.json").exists():
        return "npm"

    return None


def format_js_command(package_manager: str | None, script_name: str) -> str:
    if package_manager == "yarn":
        return f"yarn {script_name}"
    if package_manager == "pnpm":
        return f"pnpm run {script_name}"
    if package_manager == "bun":
        return f"bun run {script_name}"
    return f"npm run {script_name}"


def add_command(commands: dict[str, list[str]], key: str, command: str) -> None:
    values = commands.setdefault(key, [])
    if command not in values:
        values.append(command)


def collect_package_json_signals(
    root: Path,
    manifests: list[dict[str, str]],
) -> tuple[set[str], dict[str, list[str]], str | None, bool]:
    framework_hints: set[str] = set()
    commands: dict[str, list[str]] = {}
    has_workspace = False
    root_package = read_json(root / "package.json")
    package_manager = detect_package_manager(root, root_package)

    if root_package:
        dependencies = set()
        for section in ("dependencies", "devDependencies", "peerDependencies"):
            values = root_package.get(section, {})
            if isinstance(values, dict):
                dependencies.update(values.keys())
        framework_hints.update(
            hint for dep, hint in NODE_FRAMEWORKS.items() if dep in dependencies
        )
        scripts = root_package.get("scripts", {})
        if isinstance(scripts, dict):
            for name in CANONICAL_SCRIPT_NAMES:
                if name in scripts:
                    add_command(commands, name, format_js_command(package_manager, name))
        has_workspace = bool(root_package.get("workspaces"))

    if (root / "pnpm-workspace.yaml").exists() or (root / "turbo.json").exists() or (root / "nx.json").exists():
        has_workspace = True

    package_json_count = sum(1 for manifest in manifests if manifest["type"] == "package.json")
    if package_json_count > 1:
        has_workspace = True

    return framework_hints, commands, package_manager, has_workspace


def collect_python_signals(root: Path) -> tuple[set[str], dict[str, list[str]]]:
    framework_hints: set[str] = set()
    commands: dict[str, list[str]] = {}
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        return framework_hints, commands

    pyproject = read_toml(pyproject_path)
    if not pyproject:
        return framework_hints, commands

    dependencies: set[str] = set()

    project = pyproject.get("project", {})
    if isinstance(project, dict):
        dependency_items = project.get("dependencies", [])
        if isinstance(dependency_items, list):
            for item in dependency_items:
                if isinstance(item, str) and item.strip():
                    dependencies.add(item.split()[0].split("[", 1)[0].split(";", 1)[0].split(">=", 1)[0].split("==", 1)[0].split("<", 1)[0].strip())
        optional_dependencies = project.get("optional-dependencies", {})
        if isinstance(optional_dependencies, dict):
            for values in optional_dependencies.values():
                if isinstance(values, list):
                    for item in values:
                        if isinstance(item, str) and item.strip():
                            dependencies.add(item.split()[0].split("[", 1)[0].split(";", 1)[0].split(">=", 1)[0].split("==", 1)[0].split("<", 1)[0].strip())

    tool = pyproject.get("tool", {})
    if isinstance(tool, dict):
        poetry = tool.get("poetry", {})
        if isinstance(poetry, dict):
            poetry_deps = poetry.get("dependencies", {})
            if isinstance(poetry_deps, dict):
                dependencies.update(name for name in poetry_deps.keys() if name != "python")

    framework_hints.update(
        hint for dep, hint in PYTHON_FRAMEWORKS.items() if dep in dependencies
    )

    if (root / "uv.lock").exists() or (isinstance(tool, dict) and "uv" in tool):
        runner = "uv run"
    elif (root / "poetry.lock").exists() or (isinstance(tool, dict) and "poetry" in tool):
        runner = "poetry run"
    else:
        runner = ""

    def prefixed(command: str) -> str:
        return f"{runner} {command}".strip()

    if "pytest" in dependencies or (isinstance(tool, dict) and "pytest" in tool):
        add_command(commands, "test", prefixed("pytest"))
    if "ruff" in dependencies or (isinstance(tool, dict) and "ruff" in tool):
        add_command(commands, "lint", prefixed("ruff check ."))
    if "mypy" in dependencies or (isinstance(tool, dict) and "mypy" in tool):
        add_command(commands, "typecheck", prefixed("mypy ."))
    if "black" in dependencies or (isinstance(tool, dict) and "black" in tool):
        add_command(commands, "format", prefixed("black ."))

    return framework_hints, commands


def collect_rust_signals(root: Path) -> tuple[set[str], dict[str, list[str]]]:
    if not (root / "Cargo.toml").exists():
        return set(), {}
    return {
        "Rust",
    }, {
        "build": ["cargo build"],
        "test": ["cargo test"],
        "lint": ["cargo clippy --all-targets --all-features -- -D warnings"],
        "format": ["cargo fmt --check"],
    }


def collect_go_signals(root: Path) -> tuple[set[str], dict[str, list[str]]]:
    if not (root / "go.mod").exists():
        return set(), {}
    return {
        "Go",
    }, {
        "build": ["go build ./..."],
        "test": ["go test ./..."],
        "lint": ["go vet ./..."],
    }


def detect_surfaces(
    root: Path,
    framework_hints: set[str],
    top_level_dirs: list[str],
) -> list[str]:
    surfaces: list[str] = []

    frontend_hints = {
        "Next.js",
        "React",
        "Vue",
        "Svelte",
        "Angular",
        "Vite",
    }
    backend_hints = {
        "Express",
        "NestJS",
        "Koa",
        "Fastify",
        "Hono",
        "FastAPI",
        "Django",
        "Flask",
        "Starlette",
    }
    mobile_hints = {"React Native", "Expo"}

    if frontend_hints.intersection(framework_hints) or {"app", "web", "ui", "frontend"} & set(top_level_dirs):
        surfaces.append("frontend-ui")
    if backend_hints.intersection(framework_hints) or {"api", "server", "backend", "services"} & set(top_level_dirs):
        surfaces.append("backend-api")
    if mobile_hints.intersection(framework_hints) or {"android", "ios"} & set(top_level_dirs):
        surfaces.append("mobile")
    if (
        (root / "Dockerfile").exists()
        or (root / "docker-compose.yml").exists()
        or (root / "docker-compose.yaml").exists()
        or (root / "infra").exists()
        or (root / "terraform").exists()
        or any((root / folder).exists() for folder in ("k8s", "helm"))
    ):
        surfaces.append("infra-ops")

    return surfaces


def build_recommended_sections(
    commands: dict[str, list[str]],
    surfaces: list[str],
    existing_guidance: list[str],
    is_monorepo: bool,
) -> list[str]:
    sections = [
        "Purpose and scope",
        "Repo snapshot",
        "Change safety",
        "Validation baseline",
    ]
    if commands:
        sections.append("Verified commands")
    if existing_guidance:
        sections.append("Existing instruction merge notes")
    if is_monorepo:
        sections.append("Workspace boundaries")
    if "frontend-ui" in surfaces:
        sections.append("Frontend/UI guardrails")
    if "backend-api" in surfaces:
        sections.append("Backend/API guardrails")
    if "mobile" in surfaces:
        sections.append("Mobile guardrails")
    if "infra-ops" in surfaces:
        sections.append("Infra/Ops guardrails")
    return sections


def collect_risk_notes(
    manifests: list[dict[str, str]],
    existing_guidance: list[str],
    is_monorepo: bool,
    commands: dict[str, list[str]],
) -> list[str]:
    notes: list[str] = []
    if existing_guidance:
        notes.append("Existing guidance files were found. Merge or update them instead of overwriting blindly.")
    if is_monorepo:
        notes.append("Workspace or multi-package signals were found. Separate repo-wide rules from package-specific commands.")
    manifest_paths = [item["path"] for item in manifests if item["path"] != "package.json"]
    if manifest_paths:
        notes.append("Multiple manifest types were found. Cross-check commands against the relevant package or service, not just the repo root.")
    if not commands:
        notes.append("No obvious root-level build or test commands were confirmed. Inspect CI files and package-specific manifests before finalizing AGENTS.md.")
    return notes


def collect_languages(root: Path) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for path in iter_repo_files(root, max_depth=5, max_files=5000):
        suffix = path.suffix.lower()
        language = LANGUAGE_BY_SUFFIX.get(suffix)
        if language:
            counts[language] += 1
    return [
        {"name": name, "files": count}
        for name, count in counts.most_common(8)
    ]


def collect_manifests(root: Path) -> list[dict[str, str]]:
    manifests: list[dict[str, str]] = []
    for path in iter_repo_files(root, max_depth=3, max_files=800):
        if path.name in MANIFEST_NAMES:
            manifests.append(
                {
                    "path": relpath(path, root),
                    "type": path.name,
                }
            )
    manifests.sort(key=lambda item: item["path"])
    return manifests


def collect_named_files(root: Path, names: set[str], *, max_depth: int = 3) -> list[str]:
    matches: list[str] = []
    for path in iter_repo_files(root, max_depth=max_depth, max_files=1200):
        if path.name in names:
            matches.append(relpath(path, root))
    matches.sort()
    return matches


def collect_ci_files(root: Path) -> list[str]:
    candidates = []
    github_dir = root / ".github" / "workflows"
    if github_dir.exists():
        candidates.extend(sorted(relpath(path, root) for path in github_dir.iterdir() if path.is_file()))
    for filename in (".gitlab-ci.yml", ".circleci/config.yml", "azure-pipelines.yml"):
        if (root / filename).exists():
            candidates.append(filename)
    return candidates


def collect_docs(root: Path) -> list[str]:
    docs = set(collect_named_files(root, DOC_NAMES, max_depth=2))
    if (root / "docs").exists():
        docs.add("docs/")
    return sorted(docs)


def collect_top_level_dirs(root: Path) -> list[str]:
    names = []
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        if entry.is_dir() and not is_ignored_dir(entry.name):
            names.append(entry.name)
    return names[:20]


def merge_commands(*command_maps: dict[str, list[str]]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for command_map in command_maps:
        for key, values in command_map.items():
            for value in values:
                add_command(merged, key, value)
    return merged


def collect_inventory(root: Path) -> dict[str, Any]:
    root = root.resolve()
    manifests = collect_manifests(root)
    top_level_dirs = collect_top_level_dirs(root)
    package_frameworks, js_commands, package_manager, is_monorepo = collect_package_json_signals(root, manifests)
    python_frameworks, python_commands = collect_python_signals(root)
    rust_frameworks, rust_commands = collect_rust_signals(root)
    go_frameworks, go_commands = collect_go_signals(root)
    framework_hints = sorted(
        package_frameworks | python_frameworks | rust_frameworks | go_frameworks
    )
    commands = merge_commands(js_commands, python_commands, rust_commands, go_commands)
    surfaces = detect_surfaces(root, set(framework_hints), top_level_dirs)
    existing_guidance = collect_named_files(root, GUIDANCE_NAMES, max_depth=3)
    docs = collect_docs(root)
    ci_files = collect_ci_files(root)
    recommended_sections = build_recommended_sections(
        commands,
        surfaces,
        existing_guidance,
        is_monorepo,
    )
    risk_notes = collect_risk_notes(
        manifests,
        existing_guidance,
        is_monorepo,
        commands,
    )

    return {
        "root": str(root),
        "git": detect_git(root),
        "package_manager": package_manager,
        "manifests": manifests,
        "top_level_dirs": top_level_dirs,
        "languages": collect_languages(root),
        "framework_hints": framework_hints,
        "commands": commands,
        "ci_files": ci_files,
        "docs": docs,
        "existing_guidance": existing_guidance,
        "detected_surfaces": surfaces,
        "is_monorepo": is_monorepo,
        "recommended_sections": recommended_sections,
        "risk_notes": risk_notes,
    }


def render_markdown(inventory: dict[str, Any]) -> str:
    lines = ["# Project Inventory", ""]
    lines.append(f"- Root: `{inventory['root']}`")
    git_info = inventory["git"]
    if git_info.get("is_repo"):
        lines.append(f"- Git repo: yes")
        if git_info.get("branch"):
            lines.append(f"- Branch: `{git_info['branch']}`")
        lines.append(f"- Dirty worktree: `{'yes' if git_info.get('is_dirty') else 'no'}`")
    else:
        lines.append("- Git repo: no")
    if inventory.get("package_manager"):
        lines.append(f"- Package manager: `{inventory['package_manager']}`")
    lines.append("")

    def add_list_section(title: str, values: list[Any], formatter=None) -> None:
        lines.append(f"## {title}")
        if not values:
            lines.append("- None")
            lines.append("")
            return
        for value in values:
            text = formatter(value) if formatter else str(value)
            lines.append(f"- {text}")
        lines.append("")

    add_list_section("Manifests", inventory["manifests"], lambda item: f"`{item['path']}` ({item['type']})")
    add_list_section("Top-level Directories", inventory["top_level_dirs"])
    add_list_section("Languages", inventory["languages"], lambda item: f"{item['name']} ({item['files']} files)")
    add_list_section("Framework Hints", inventory["framework_hints"])

    lines.append("## Commands")
    if not inventory["commands"]:
        lines.append("- None confirmed at repo root")
        lines.append("")
    else:
        for key, values in inventory["commands"].items():
            lines.append(f"- {key}: {', '.join(f'`{value}`' for value in values)}")
        lines.append("")

    add_list_section("CI Files", inventory["ci_files"], lambda value: f"`{value}`")
    add_list_section("Docs", inventory["docs"], lambda value: f"`{value}`")
    add_list_section("Existing Guidance", inventory["existing_guidance"], lambda value: f"`{value}`")
    add_list_section("Detected Surfaces", inventory["detected_surfaces"])
    add_list_section("Recommended AGENTS Sections", inventory["recommended_sections"])
    add_list_section("Risk Notes", inventory["risk_notes"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a repository and summarize AGENTS-relevant signals.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Target repository root (defaults to current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"[ERROR] Path not found: {root}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"[ERROR] Path is not a directory: {root}", file=sys.stderr)
        return 1

    inventory = collect_inventory(root)
    if args.format == "json":
        print(json.dumps(inventory, indent=2, sort_keys=True))
    else:
        print(render_markdown(inventory), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
