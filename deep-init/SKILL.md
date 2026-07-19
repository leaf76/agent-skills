---
name: deep-init
description: Inspect a repository and plan or draft a project-specific AGENTS.md using evidence from manifests, commands, CI files, architecture hints, and existing guidance docs. Use when bootstrapping agent instructions for a new project, refreshing stale AGENTS.md rules after repo changes, or when a user wants repo-grounded working rules instead of a generic template.
---

# Deep Init

## Overview

Inspect the target repository before writing guidance. Start from repo facts, not generic policy boilerplate, and turn those facts into a concise AGENTS plan or draft.

## Workflow

1. Set the target root.
- Default to the current working directory unless the user points to another repo.
- Decide whether the request is:
  - planning only
  - creating a new `AGENTS.md`
  - updating an existing `AGENTS.md`

2. Gather repo evidence first.
- Resolve `scripts/project_inventory.py` relative to this skill directory, then run `python3 <that-path> <repo-root>` before drafting anything.
- Use `--format json` when you need machine-readable output for follow-up processing or tests.
- Treat the inventory as a map for what to inspect next, not as the final answer.
- Read only the files supported by those signals: root docs, manifests, CI files, lint/type/test configs, existing guidance docs, and the most relevant top-level app or service directories.

3. Convert evidence into AGENTS rules.
- Keep rules operational and repo-specific.
- Only include commands that are confirmed by manifests, scripts, or CI configuration.
- Separate repo-wide policy from workspace-specific notes when monorepo signals exist.
- Preserve stronger existing instructions instead of weakening or rewriting them.
- Explicitly call out uncertainty when evidence is missing or contradictory.

4. Shape the output to the request.
- For planning-only requests, return:
  - evidence summary
  - proposed `AGENTS.md` sections
  - repo-specific risks or gaps
  - open questions that genuinely block a safe draft
- For drafting requests, keep the file concise and include only the sections the repo actually needs.

## Default Sections

- Purpose and scope
- Repo snapshot
- Workflow policy
- Change safety
- Verified commands
- Domain guardrails
- Validation baseline
- Repo-specific notes

Skip sections that are not supported by repo evidence. Add workspace boundaries only when the repo shows monorepo or multi-service structure.

## Output Rules

- Keep planning and explanations in Traditional Chinese unless the repo clearly standardizes another documentation language.
- Keep generated `AGENTS.md` content in the repo's documentation language when obvious; otherwise default to English for compatibility with agent tooling.
- Never invent commands, owners, deployment steps, or hidden process requirements.
- Never weaken existing security, validation, or change-safety rules without explicit user instruction.

## Resources

- Use `scripts/project_inventory.py` to summarize manifests, languages, framework hints, commands, CI files, and AGENTS-relevant risk notes.
- Use `references/agents-outline.md` when turning repo signals into concrete `AGENTS.md` sections.
- Use `scripts/test_project_inventory.py` to regression-check the inventory logic after changes.
