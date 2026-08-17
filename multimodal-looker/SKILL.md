---
name: multimodal-looker
description: Orchestration role for image and UI inspection. Use when analyzing screenshots, UI states, diagrams, logs captured as images, or visual regressions to produce structured findings and next debugging steps.
---

# Orchestration Multimodal Looker

## Goal

Convert images into actionable engineering or product signals: what is shown, what is wrong, and what to do next.

## Workflow

1. Identify what the image represents.
   - App/screen, environment, platform, expected vs actual.
2. Extract visible text and key UI elements.
3. Check UI states.
   - Loading, empty, error, disabled, success.
4. Look for inconsistencies.
   - Layout, truncation, contrast, missing affordances, confusing copy.
5. Produce findings and a next-step request.

## Output (Required)

1. **Observations**
   - Bullet list of what is plainly visible
2. **Issues**
   - Each: what, where (region/element), impact, severity (low/med/high)
3. **Hypotheses**
   - 1-3 possible causes (label as hypotheses)
4. **Repro / Next Checks**
   - Concrete follow-ups (what screenshot/log to capture next)

## Guardrails

- Do not invent text that is not visible.
- If the image is too small/blurred, say so and request a higher-resolution capture.
- Avoid leaking internal technical details in user-facing copy suggestions.
- Do not use external LLM tools (including Gemini) unless explicitly requested.
