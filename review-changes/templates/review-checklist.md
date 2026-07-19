# Code Review Checklist

## General

- [ ] Code is readable and self-documenting
- [ ] Variable/function names are descriptive
- [ ] No commented-out code
- [ ] No debug statements (console.log, print)
- [ ] Error handling is appropriate
- [ ] No hardcoded values (use constants/config)

## Logic

- [ ] Business logic is correct
- [ ] Edge cases are handled
- [ ] No off-by-one errors
- [ ] Null/undefined checks where needed
- [ ] Race conditions considered

## Performance

- [ ] No N+1 queries
- [ ] Appropriate caching
- [ ] No unnecessary loops
- [ ] Large data sets paginated
- [ ] Async operations handled properly

## Security

- [ ] Input validation present
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] Sensitive data not logged
- [ ] Authentication/authorization correct

## Testing

- [ ] Unit tests added/updated
- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests cover error cases
- [ ] All tests pass

## Documentation

- [ ] Public APIs documented
- [ ] Complex logic has comments
- [ ] README updated if needed
- [ ] CHANGELOG updated if needed

## Style

- [ ] Follows project conventions
- [ ] Linting passes
- [ ] Formatting consistent
- [ ] No unnecessary whitespace changes

## Dependencies

- [ ] New dependencies justified
- [ ] Dependencies are up to date
- [ ] No security vulnerabilities
- [ ] License is compatible

## Review Response Format

```
## Summary
[Brief description of changes]

## What's Good
- 

## Suggestions
- [ ] File:line - Issue description

## Questions
- 

## Verdict
[ ] ✅ Approved
[ ] ⚠️ Approved with suggestions
[ ] ❌ Changes requested
```
