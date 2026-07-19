---
name: "source-command-collab-start"
description: "Start session collaboration for non-trivial or multi-session work (not pure Q&A)"
---

# source-command-collab-start

Use when the user asks to run `collab-start`, or when starting **non-trivial** edit work that may conflict with parallel sessions. **Skip** pure Q&A / chat.

## Command Template

Call `mcp__session-collab__collab_session_start` with:
- project_root: repo to edit
- name: stable descriptive session name (enables reuse)
- restore_context: false by default
- force_new: true only to skip reuse

Then prefer `collab_claim` action=create (batch files). check is optional. Memory = short highlights only (not AI-Memory vault).
