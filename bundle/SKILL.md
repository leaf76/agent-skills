---
name: bundle
description: Bundle and package projects for distribution. Supports frontend apps (Vite/Webpack), libraries (npm/PyPI), executables (Go/Rust binaries), and web extensions (Chrome/Firefox). Use when preparing releases, packaging for distribution, or creating deployable artifacts.
allowed-tools: Read, Grep, Glob, Bash
---

# Bundle Project

Package projects for distribution across different formats.

## Bundle Type Detection

| Indicator | Bundle Type | Output |
|-----------|-------------|--------|
| `vite.config.*` / `webpack.config.*` | Frontend App | `dist/` static files |
| `package.json` with `main`/`exports` | npm Library | `dist/` + `package.json` |
| `pyproject.toml` with `[build-system]` | PyPI Library | `dist/*.whl` |
| `go.mod` with `main` package | Go Binary | Single executable |
| `Cargo.toml` with `[[bin]]` | Rust Binary | Single executable |
| `manifest.json` (v3) | Web Extension | `.zip` for store upload |

## Frontend App Bundle

### Vite

```bash
# Production build
pnpm build  # or npm run build

# Preview locally
pnpm preview
```

**Output:** `dist/` with optimized static files

### Webpack

```bash
# Production build
NODE_ENV=production npx webpack

# Analyze bundle size
npx webpack-bundle-analyzer dist/stats.json
```

### Optimization Checklist

- [ ] Tree shaking enabled
- [ ] Code splitting configured
- [ ] Assets minified (JS/CSS/images)
- [ ] Source maps for production (hidden)
- [ ] Gzip/Brotli compression ready

## Library Bundle

### npm Package

```bash
# Build library
pnpm build

# Check package contents before publish
npm pack --dry-run

# Verify exports
node -e "console.log(require('./dist'))"
```

**package.json requirements:**
```json
{
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  },
  "files": ["dist"]
}
```

### PyPI Package

```bash
# Build with poetry
poetry build

# Build with uv
uv build

# Check package
twine check dist/*
```

**Output:** `dist/package-version.whl` and `dist/package-version.tar.gz`

## Executable Bundle

### Go Binary

```bash
# Build for current platform
go build -ldflags="-s -w" -o bin/app ./cmd/app

# Cross-compile all platforms
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o bin/app-linux-amd64 ./cmd/app
GOOS=darwin GOARCH=arm64 go build -ldflags="-s -w" -o bin/app-darwin-arm64 ./cmd/app
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o bin/app-windows-amd64.exe ./cmd/app
```

**Optimization flags:**
- `-s` - Strip symbol table
- `-w` - Strip DWARF debug info
- `-trimpath` - Remove file paths from binary

### Rust Binary

```bash
# Release build
cargo build --release

# Optimized for size
RUSTFLAGS="-C opt-level=s" cargo build --release

# Strip symbols (Linux/macOS)
strip target/release/app
```

**Cargo.toml optimizations:**
```toml
[profile.release]
lto = true
codegen-units = 1
panic = "abort"
strip = true
```

## Web Extension Bundle

### Chrome Extension (Manifest V3)

```bash
# Build extension
pnpm build

# Create zip for Chrome Web Store
cd dist && zip -r ../extension-chrome.zip . -x "*.map"
```

### Firefox Extension

```bash
# Build with web-ext
npx web-ext build --source-dir=dist --artifacts-dir=artifacts

# Or manual zip
cd dist && zip -r ../extension-firefox.zip . -x "*.map"
```

### Extension Checklist

- [ ] `manifest.json` version updated
- [ ] Icons included (16, 48, 128px)
- [ ] Permissions minimized
- [ ] Content Security Policy set
- [ ] No dynamic code execution (prohibited by CSP)
- [ ] Source maps excluded from zip

## Bundle Verification

After bundling, verify:

```bash
# Check bundle size
du -sh dist/

# List contents
ls -la dist/

# For zip files
unzip -l extension.zip
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Bundle too large | No tree shaking | Check imports, use named exports |
| Missing assets | Wrong public path | Fix `base` in vite.config |
| Runtime errors | Missing polyfills | Add core-js or specific polyfills |
| Extension rejected | CSP violation | Remove dynamic code execution |

## Output

Report bundle results:
1. Bundle type and output location
2. Total size (before/after compression)
3. Files included
4. Any warnings or optimization suggestions
