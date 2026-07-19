---
name: database-analysis
description: Analyze relational database artifacts such as DDL, migrations, ORM models, SQL queries, EXPLAIN plans, and sample result sets. Use when Codex needs cross-database, read-only review of schema design, query behavior, indexing, migration safety, data integrity risk, or evidence-driven next checks without defaulting to live production access.
---

# Database Analysis

## Overview

Use this skill to review database-related artifacts without assuming direct database access. Start from evidence, keep recommendations reversible, and highlight unknowns instead of guessing.

## Quick Triage

Classify the request before going deep:

- Use schema analysis for DDL, migrations, ORM models, table definitions, indexes, or relationship questions.
- Use query analysis for SQL text, performance complaints, EXPLAIN output, or indexing suggestions.
- Use migration and data checks for backfills, type changes, renames, constraint changes, or data repair plans.
- Combine paths only when the artifacts clearly overlap.

Load only the references that match the task:

- `references/schema-analysis.md`
- `references/query-analysis.md`
- `references/migration-and-data-checks.md`

## Default Workflow

### 1. Inventory the evidence

List what is available and what is missing:

- Database engine and version
- DDL, migration files, or ORM models
- SQL text and bound parameters
- EXPLAIN or execution-plan output
- Table sizes, cardinality hints, or sample result sets
- Existing incidents, error messages, or latency symptoms

If a missing fact changes the conclusion, state the gap explicitly. Ask only for the smallest artifact that unlocks the next step.

### 2. Pick the narrowest analysis lane

Prefer one primary lane:

- Structure and consistency
- Query correctness and performance
- Migration safety and data integrity

Avoid broad “optimize the whole database” advice when the evidence only supports one area.

### 3. Analyze from artifact to conclusion

Work from observable evidence:

- Quote or summarize the relevant schema, SQL fragment, or plan node.
- Explain why it matters.
- Distinguish confirmed findings from informed hypotheses.
- Name the smallest safe next check when proof is incomplete.

Do not rely on vendor-specific behavior unless the engine is known.

### 4. Produce findings-first output

Order the response like this:

1. Findings, ordered by severity or likely impact
2. Supporting evidence
3. Evidence gaps or assumptions
4. Safe next checks or validation steps

Keep recommendations actionable. Prefer “add or verify an index matching these predicates” over generic tuning advice.

## Safety Rules

- Default to artifact-first, read-only analysis.
- Do not assume direct database access.
- Do not run write statements, destructive checks, or production experiments by default.
- If the user explicitly requests live investigation, confirm that the access is read-only and avoid production-impacting queries.
- Flag any SQL injection risk, unsafe dynamic identifiers, or missing input validation immediately.
- Prefer parameterized SQL and allowlisted identifier mappings in all examples.

## Analysis Heuristics

- Separate correctness problems from performance problems. A fast wrong query is still wrong.
- Check join cardinality, filter selectivity, sorting, grouping, and pagination before suggesting indexes.
- Treat missing constraints, weak nullability, or inconsistent naming as integrity risks, not just style issues.
- For migration work, prefer expand/contract thinking and call out rollback difficulty.
- When sample sizes or statistics are absent, avoid claiming exact performance outcomes.

## Output Expectations

When responding, include:

- A short statement of what was analyzed
- Findings first, with concrete evidence
- Cross-database-safe guidance unless the engine is known
- Explicit assumptions and unknowns
- A validation or follow-up checklist when relevant

## Example Triggers

- “Review this schema dump and tell me what is risky.”
- “Analyze this SQL query and EXPLAIN output.”
- “Check whether this migration plan is backward compatible.”
- “Look at these ORM models and infer database design problems.”
