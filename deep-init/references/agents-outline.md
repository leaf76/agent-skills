# AGENTS Outline

## Purpose

Use this reference when `deep-init` needs to turn repo evidence into a project-specific `AGENTS.md`.

## Minimal sections

1. Purpose and scope
2. Repo snapshot
3. Workflow policy
4. Change safety
5. Verified commands
6. Domain guardrails
7. Validation baseline
8. Repo-specific notes

## Evidence mapping

- `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, `pubspec.yaml`
  Map to stack summary, commands, and language-specific validation rules.
- Lockfiles and workspace markers
  Map to package manager selection and monorepo/workspace boundaries.
- CI files
  Map to required validation and non-optional checks.
- Existing guidance files such as `AGENTS.md`, `CLAUDE.md`, or `CONTRIBUTING.md`
  Preserve stronger rules and merge rather than replace blindly.
- Frontend framework hints and UI directories
  Add frontend guardrails only when the repo actually includes those surfaces.
- Backend/service framework hints and API directories
  Add API error-handling, compatibility, and validation rules when the repo includes backend code.
- Mobile directories or frameworks
  Add mobile-specific reliability, storage, deep-link, and permission notes only when relevant.
- Docker, Terraform, Helm, or infra directories
  Add blast-radius, permission, and troubleshooting notes for infra work.

## Drafting rules

- Prefer imperative bullets and concrete file or command references.
- Keep repo-global rules separate from workspace or package-specific notes.
- Do not invent commands, owners, deployment steps, or team rituals without repo evidence.
- When evidence is weak, write an explicit gap note instead of a fake rule.
- If the repo already has strong global instructions, add only the missing repo-specific guidance.

## Open question prompts

- Which workspace or service should this `AGENTS.md` primarily govern?
- Which commands are mandatory in CI versus optional local helpers?
- Are there generated files, protected directories, or deployment paths that must stay untouched?
