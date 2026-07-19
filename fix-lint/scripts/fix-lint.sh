#!/bin/bash
# Auto-fix linting errors
set -e

echo "🔍 Detecting project type and running linters..."
echo ""

fix_python() {
    echo "🐍 Fixing Python code..."
    
    # Ruff (fastest, preferred)
    if command -v ruff &> /dev/null; then
        echo "  Running ruff format..."
        ruff format . 2>/dev/null || true
        echo "  Running ruff check --fix..."
        ruff check --fix . 2>/dev/null || true
    fi
    
    # Black (formatting)
    if command -v black &> /dev/null && ! command -v ruff &> /dev/null; then
        echo "  Running black..."
        black . 2>/dev/null || true
    fi
    
    # isort (imports)
    if command -v isort &> /dev/null; then
        echo "  Running isort..."
        isort . 2>/dev/null || true
    fi
    
    echo "  ✓ Python linting complete"
}

fix_typescript() {
    echo "📘 Fixing TypeScript/JavaScript code..."
    
    # ESLint
    if [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f "eslint.config.js" ]; then
        echo "  Running eslint --fix..."
        npx eslint --fix . 2>/dev/null || true
    fi
    
    # Prettier
    if [ -f ".prettierrc" ] || [ -f ".prettierrc.json" ] || [ -f "prettier.config.js" ]; then
        echo "  Running prettier..."
        npx prettier --write . 2>/dev/null || true
    fi
    
    # TypeScript check
    if [ -f "tsconfig.json" ]; then
        echo "  Running tsc..."
        npx tsc --noEmit 2>/dev/null || true
    fi
    
    echo "  ✓ TypeScript/JavaScript linting complete"
}

fix_go() {
    echo "🔵 Fixing Go code..."
    
    echo "  Running gofmt..."
    gofmt -w . 2>/dev/null || true
    
    echo "  Running go vet..."
    go vet ./... 2>/dev/null || true
    
    if command -v golangci-lint &> /dev/null; then
        echo "  Running golangci-lint..."
        golangci-lint run --fix 2>/dev/null || true
    fi
    
    echo "  ✓ Go linting complete"
}

fix_rust() {
    echo "🦀 Fixing Rust code..."
    
    echo "  Running cargo fmt..."
    cargo fmt 2>/dev/null || true
    
    echo "  Running cargo clippy --fix..."
    cargo clippy --fix --allow-dirty 2>/dev/null || true
    
    echo "  ✓ Rust linting complete"
}

# Detect and fix
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
    fix_python
fi

if [ -f "package.json" ]; then
    fix_typescript
fi

if [ -f "go.mod" ]; then
    fix_go
fi

if [ -f "Cargo.toml" ]; then
    fix_rust
fi

echo ""
echo "✅ All linting fixes applied"
