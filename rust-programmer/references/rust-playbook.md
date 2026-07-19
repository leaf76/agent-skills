# Rust Playbook

Use this file when a task needs deeper guidance than the main workflow (API design, error strategy, async pitfalls, testing patterns).

## Error handling (rule of thumb)

### Library crates
- Expose a stable, semver-aware error type: `pub enum Error { ... }`.
- Prefer `thiserror` for ergonomic definitions.
- Use `Result<T, Error>` in public APIs. Avoid leaking dependency errors unless that is an explicit design choice.
- Add context at boundaries by mapping dependency errors into your error enum.

### Binary/CLI crates
- Prefer `anyhow::Result<T>` for top-level flows.
- Add context at boundaries with `anyhow::Context` so failures are actionable.

## Ownership and lifetimes (boundary-first)

- Prefer **owned** types at module and API boundaries (e.g., `String`, `PathBuf`, `Vec<T>`).
- Prefer **borrowing** internally when it reduces allocations and improves clarity.
- If you need “borrow-or-own”, consider `Cow<'a, str>` or `Cow<'a, [T]>`.
- Avoid cloning “by default”; clone only when it is a documented tradeoff.

## Async and blocking pitfalls

- Do not block inside async tasks (filesystem, CPU-heavy parsing, synchronous DB clients).
- If you must call blocking code from async:
  - Use `tokio::task::spawn_blocking` for CPU-heavy or blocking IO.
  - Keep the blocking section small; pass owned data in/out.
- Prefer explicit timeouts at IO boundaries (HTTP, DB, RPC).

## API design checklist (public-facing)

- Choose names that read well at call sites.
- Prefer small composable functions over a single “do everything” function.
- Separate parsing/validation from side effects when possible.
- Use `Option<T>` only when “missing” is a valid state; otherwise use `Result<T, Error>`.
- Consider feature flags for optional dependencies and platform-specific code.

## Common crates (pick intentionally)

- CLI: `clap`
- Serialization: `serde` (+ `serde_json`, `toml`, `serde_yaml` as needed)
- Errors: `thiserror` (libs), `anyhow` (bins)
- Logging/tracing: `tracing`, `tracing-subscriber`
- HTTP client: `reqwest`
- HTTP server: `axum` (Tokio)

Do not add a new dependency if the repo already has an established alternative.

## Testing patterns

- Unit tests for pure logic live close to the code.
- Integration tests (`tests/`) cover the public API and behavior across modules.
- Prefer table-driven tests for parsing/validation.
- Avoid non-deterministic timing tests; if unavoidable, bound retries and use timeouts.

## Performance hygiene (when it matters)

- Avoid `O(n^2)` hidden loops; watch for repeated `.clone()` in loops.
- Prefer iterators and borrowing, but optimize only with evidence.
- Use `cargo bench` / `criterion` when the change is performance-sensitive.

## Unsafe code (rare)

- Use `unsafe` only when it is necessary and justified.
- Document invariants and why they hold.
- Add tests that exercise the unsafe boundary.
