---
name: rust-programmer
description: Write, refactor, and debug Rust (.rs) code and Cargo projects using idiomatic patterns, safe error handling, ownership/lifetimes guidance, async/concurrency best practices, and a standard verification routine (fmt/clippy/test). Use when tasks involve Rust source files, Cargo.toml workspaces, Rust API design, or Rust performance/safety reviews.
---

# Rust Programmer

Goal: produce idiomatic, safe, and testable Rust with a repeatable verification loop.

## Workflow

### 1) Clarify requirements
- Confirm crate type: **library** vs **binary**.
- Confirm runtime: **sync** vs **async** (Tokio or not).
- Confirm MSRV/toolchain constraints and target platforms.
- Confirm error strategy (public error type vs opaque errors).
- Identify public API surface and backwards-compat expectations.

### 2) Inspect the existing crate/workspace
- Read `Cargo.toml` (features, workspace members, lints, edition).
- Follow the current patterns (error types, logging/tracing, async runtime).
- Locate critical paths via `rg` and call sites (avoid introducing a new style).

### 3) Design before coding
- Use strongly typed data; avoid “stringly typed” APIs.
- Prefer ownership at boundaries and borrowing internally.
- Pick an error model:
  - Library: `thiserror` + a stable error enum.
  - Binary/CLI: `anyhow` + `Context` at boundaries.
- If async: avoid blocking calls in async contexts; use `spawn_blocking` for CPU/IO-bound sync work.

### 4) TDD (required for behavior changes)
- Add deterministic unit tests for pure logic.
- Add integration tests for public API and IO boundaries.
- Avoid timing-dependent tests unless required; keep retries bounded and explicit.

### 5) Implement (idiomatic + minimal diff)
- Prefer iterators, pattern matching, and small focused functions.
- Avoid `unwrap`/`expect` outside tests unless the invariant is proven and documented.
- Avoid `unsafe` unless necessary; document invariants and add coverage.

### 6) Verify
Run the standard checks (fast → slow):
- `cargo fmt --all -- --check`
- `cargo clippy --all-targets --all-features -- -D warnings` (or match repo policy)
- `cargo test --all --all-features`

If useful, run the bundled script: `scripts/cargo_verify.sh`.

## Output expectations
- State assumptions (toolchain, crate type, runtime).
- Summarize what changed and why.
- List verification (commands, tests).
- Call out compatibility risk if public APIs or features change.

## Resources
- `scripts/cargo_verify.sh`: standard local verification runner.
- `references/rust-playbook.md`: deeper patterns and decision notes.
