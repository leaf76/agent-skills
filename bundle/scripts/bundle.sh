#!/bin/bash
# Bundle project for distribution
set -e

PROJECT_NAME=$(basename "$PWD")
VERSION=$(git describe --tags --always 2>/dev/null || echo "0.0.1")

bundle_frontend() {
    echo "🌐 Bundling frontend app..."
    if [ -f "vite.config.ts" ] || [ -f "vite.config.js" ]; then
        npm run build
    elif [ -f "webpack.config.js" ]; then
        npm run build
    fi
    echo "📁 Output: dist/"
}

bundle_npm() {
    echo "📦 Bundling npm package..."
    npm run build 2>/dev/null || true
    npm pack
    echo "📁 Output: ${PROJECT_NAME}-${VERSION}.tgz"
}

bundle_python() {
    echo "🐍 Bundling Python package..."
    if [ -f "pyproject.toml" ]; then
        python -m build
    else
        python setup.py sdist bdist_wheel
    fi
    echo "📁 Output: dist/*.whl"
}

bundle_go() {
    echo "🔵 Building Go binary..."
    CGO_ENABLED=0 go build -ldflags="-s -w" -o "dist/${PROJECT_NAME}" ./...
    echo "📁 Output: dist/${PROJECT_NAME}"
}

bundle_rust() {
    echo "🦀 Building Rust binary..."
    cargo build --release
    cp "target/release/${PROJECT_NAME}" "dist/" 2>/dev/null || true
    echo "📁 Output: dist/${PROJECT_NAME}"
}

bundle_extension() {
    echo "🧩 Bundling web extension..."
    mkdir -p dist
    zip -r "dist/${PROJECT_NAME}-${VERSION}.zip" . \
        -x "*.git*" -x "node_modules/*" -x "dist/*" -x "*.md"
    echo "📁 Output: dist/${PROJECT_NAME}-${VERSION}.zip"
}

# Auto-detect and bundle
mkdir -p dist

if [ -f "manifest.json" ]; then
    bundle_extension
elif [ -f "vite.config.ts" ] || [ -f "vite.config.js" ] || [ -f "webpack.config.js" ]; then
    bundle_frontend
elif [ -f "package.json" ] && grep -q '"main"' package.json; then
    bundle_npm
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ]; then
    bundle_python
elif [ -f "go.mod" ]; then
    bundle_go
elif [ -f "Cargo.toml" ]; then
    bundle_rust
else
    echo "❌ Unknown project type"
    exit 1
fi

echo "✅ Bundle completed"
