---
name: gemini-cli
description: Use when a task benefits from local Gemini CLI for text-first analysis, summarization, critique, drafting, rewriting, translation, or structured planning artifacts, especially when the user asks for Gemini CLI directly or wants a second-pass large-context review without changing project files.
---

# Gemini CLI

## Overview

Use local Gemini CLI as a bounded helper for text-first reasoning and artifact generation. Treat Gemini output as a draft or second opinion that must be reviewed before it drives code, product, deployment, or security decisions.

## When to Use

- The user explicitly asks to use Gemini CLI.
- A text brief, notes file, log excerpt, design brief, or document needs summarization, critique, rewrite, translation, or structured Markdown output.
- A large text context needs a second-pass review before implementation planning.
- Existing specialized skills do not fit the request.

Use this skill as the only Gemini CLI entrypoint. Keep specialized needs explicit in the prompt, and do not use Gemini CLI to handle secrets, production credentials, private tokens, or raw sensitive data.

## Safety Rules

- Keep secrets, credentials, tokens, cookies, private keys, and production-only configuration out of prompts and saved prompt files.
- Prefer focused excerpts over whole repositories or broad log dumps.
- Do not let Gemini output directly edit files. Review the output, then apply changes yourself using the normal repository workflow.
- For security, auth, data mutation, deploy, or database work, treat Gemini output as advisory only and verify against source code, tests, docs, and runtime evidence.
- Do not paste untrusted external input into shell commands. Put prompt text in a file when it includes quotes, code blocks, logs, or user-provided content.
- Keep retries bounded. A Gemini failure is not a reason to weaken validation or skip verification.

## Quick Start

Write the prompt to a file first:

```bash
cat > prompt.md <<'EOF'
Summarize the following notes into:
- key decisions
- open questions
- implementation risks
- next actions

<paste focused text here>
EOF
```

Run Gemini CLI in non-interactive mode:

```bash
gemini -p "Follow the instructions from stdin." < prompt.md
```

Save output only when it is useful as an artifact:

```bash
gemini -p "Follow the instructions from stdin." < prompt.md > gemini-output.md
```

## Workflow

### 1. Define the task

State the desired output shape before running Gemini:

- summary
- critique
- rewrite
- translation
- comparison
- implementation plan
- risk list
- test matrix
- Markdown document

Include constraints, non-goals, audience, language, and exact terms that must remain unchanged.

### 2. Prepare input

- Use one focused prompt file.
- Add only high-signal context.
- Remove secrets and environment-specific values.
- Replace sensitive identifiers with stable placeholders when needed.
- Keep exact file paths or code references only when they are necessary for review.

### 3. Run Gemini

Prefer a command that is easy to rerun:

```bash
gemini -p "Follow the instructions from stdin." < prompt.md
```

For commands that need model selection, keep the model explicit and document why:

```bash
gemini --model "<model-name>" -p "Follow the instructions from stdin." < prompt.md
```

If the task requires a saved artifact:

```bash
gemini -p "Follow the instructions from stdin." < prompt.md > docs/gemini-draft.md
```

### 4. Review output

Before acting on Gemini output, check:

- assumptions are explicit
- no secrets or private data are echoed
- claims match project files or cited sources
- recommendations fit the requested scope
- risks, open questions, and verification steps are concrete
- user-facing copy follows the requested language and tone

### 5. Apply or discard

Use Gemini output as source material, not as an authority. Apply only the parts that survive local review, project constraints, and normal verification.

## Prompt Pattern

```text
Task:
<one sentence goal>

Output format:
<exact sections, bullets, table, or Markdown structure>

Constraints:
- <must keep>
- <must avoid>
- <language and tone>
- <non-goals>

Context:
<focused source text>

Review requirements:
- List assumptions.
- List uncertainty separately from conclusions.
- Do not invent facts that are not present in the context.
```

## Verification

- For documentation-only output, review the generated file for accuracy, scope, and formatting.
- For code-affecting output, verify with source inspection and the project test/check commands.
- For UI-affecting output, verify with the appropriate browser or layout-review workflow.
- For deploy, auth, security, database, or payment decisions, verify with primary project evidence and do not rely on Gemini alone.

## Common Mistakes

- Sending too much context and getting generic output.
- Treating Gemini's draft as verified truth.
- Saving prompts that contain secrets or private production data.
- Using Gemini CLI for a specialized workflow that already has a narrower skill.
- Skipping local tests because Gemini's explanation sounds plausible.
