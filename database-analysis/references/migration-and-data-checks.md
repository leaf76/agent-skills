# Migration and Data Checks Reference

Use this reference for schema migrations, backfills, data repair plans, compatibility reviews, and integrity validation planning.

## Review Order

1. Classify the change shape.
2. Check backward compatibility for old and new code paths.
3. Check data integrity before, during, and after rollout.
4. Check rollback or restore feasibility.
5. Produce a minimal validation plan.

## Change Classification

Classify the proposed change before analyzing details:

- Additive schema change
- Rename or semantic replacement
- Type change
- Constraint or index change
- Backfill or data repair
- Destructive cleanup after migration

Each class has different rollout and rollback expectations.

## Compatibility Checklist

### Expand phase

- Add new columns or tables in a way old code can ignore safely.
- Keep old reads and writes working while the new path rolls out.
- Avoid making new fields mandatory before all writers can populate them.

### Transition phase

- Check whether dual-write, dual-read, or backfill coordination is required.
- Check idempotency for retryable backfills and repair jobs.
- Check whether the job can resume safely after interruption.

### Contract phase

- Remove old columns, constraints, or code paths only after compatibility windows are closed.
- Verify that old readers, workers, and batch jobs are no longer active.

## Integrity Checks

Plan both success and failure checks.

### Before the change

- Measure existing nulls, duplicates, or orphan rows.
- Verify assumptions that new constraints depend on.
- Identify rows that will fail type conversion or new validation rules.

### During the change

- Track progress with deterministic batches when data volume is large.
- Check for race conditions with live writes.
- Check whether long-running transactions or locks can affect availability.

### After the change

- Verify row counts, uniqueness, referential integrity, and application-visible correctness.
- Verify new writes land in the expected shape.
- Verify old paths fail safely or are fully removed, depending on rollout stage.

## Common Risks

- Renames presented as simple edits when they require phased compatibility
- Type narrowing that truncates or rejects existing values
- Non-null constraints added before backfill is complete
- Large updates without batching or resume logic
- Backfills that depend on current application state and are not repeatable
- Rollback plans that restore schema but not data semantics

## Read-Only Investigation Guidance

Default to artifact review. If the user asks for live database checks:

- Prefer read-only verification queries.
- Avoid full-table scans on large production tables unless the user explicitly accepts the cost.
- Ask for engine, scale, and environment before suggesting operational checks that might be expensive.

## Validation Plan Template

When proposing validation, include:

1. Preconditions to check before rollout
2. Success checks during rollout
3. Failure signals and how to stop safely
4. Post-rollout integrity checks
5. Rollback or restore notes if the change is not easily reversible

## Output Pattern

For each migration or data-risk finding:

1. State the change class
2. Point to the schema or rollout evidence
3. Explain the compatibility or integrity risk
4. Recommend the smallest safe mitigation or validation step

## Cross-Database Cautions

- Do not assume online schema change behavior is portable.
- Do not assume locking cost, transactional DDL, or rollback semantics are the same across engines.
- Label engine-specific migration advice as conditional when support is uncertain.
