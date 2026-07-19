#!/bin/bash
# Security audit helper
set -e

echo "🔒 Security Audit"
echo "================="
echo ""

# Check for secrets in code
check_secrets() {
    echo "🔑 Checking for hardcoded secrets..."
    
    # Common secret patterns
    PATTERNS=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api_key\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
        "AWS_ACCESS_KEY"
        "PRIVATE.KEY"
        "-----BEGIN RSA PRIVATE KEY-----"
        "-----BEGIN OPENSSH PRIVATE KEY-----"
    )
    
    for pattern in "${PATTERNS[@]}"; do
        echo "  Checking: $pattern"
        grep -rn --include="*.py" --include="*.js" --include="*.ts" --include="*.env" \
            -E "$pattern" . 2>/dev/null | grep -v node_modules | grep -v ".git" || true
    done
    
    echo "  ✓ Secret check complete"
}

# Check dependencies for vulnerabilities
check_dependencies() {
    echo ""
    echo "📦 Checking dependencies for vulnerabilities..."
    
    if [ -f "package.json" ]; then
        echo "  Running npm audit..."
        npm audit --audit-level=moderate 2>/dev/null || true
    fi
    
    if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
        echo "  Running pip-audit..."
        pip-audit 2>/dev/null || pip install pip-audit && pip-audit 2>/dev/null || true
    fi
    
    echo "  ✓ Dependency check complete"
}

# Check for SQL injection patterns
check_sql_injection() {
    echo ""
    echo "💉 Checking for potential SQL injection..."
    
    # f-string SQL patterns
    grep -rn --include="*.py" \
        -E "(execute|query|raw)\s*\(\s*f['\"]" . 2>/dev/null | grep -v ".git" || true
    
    # String concatenation in SQL
    grep -rn --include="*.py" \
        -E "execute\s*\(['\"].*\+.*['\"]" . 2>/dev/null | grep -v ".git" || true
    
    echo "  ✓ SQL injection check complete"
}

# Check for XSS patterns
check_xss() {
    echo ""
    echo "🌐 Checking for potential XSS..."
    
    # dangerouslySetInnerHTML
    grep -rn --include="*.tsx" --include="*.jsx" \
        "dangerouslySetInnerHTML" . 2>/dev/null | grep -v node_modules || true
    
    # innerHTML
    grep -rn --include="*.js" --include="*.ts" \
        "innerHTML\s*=" . 2>/dev/null | grep -v node_modules || true
    
    # Python format in templates
    grep -rn --include="*.html" \
        -E "\{\{.*\|safe\}\}" . 2>/dev/null || true
    
    echo "  ✓ XSS check complete"
}

# Check file permissions
check_permissions() {
    echo ""
    echo "📁 Checking file permissions..."
    
    # World-writable files
    find . -type f -perm -002 -not -path "./.git/*" 2>/dev/null | head -20 || true
    
    # Executable scripts
    find . -type f -name "*.sh" -not -perm -100 -not -path "./.git/*" 2>/dev/null | head -20 || true
    
    echo "  ✓ Permission check complete"
}

# Run all checks
check_secrets
check_dependencies
check_sql_injection
check_xss
check_permissions

echo ""
echo "✅ Security audit complete"
echo ""
echo "Note: This is an automated scan. Manual review is still recommended."
