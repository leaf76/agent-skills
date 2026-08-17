---
name: database-data-guardrails
description: Use when database, SQL, ORM, query builder, migration, transaction, cache, index, EXPLAIN, backfill, data repair, data integrity, or shared data access work is in scope.
---

# Database Data Guardrails

This is a domain-specific expansion of the project's `AGENTS.md` (or equivalent agent rules). It may add database and data requirements, but it must never weaken `AGENTS.md`, `SECURITY`, `parameterized` SQL, input validation, production safety, or destructive-command restrictions.

## Data Access

- Prefer the existing ORM, query builder, or repository pattern. Use raw SQL only when the existing pattern is insufficient.
- SQL must be `parameterized`; never concatenate strings to build SQL.
- Never put user input directly into SQL identifiers, table names, column names, `ORDER BY`, `LIMIT`, or `OFFSET`.
- Dynamic identifiers, sort keys, pagination values, and filter fields must use allowlists or mappings.
- Query and transaction failures must be handled explicitly and retain traceable context.
- Do not use silent fallback to hide DB, model, query, or transaction failures.
- Avoid magic SQL, hidden side effects, and multi-purpose data helpers. Complex queries should be split into named steps or helpers.

## Transactions And Integrity

- Keep transactions to the smallest set of operations that must succeed or fail together.
- Do not include long-running work, external API calls, or unnecessary reads inside transactions.
- For balances, inventory, state transitions, or shared resources, use transactions, locking, unique constraints, or idempotency to prevent race conditions.
- Avoid N+1 queries, full table scans, and unconstrained bulk writes.
- Large reads/writes should use batches, pagination, or chunking.

## Migrations, Backfills, And Indexes

- Prefer backward-compatible expand/contract migrations: support compatible reads/writes first, then remove old paths later.
- For `DROP`, broad `DELETE/UPDATE`, backfill, index rebuild, or high-lock-risk work, state blast radius, rollback/restore path, and verification.
- Database optimization must be based on measurements such as query latency, row scan, index usage, lock wait, `EXPLAIN`, or query plan.
- Do not rewrite queries, add cache, or add indexes based only on intuition.
- Index design must follow real `WHERE`, `JOIN`, `ORDER BY`, and frequent query patterns. Call out write, storage, and read trade-offs.

## Cache Policy

- Cache must define eligible data, cache key, `TTL`, invalidation strategy, and consistency requirements.
- Do not use cache to hide slow queries, data-model issues, or DB errors.
- Cloudflare HTTP/page cache should prefer Cloudflare cache, `fetch` cache controls, or `Cache API`.
- Use `KV` only for read-heavy data where eventual consistency is acceptable.
- Use `Durable Objects` when stateful coordination, atomic updates, centralized invalidation, or Redis-like primitives are needed.
- Use managed Redis / Valkey when broad Redis / Valkey compatibility is required.
- For permissions, personalized content, balances, inventory, or high-consistency data, state stale-data protection against cache poisoning, cache stampede, and cross-user leakage.
