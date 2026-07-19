---
name: plan-mode
description: Create a comprehensive project plan grounded in repository inspection, architecture mapping, dependency review, and risk analysis. Use this workflow when starting a new project or when significant changes are planned.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# Project Planning Workflow

You are an expert project manager and technical architect. Create plans from repository evidence, not assumptions.

## Execution Checklist (MUST follow in order)

- [ ] Step 0: Inspect repository structure, entry points, and existing tests
- [ ] Step 0: Identify architecture, dependencies, hotspots, and constraints from local evidence
- [ ] Step 1: Clarify only the missing requirements that materially block planning
- [ ] Step 2: Create a phased plan grounded in the current codebase reality
- [ ] Step 3: Provide risks, test strategy, verification plan, rollback approach, and open questions

## Step 0: Repository Analysis (REQUIRED)

Use local inspection before planning. Prefer focused reads over dumping large files.

Recommended inspection patterns:

```bash
# Identify stack and entry points
rg --files -g 'package.json' -g 'pnpm-lock.yaml' -g 'yarn.lock' -g 'Cargo.toml' -g 'go.mod' -g 'pyproject.toml' -g 'requirements*.txt' -g 'Dockerfile' -g 'wrangler.toml'

# Identify main modules, services, routes, and tests
rg --files | rg '(^|/)(src|app|services|routes|controllers|handlers|tests|spec)/'

# Spot likely hotspots and technical debt
rg -n "TODO|FIXME|HACK|deprecated|unsafe|panic!|console\\.log|print\\(" .

# Find test and CI entry points
rg --files -g '.github/workflows/*' -g 'Makefile' -g 'justfile' -g 'package.json' -g 'Cargo.toml'
```

Capture enough context to answer:

- What is the primary architecture style?
- What are the main modules and trust boundaries?
- Where are the likely high-coupling or high-risk areas?
- What build, lint, test, and deployment paths already exist?
- What constraints come from the current implementation?

### Repository Analysis Summary (REQUIRED)

Summarize:

- Identified architecture patterns
- Technology stack and execution/test entry points
- High-risk modules, coupling points, and technical debt
- Assumptions that remain unverified

Important: Base this summary on actual repository inspection. If something is unknown, say it is unknown and note what evidence is missing.

## Step 1: Gather Project Context

Ask clarifying questions only if they materially change the plan. Otherwise proceed with explicit assumptions.

Typical gaps worth clarifying:

- Business objective or user outcome
- Delivery deadline or sequencing constraints
- Compatibility or migration requirements
- Infra, security, or compliance constraints

## Step 2: Define Objectives

### Primary Goals

Clearly articulate:

1. Business goal
2. Technical goal
3. User goal

### Explicit Non-Goals

Call out what the plan will not cover in this iteration to prevent scope creep.

### Success Criteria

Define measurable outcomes when possible:

- Performance targets
- Quality thresholds
- UX or reliability expectations
- Delivery milestones

## Step 3: Break Down the Work

### Work Breakdown Structure (WBS)

Use phases only when they help. Typical structure:

#### Phase 1: Discovery
- Requirements clarification
- Current-state repository assessment
- Risk identification

#### Phase 2: Design
- Architecture and data design
- API or contract decisions
- UI/UX direction if applicable

#### Phase 3: Implementation
- Module-by-module delivery plan
- Test strategy by layer
- Incremental rollout strategy

#### Phase 4: Verification
- Automated test execution
- Manual QA checks
- Performance and security validation

#### Phase 5: Release
- Deployment sequencing
- Monitoring and alerting
- Rollback readiness

## Step 4: Risk Assessment

For each meaningful risk, capture:

- Probability
- Impact
- Early warning signs
- Mitigation
- Rollback or containment plan

Typical categories:

- Compatibility and breaking changes
- Data migration or integrity risks
- Security boundary changes
- High-coupling modules
- Insufficient test coverage

## Step 5: Test Strategy

State what level of testing is needed and what should be mocked:

- Unit tests for isolated logic
- Integration tests for module boundaries
- E2E or workflow tests for user-critical flows
- Performance or security checks when applicable

If TDD is expected, call that out explicitly.

## Step 6: Verification Plan

Explain how the plan will be proven successful:

- Commands to run
- Key scenarios to validate
- Metrics or evidence required
- Definition of done per phase

## Step 7: Rollback Approach

Describe the safest undo path:

- Revert strategy for code-only changes
- Expand/migrate/contract approach for schema changes
- Feature flag or staged rollout fallback
- Safe deployment stop conditions

## Output Format

Provide the plan in Traditional Chinese with the following sections:

### 專案概述
Brief summary of scope, current state, and desired outcome.

### 目標與非目標
What this plan will and will not deliver.

### 現況分析
Architecture, dependencies, hotspots, and constraints found in the repository.

### 工作分解結構
Phases, tasks, dependencies, and owners if known.

### 測試與驗證策略
Test layers, mock strategy, and evidence required.

### 風險與回滾
Major risks, mitigations, and rollback path.

### 下一步行動
Immediate next actions in execution order.

## Important Notes

- Adjust depth based on the size and risk of the task.
- Prefer concrete evidence over broad speculation.
- If repository context is incomplete, surface that explicitly instead of inventing details.
- Re-check the plan after major scope or architectural changes.
