# Query Analysis Reference

Use this reference for SQL review, EXPLAIN interpretation, indexing suggestions, and performance RCA from query artifacts.

## Review Order

1. Confirm the query is semantically correct.
2. Identify the expensive operations.
3. Match predicates, joins, grouping, sorting, and pagination to available indexes.
4. Separate confirmed bottlenecks from hypotheses that need more evidence.

## Correctness First

- Verify joins cannot multiply rows unexpectedly.
- Verify filters apply at the intended stage.
- Verify aggregation matches the business question.
- Verify pagination is deterministic when order matters.
- Verify timezone, null, and duplicate semantics are handled intentionally.

Do not suggest performance changes until the query logic is trustworthy.

## Query Review Checklist

### Predicates and selectivity

- Check equality, range, and prefix filters.
- Check whether functions or casts make predicates non-sargable.
- Check whether optional filters lead to wide scans.
- Check whether the most selective predicates can use an index.

### Joins

- Check join keys for type consistency and uniqueness assumptions.
- Flag joins on expressions or transformed values.
- Flag accidental cross joins or missing predicates.
- Check whether outer joins are necessary or masking data issues.

### Sorting, grouping, and pagination

- Check whether sort columns are indexed in useful order.
- Check whether group-by columns explode cardinality.
- Flag offset pagination on large result sets when keyset pagination is more stable.
- Flag distinct used to hide duplicate joins instead of fixing the join logic.

### Projection and row width

- Flag select-star on wide tables when only a few columns are needed.
- Flag large text or JSON columns fetched in latency-sensitive paths.
- Check whether the query returns more rows than the caller can consume.

## EXPLAIN Interpretation

Read plans as evidence, not as labels alone.

### What to look for

- Full table or full index scans on large tables
- Join order that starts from non-selective inputs
- Large sort or hash operations
- Materialization, temp storage, or repeated subplans
- Estimated rows versus actual rows when both are available

### High-signal mismatches

- Huge row estimate error can indicate stale statistics, skew, or correlated predicates.
- A good index that is ignored can indicate poor selectivity, incompatible ordering, or outdated stats.
- A plan that is fast on small samples may still fail at production scale if row counts or row width explode.

## Index Suggestion Heuristics

- Start from the actual filter, join, and order-by pattern.
- Prefer one index that matches the dominant access path over many speculative indexes.
- Consider write cost and maintenance cost before adding composite indexes.
- Verify existing indexes are not already sufficient with a different query shape.

## Common Anti-Patterns

- Function-wrapped indexed columns in predicates
- Leading wildcard searches on plain b-tree indexes
- Repeated correlated subqueries when a join or pre-aggregation would be clearer
- Using OR across unrelated columns without understanding index impact
- Dynamic ORDER BY or LIMIT values without allowlisting

## Evidence Gaps

If the artifact set is incomplete, ask for the smallest missing proof:

- Bound parameters, not only SQL text
- Table sizes or rough row counts
- Index definitions
- EXPLAIN output with actual timing if available
- A sample of the result shape if correctness is uncertain

## Output Pattern

For each query finding:

1. State whether it is a correctness or performance issue
2. Cite the relevant SQL fragment or plan node
3. Explain the impact
4. Recommend the smallest safe next action or check

## Cross-Database Cautions

- Do not assume every engine uses the same plan terminology.
- Do not assume CTEs, optimizer hints, or index-only scans behave the same everywhere.
- Label engine-specific advice explicitly when the engine is known.
