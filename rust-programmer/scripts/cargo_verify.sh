#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: cargo_verify.sh [options]

Run a standard Rust verification loop for the current Cargo project.

Options:
  --all-features     Enable all Cargo features for clippy/test
  --workspace        Use --workspace for clippy/test (safe for workspaces)
  --no-fmt           Skip cargo fmt check
  --no-clippy        Skip cargo clippy
  --no-test          Skip cargo test
  -h, --help         Show this help
EOF
}

all_features=false
workspace=false
run_fmt=true
run_clippy=true
run_test=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all-features)
      all_features=true
      shift
      ;;
    --workspace)
      workspace=true
      shift
      ;;
    --no-fmt)
      run_fmt=false
      shift
      ;;
    --no-clippy)
      run_clippy=false
      shift
      ;;
    --no-test)
      run_test=false
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if $run_fmt; then
  echo "[verify] cargo fmt (check)"
  cargo fmt --all -- --check
fi

clippy_args=(clippy --all-targets)
test_args=(test)

if $workspace; then
  clippy_args+=(--workspace)
  test_args+=(--workspace)
fi

if $all_features; then
  clippy_args+=(--all-features)
  test_args+=(--all-features)
fi

if $run_clippy; then
  echo "[verify] cargo clippy"
  cargo "${clippy_args[@]}" -- -D warnings
fi

if $run_test; then
  echo "[verify] cargo test"
  cargo "${test_args[@]}"
fi
