# Security Audit Checklist

## Input Validation

### SQL Injection
- [ ] Use parameterized queries / prepared statements
- [ ] Never concatenate user input into SQL
- [ ] Use ORM properly (avoid raw queries)

```python
# ❌ Bad
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ Good
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### XSS (Cross-Site Scripting)
- [ ] Escape HTML output
- [ ] Use Content Security Policy headers
- [ ] Sanitize user-generated content
- [ ] Use HttpOnly cookies

```python
# ❌ Bad
return f"<div>{user_input}</div>"

# ✅ Good
from markupsafe import escape
return f"<div>{escape(user_input)}</div>"
```

### Command Injection
- [ ] Avoid shell=True in subprocess
- [ ] Use shlex.quote() for shell arguments
- [ ] Validate file paths

```python
# ❌ Bad
os.system(f"convert {user_file}")

# ✅ Good
subprocess.run(["convert", user_file], check=True)
```

## Authentication

- [ ] Use strong password hashing (bcrypt, argon2)
- [ ] Implement rate limiting
- [ ] Use secure session management
- [ ] Implement MFA where appropriate
- [ ] Secure password reset flow

```python
# ✅ Password hashing
from passlib.hash import bcrypt
hashed = bcrypt.hash(password)
bcrypt.verify(password, hashed)
```

## Authorization

- [ ] Implement proper access control
- [ ] Check ownership before allowing access
- [ ] Use role-based access control (RBAC)
- [ ] Validate permissions server-side

```python
# ✅ Ownership check
if resource.owner_id != current_user.id:
    raise PermissionError("Access denied")
```

## Sensitive Data

### In Code
- [ ] No hardcoded secrets
- [ ] Use environment variables
- [ ] No secrets in version control

### In Logs
- [ ] Don't log passwords
- [ ] Don't log tokens/API keys
- [ ] Don't log PII unnecessarily
- [ ] Mask sensitive data

```python
# ❌ Bad
logger.info(f"User login: {email}, password: {password}")

# ✅ Good
logger.info(f"User login: {email}")
```

### In Transit
- [ ] Use HTTPS everywhere
- [ ] Validate SSL certificates
- [ ] Use TLS 1.2+

### At Rest
- [ ] Encrypt sensitive data
- [ ] Use proper key management
- [ ] Secure database credentials

## HTTP Security Headers

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## API Security

- [ ] Use API authentication (OAuth2, JWT)
- [ ] Implement rate limiting
- [ ] Validate Content-Type
- [ ] Return minimal error information
- [ ] Use HTTPS only

## File Upload

- [ ] Validate file type (magic bytes, not extension)
- [ ] Limit file size
- [ ] Generate random filenames
- [ ] Store outside webroot
- [ ] Scan for malware

## Dependencies

- [ ] Keep dependencies updated
- [ ] Run `npm audit` / `pip-audit`
- [ ] Use lockfiles
- [ ] Review transitive dependencies

## Common Vulnerabilities (OWASP Top 10)

1. Broken Access Control
2. Cryptographic Failures
3. Injection
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable Components
7. Authentication Failures
8. Data Integrity Failures
9. Logging Failures
10. SSRF
