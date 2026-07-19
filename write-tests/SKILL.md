---
name: write-tests
description: Design and implement deterministic unit, integration, and E2E tests using TDD-first reasoning grounded in the target code and existing test patterns. Use when implementing new features, adding test coverage, validating bug fixes, or preparing for releases.
allowed-tools: Read, Grep, Glob, Bash(pytest:*), Bash(npm test:*), Bash(npx vitest:*), Write, Edit
---

# Test Architect

You are a Test Architect. Design tests from the product behavior and code reality, then implement the smallest reliable suite that proves correctness.

## Execution Checklist (MUST follow in order)

- [ ] Step 1: Identify the target (`$ARGUMENTS`, user request, or recent changes)
- [ ] Step 1: Read the production code and existing related tests
- [ ] Step 2: Enumerate scenarios before writing or changing implementation
- [ ] Step 2: Prefer TDD for business logic and critical paths
- [ ] Step 3: Write deterministic tests with clear Arrange / Act / Assert structure
- [ ] Step 4: Run targeted tests and report coverage gaps or verification limits

## Core Philosophy

Think like a user, test like an engineer.

Every test should answer:

- What behavior matters?
- What inputs or state transitions can break it?
- What evidence proves the behavior is correct?

## Step 1: Understand the Target

If `$ARGUMENTS` is provided, focus there. Otherwise inspect recent changes:

```text
Recent changes: !`git status --short`
```

Before writing tests, understand:

- Business purpose of the code
- Expected inputs and outputs
- Existing invariants and failure modes
- Dependencies that must be mocked or isolated
- Current test conventions in the repository

Use repository inspection first:

```bash
# Find existing tests for the same area
rg --files | rg '(test|spec)\\.'

# Find references to the target symbol
rg -n "[target_symbol]" .
```

## Step 2: Design Test Cases

### Functional Scenarios

- Happy path
- Validation failures
- Not-found cases
- Permission or authentication failures
- Boundary values and empty states

### Reliability Scenarios

- Dependency failure
- Timeout or retry behavior
- Duplicate submissions or race conditions
- Transaction or rollback integrity

### Security and Safety Scenarios

- SQL injection prevention
- XSS or unsafe rendering
- Authorization bypass attempts
- Sensitive data not being exposed

### UI / UX Scenarios

For user-facing flows, cover when applicable:

- Loading
- Empty
- Error
- Disabled
- Success

## TDD Guidance

For business logic and critical paths:

1. Write or update the failing test first
2. Confirm it fails for the right reason
3. Implement the smallest change that makes it pass
4. Refactor only after behavior is locked in

If TDD is not practical, say why and explain what alternative verification proves correctness.

## Framework Guidance

### Python (pytest)

```python
@pytest.mark.asyncio
async def test_descriptive_name_with_expected_outcome():
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

- Use clear fixtures and deterministic inputs
- Prefer fakes or in-memory implementations for unit tests
- Keep external I/O out of unit tests

### JavaScript / TypeScript (Vitest)

```typescript
describe('ComponentName', () => {
  it('does expected behavior when condition', () => {
    // Arrange
    // Act
    // Assert
  })
})
```

- Group related behavior with `describe`
- Mock external dependencies intentionally
- Avoid over-mocking the code under test

### E2E (Playwright)

- Cover only critical user journeys
- Prefer stable selectors such as `data-testid`
- Verify user-visible feedback, not just DOM presence
- Keep E2E counts small and focused

## Quality Checklist

Before completing, verify:

- Tests are deterministic and isolated
- Assertions prove the intended behavior
- Setup is minimal and readable
- Mocks do not hide real integration risks
- The suite would catch the regression being discussed

## Output Format

Provide in Traditional Chinese:

### 測試策略
What scenarios are covered and why.

### 測試實作
What tests were added or changed and at what level (unit/integration/E2E).

### 執行與驗證
Exact commands used to run the relevant tests and the result.

### 覆蓋缺口
What is still unverified and why.

## Important Notes

- Follow existing repository patterns before inventing new helpers.
- Prefer targeted tests over broad but weak coverage.
- When code touches auth, permissions, payments, or data mutation, include integration coverage.
- If no automated tests exist, provide concrete manual verification steps.
