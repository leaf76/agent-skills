# Release Gates

Use this checklist before any publish or deploy action.

## Hard stops

- Stop if the working directory is not a git repository.
- Stop if acceptance criteria or the requested stop point are unclear.
- Stop if the target environment is unclear.
- Stop if production deploy was not explicitly approved in the current release lane.
- Reuse an earlier production approval from the same release lane when the target environment, final diff, deploy path, database lane, blast radius, and rollback risk still match what was approved.
- Stop and ask again if the scope, final diff, deploy path, target environment, database lane, infrastructure/config/permission blast radius, or rollback risk materially changes after the approval.
- Stop if the worktree contains unrelated changes with meaningful conflict risk.
- Stop if verification is missing, failing, or materially incomplete.
- Stop if the release path is unknown and cannot be established from repository evidence.
- Stop if the release depends on database or schema changes and remote migration state has not been checked.
- Stop if schema-dependent code is about to ship while remote migrations are pending, failed, or unverified.

## Commit and push gate

- Confirm the diff is in scope.
- Confirm review findings are either fixed or explicitly accepted by the user.
- Confirm the verification evidence is recent and relevant to the final diff.
- Confirm commit and push are part of the user's requested outcome.

## PR gate

- Prefer a draft PR unless the user explicitly asked for a ready-for-review PR.
- Ensure the PR description explains the change, impact, root cause when relevant, and verification evidence.

## Deploy gate

- Confirm the repository's approved deploy path.
- Confirm the target environment: preview, staging, production, or other named environment.
- For production, confirm approval exists in the current release lane; do not require a duplicate final confirmation when the approval still matches the current deploy.
- Confirm required credentials are present through environment variables, secret manager, or existing authenticated tooling.
- Confirm rollback or restore notes exist for high-risk deploys.
- Confirm data, config, infra, permission, or migration blast radius is understood.
- If the diff touches migrations, schema, repositories, or DB invariants, confirm the remote migration lane:
  - detect pending remote migrations,
  - apply them through the approved path,
  - verify the remote database is fully caught up after apply.
- Do not mark deploy complete until both the code lane and any required database lane have succeeded.

## Output requirements

- State what gate was passed.
- State what blocked progress when a gate fails.
- State the exact step where the flow stopped.
