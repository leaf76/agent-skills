# Deploy Discovery

Use this guide when the repository's release path is not already obvious.

## Inspect in this order

1. Read `package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`, and similar entry points for `deploy`, `release`, or `publish` scripts.
2. Check `.github/workflows/` for deployment workflows, environment names, branch triggers, and required approvals.
3. Search the repository for likely deploy commands and platforms:
   - `rg -n "wrangler|vercel|netlify|flyctl|railway|render|helm|kubectl|terraform|pulumi|deploy|release|publish" .`
4. Read project docs such as `README.md`, `docs/`, `AGENTS.md`, or ops runbooks for release instructions.
5. Check for platform config files such as `wrangler.toml`, `cloudflare.json`, `vercel.json`, `netlify.toml`, `fly.toml`, `Dockerfile`, `docker-compose.yml`, or infra directories.
6. Check whether the release also has a database lane:
   - migration directories such as `migrations/`, `db/migrations/`, `schema/`
   - documented migration commands
   - repo changes touching schema, repositories, or database invariants

## Interpret the evidence

- If a repository clearly uses Cloudflare Workers or Pages, route to `cloudflare-deploy`.
- If deployment is handled by GitHub Actions after push or merge, identify the triggering branch and whether manual approval exists.
- If deployment is driven by a local script, inspect the script before running it and confirm its target environment.
- If the repo has a separate database lane, treat it as part of the release path rather than a post-deploy cleanup step.
- If schema changes are present, require evidence for how to list pending remote migrations, how to apply them, and how to verify completion.
- If multiple deploy paths exist, do not guess. Ask which environment and path the user wants.

## Red flags

- Production and preview commands share the same entry point but differ only by hidden environment state.
- A deploy script performs migrations, seed jobs, or destructive infrastructure changes without clear prompts.
- Code deploy and database rollout are separate commands, but only the code lane is documented or executed.
- Remote migrations can be listed, but the release workflow does not require checking or applying them.
- Required secrets or credentials are missing.
- The repo mixes old and new deployment systems and it is unclear which one is active.

## Minimum report

- Chosen deploy path
- Target environment
- Trigger mechanism
- Database or migration lane, if any
- Required credentials or auth state
- Rollback note or restore path
