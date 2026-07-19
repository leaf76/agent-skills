# Schema Analysis Reference

Use this reference for DDL, ORM models, table definitions, index inventories, and relationship reviews.

## Review Order

1. Identify entities and their primary write and read paths.
2. Check keys, constraints, and relationship shape.
3. Check data types, nullability, defaults, and generated values.
4. Check indexing against expected access patterns.
5. Check for maintainability and future migration risk.

## Core Checklist

### Table and entity shape

- Verify each table has a clear responsibility.
- Flag tables that mix unrelated domains or lifecycle states.
- Flag columns that store multiple meanings in one field.
- Flag repeated groups that should likely be separate rows.

### Primary keys and identifiers

- Verify every table has a stable primary key.
- Check whether the key shape fits access patterns and replication needs.
- Flag mutable business keys used as the only identifier.
- Flag natural keys that are too wide for joins or secondary indexes.

### Foreign keys and relationship integrity

- Verify important relationships are enforced, not only implied in application code.
- Check nullable foreign keys for ambiguous ownership or lifecycle problems.
- Flag orphan-risk tables when deletes or state transitions can break integrity.
- Check many-to-many tables for duplicate row risk and missing uniqueness constraints.

### Data types, nullability, and defaults

- Verify IDs, timestamps, money values, counters, status fields, and booleans use sensible types.
- Flag text columns used for numeric or structured data unless intentionally serialized.
- Flag nullable columns when null and empty or zero appear to mean different things.
- Check defaults for correctness and migration safety.

### Constraints and invariants

- Look for missing unique constraints on user-facing identifiers, mapping tables, and idempotency keys.
- Look for missing check constraints on bounded states, ranges, or mutually exclusive fields.
- Call out invariants enforced only in application code if the database should also guard them.

### Indexing

- Check whether indexes match common predicates, joins, sort order, and uniqueness needs.
- Flag redundant indexes where one index fully prefixes another and both serve the same workload.
- Flag write-heavy tables with too many overlapping indexes.
- Flag indexes that support filtering but not required ordering, or vice versa.

## Common Findings

### Integrity risks

- Missing foreign keys on ownership-critical rows
- Missing uniqueness on join tables or external IDs
- Nullability that hides incomplete writes
- Status columns without bounded states

### Performance risks

- Large text columns in frequently scanned tables
- Unindexed foreign keys used for joins
- Timestamp or status filters without matching indexes
- Wide composite indexes that do not align with real predicate order

### Migration risks

- Renames that will break old code paths
- Type changes that need backfill or dual-read handling
- New non-null columns without safe defaults or phased rollout
- Constraints added before data is cleaned up

## Questions to Ask Only When Needed

- Which database engine and version is this?
- What are the hottest read and write paths?
- Roughly how large are the affected tables?
- Are there existing data-quality problems or legacy nulls?

Ask only when the answer materially changes the conclusion.

## Output Pattern

For each finding:

1. Name the issue
2. Point to the exact schema evidence
3. Explain the impact on correctness, performance, or operability
4. Suggest the smallest safe next action

## Cross-Database Cautions

- Do not assume partial indexes, online DDL, generated columns, or deferrable constraints exist everywhere.
- Do not assume identifier case rules or timestamp semantics are the same across engines.
- If recommending vendor-specific features, label them as conditional on engine support.
