---
name: infra-ops-mobile-guardrails
description: Use when deployment, infrastructure, Cloudflare, object storage, logging, observability, resource permissions, production rollout, migration timing, mobile retries, or idempotency work is in scope.
---

# Infra Ops Mobile Guardrails

This is a domain-specific expansion of the project's `AGENTS.md` (or equivalent agent rules). It may add infrastructure, operations, and mobile requirements, but it must never weaken `AGENTS.md`, `SECURITY`, secrets handling, production safety, or destructive-command restrictions.

## Infrastructure And Deployment

- State resource, config, permission, and blast-radius changes before making infrastructure or deployment changes.
- Do not perform experimental operations directly in production without explicit developer approval.
- Prefer GitHub-centered CI/CD such as `GitHub Actions`, `Cloud Build`, or GitHub workflow-triggered `wrangler`.
- Default deploy triggers should be push to `main` / `master` or release `tag` so deploy logic, version metadata, and artifacts stay tied to version control events.
- Avoid manual deployment drift unless the task explicitly requires a manual deploy.
- Before deploy, confirm tests/checks appropriate to the risk have completed.
- If schema or data migration is involved, state deploy order, migration execution timing, backward compatibility, rollback/restore path, and post-deploy verification.

## Logging And Observability

- Distributed systems should prefer centralized `Cloud Logging`, an observability platform, or an equivalent system.
- Correlate logs, metrics, traces, and requests with stable correlation identifiers.
- Avoid relying on local logs that cannot be correlated across services.
- Provide minimal troubleshooting notes for failure cases.
- Avoid high-cardinality logs or metrics.

## Object Storage

- Cloud object storage may use `R2`, `Cloud Storage`, or equivalent object storage based on project needs.
- Define bucket/container permissions, access boundary, encryption, retention/lifecycle policy, and cost impact.
- For external sharing, prefer short-lived signed URL / presigned URL access.
- Do not hardcode storage credentials, bucket secrets, or environment-specific endpoints.

## Mobile Reliability

- Mobile networks are unreliable and apps may be suspended or killed in the background.
- Retries must be bounded and idempotent.
- State the impact on auth, session, storage, deep links, permissions, and backward compatibility.
- Avoid hidden behavior changes in background sync, retry, token refresh, and offline paths.
