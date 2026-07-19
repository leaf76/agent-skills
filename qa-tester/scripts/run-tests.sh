#!/bin/bash
# Run tests with coverage
set -e

echo "🧪 Running Tests"
echo "================"
echo ""

run_python_tests() {
    echo "🐍 Python Tests"
    
    if [ -f "pyproject.toml" ] || [ -f "pytest.ini" ]; then
        pytest -v --cov=. --cov-report=term-missing --cov-report=html "$@"
    elif [ -f "setup.py" ]; then
        python -m pytest -v --cov=. "$@"
    else
        python -m unittest discover -v
    fi
}

run_node_tests() {
    echo "📘 Node.js Tests"
    
    if grep -q "vitest" package.json 2>/dev/null; then
        npx vitest run --coverage "$@"
    elif grep -q "jest" package.json 2>/dev/null; then
        npx jest --coverage "$@"
    elif grep -q "mocha" package.json 2>/dev/null; then
        npx mocha "$@"
    else
        npm test "$@"
    fi
}

run_go_tests() {
    echo "🔵 Go Tests"
    go test -v -cover -race ./... "$@"
}

run_rust_tests() {
    echo "🦀 Rust Tests"
    cargo test --all-features "$@"
}

# Detect project type and run tests
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "pytest.ini" ]; then
    run_python_tests "$@"
elif [ -f "package.json" ]; then
    run_node_tests "$@"
elif [ -f "go.mod" ]; then
    run_go_tests "$@"
elif [ -f "Cargo.toml" ]; then
    run_rust_tests "$@"
else
    echo "❌ Unknown project type"
    exit 1
fi

echo ""
echo "✅ Tests completed"
