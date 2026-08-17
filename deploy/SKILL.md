---
name: deploy
description: Decide how a project should be deployed before executing anything. Use when Codex needs to deploy, release, publish, ship, determine whether a repo deploys via GitHub Actions or direct tooling, or review current changes before commit/push and deployment.
allowed-tools: Read, Grep, Glob, Bash
---

# Deploy Project

Use this skill as the deployment workflow controller. Do not start by running `wrangler deploy`, `gcloud run deploy`, `docker push`, or `git push` blindly.

## Required Workflow

Follow these steps in order every time:

1. Confirm repository state.
2. Review current staged and unstaged changes.
3. Detect the deployment entry point.
4. Present the decision, evidence, fallback paths, and risks.
5. Confirm with the user.
6. Execute the approved deployment path.

If any step is ambiguous, stop and ask instead of guessing.

## 1. Confirm Repository State

Start with:

```bash
git rev-parse --is-inside-work-tree
git status --short --branch
git remote -v
```

Check for:

- Current branch and whether it tracks a remote
- Dirty tracked changes
- Untracked files that may belong to another task
- Protected-branch or release-branch risk

Stop and ask the user if:

- The directory is not a git repository
- There is no remote and the deployment path requires `push`
- The worktree is dirty in a way that may mix unrelated scope
- You cannot tell which branch should trigger deployment

## 2. Review Current Changes Before Commit / Push

Before any commit or push, follow the review workflow in:

- `review-changes/SKILL.md` (sibling skill in this library)

Minimum required checks:

```bash
git diff --cached
git diff
git diff --name-only --cached
git diff --name-only
```

Guardrails:

- Do not commit while blocking review findings remain unresolved.
- Do not absorb unrelated dirty changes just to make deployment work.
- Do not push changes you do not understand.
- If the repo has mixed staged and unstaged edits from different scopes, stop and ask the user how to separate them.

## 3. Detect the Deployment Entry Point

Collect evidence from these sources before deciding:

```bash
find .github/workflows -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \)
rg -n "deploy|release|publish|workflow_dispatch|wrangler|gcloud|docker push|docker buildx|cloudflare" .github/workflows
rg --files -g 'wrangler.toml' -g 'wrangler.json' -g 'wrangler.jsonc' -g 'cloudbuild.yaml' -g 'app.yaml' -g 'Dockerfile' -g 'Makefile' -g 'justfile' -g 'package.json'
rg -n '"(deploy|release|publish)"\\s*:' package.json
rg -n "wrangler|gcloud|docker (build|push)|artifact registry|gcr\\.io|pkg\\.dev" package.json Makefile justfile
```

### Evidence to Prioritize

- `.github/workflows/*.yml` / `.yaml`
- `wrangler.toml`, `wrangler.json`, `wrangler.jsonc`
- `cloudbuild.yaml`, `app.yaml`
- `Dockerfile`
- `package.json` deploy or release scripts
- `Makefile` or `justfile` deploy targets

### Decision Rules

Use this precedence:

1. **GitHub Actions wins** when a workflow clearly contains deploy / publish / release intent, or uses `wrangler`, `gcloud`, image push, or a production trigger.
2. **Cloudflare direct deploy** when no deploy workflow exists and Cloudflare signals are the strongest evidence.
3. **GCP direct deploy** when no deploy workflow exists and GCP signals are the strongest evidence.
4. **Docker / registry deploy** only when container signals exist and there is no stronger workflow or platform signal.
5. **Stop for clarification** when multiple platform signals conflict and no primary entry point can be justified.

### Interpreting Mixed Signals

- `.github/workflows/*` plus `wrangler.toml`: treat GitHub Actions as the primary entry and Wrangler as the underlying tool.
- `.github/workflows/*` plus `cloudbuild.yaml`: treat GitHub Actions as the primary entry and GCP as the underlying platform.
- `cloudbuild.yaml` plus `Dockerfile`: treat GCP as primary and Docker as part of the packaging path.
- `wrangler.toml` plus `cloudbuild.yaml`: ambiguous without more evidence; stop and ask.

## 4. Present the Deployment Entry Decision

Before acting, report:

- `review summary`
- `deployment entry decision`
- `evidence`
- `fallback paths`
- `risk flags`
- `recommended next step`

Use a compact structure like:

```text
Review summary:
- staged changes: ...
- unstaged changes: ...
- blocking findings: yes/no

Deployment entry decision:
- primary: github-actions
- evidence:
  - .github/workflows/deploy.yml calls wrangler deploy on push to main
  - wrangler.toml exists, so Wrangler is the underlying direct tool
- fallback paths:
  - cloudflare direct deploy
- risk flags:
  - dirty worktree
  - production intent not yet confirmed
```

Do not move forward until the user confirms the route.

## 5. Execute the Approved Path

### Path A: GitHub Actions Is the Primary Entry

Use this path when workflow evidence is clear.

Required sequence:

1. Finish review and resolve blocking findings.
2. Confirm the intended branch and scope.
3. Commit only the intended changes.
4. Push the branch that should trigger deployment.
5. Report which workflow file is expected to run.
6. If available, inspect the workflow run and report its status.

Recommended commands:

```bash
git status --short --branch
git add <intended-files>
git commit -m "chore: prepare deployment"
git push -u origin "$(git branch --show-current)"
```

If `gh` is available and authenticated, inspect the latest run:

```bash
gh auth status
gh run list --limit 5
gh run view <run-id>
```

Do not claim success unless you verified the workflow ran or clearly state that verification was skipped.

### Path B: Direct Cloudflare Deploy

Use only when no GitHub Actions deployment entry is present or the user explicitly asked to bypass it.

Preflight:

```bash
npx wrangler whoami
```

Deploy:

```bash
npx wrangler deploy
npx wrangler deploy --env staging
```

Do not push secrets from plaintext files. Use Wrangler secrets instead:

```bash
echo "secret-value" | npx wrangler secret put SECRET_NAME
```

### Path C: Direct GCP Deploy

Preflight:

```bash
gcloud auth list
```

Deploy from source:

```bash
gcloud run deploy SERVICE_NAME \
  --source . \
  --region REGION \
  --allow-unauthenticated
```

Deploy from an existing image:

```bash
gcloud run deploy SERVICE_NAME \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO/IMAGE:TAG \
  --region REGION \
  --allow-unauthenticated
```

Prefer environment variables and secret bindings over hardcoded config:

```bash
gcloud run deploy SERVICE_NAME \
  --source . \
  --region REGION \
  --set-env-vars "KEY1=value1" \
  --set-secrets "SECRET1=secret-name:latest"
```

### Path D: Direct Docker / Registry Publish

Use only when container publishing is the actual release path.

Preflight:

```bash
docker info
test -f "${DOCKER_CONFIG:-$HOME/.docker}/config.json"
```

Build and push:

```bash
docker build -t myapp:latest .
docker tag myapp:latest REGISTRY/myapp:TAG
docker push REGISTRY/myapp:TAG
```

If multi-platform output is required:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t REGISTRY/myapp:TAG \
  --push .
```

## Commit / Push Guardrails

- Do not commit with unresolved blocking findings.
- Do not push directly to a protected or production branch unless the user explicitly asked and the repo policy allows it.
- Do not deploy to production unless the user clearly requested production.
- If the release branch or environment is unclear, ask.
- If the repo uses GitHub Actions as the deployment entry, do not bypass it with a direct deploy unless the user explicitly chooses to.

## Use the Bundled Script

Use `scripts/deploy.sh` for quick detection and guarded direct deployment.

Supported commands:

```bash
./scripts/deploy.sh detect
./scripts/deploy.sh --detect-only
./scripts/deploy.sh auto
./scripts/deploy.sh deploy cloudflare
./scripts/deploy.sh deploy cloudrun
./scripts/deploy.sh deploy docker
./scripts/deploy.sh deploy gce
```

Interpretation:

- `detect` / `--detect-only`: print the current deployment-entry decision and evidence only
- `auto`: allow direct deployment only when GitHub Actions is not the primary entry
- `deploy <target>`: execute a direct deployment intentionally, even if a workflow also exists

## Rollback Notes

- GitHub Actions: redeploy or rollback through the repo's workflow and environment policy
- Cloud Run: shift traffic to a previous revision
- Cloudflare Workers: use `npx wrangler rollback`
- Docker: redeploy a previously known-good image tag

## Output Contract

Always report:

1. `review summary`
2. `deployment entry decision`
3. `commit SHA / branch` when a push happened
4. `workflow run or deployed URL` when available
5. `warnings / follow-ups`

If verification was skipped, say so explicitly and explain why.
