# Output Template

Always answer in Traditional Chinese and start directly with the required headings.

## 版面摘要

Summarize:

- target surface
- affected viewport or breakpoint
- main layout failure

Keep this section to 2-4 sentences.

## 主要問題

List the highest-impact findings first. For each finding include:

1. surface or component
2. viewport or state
3. observable layout problem
4. user impact

Good examples:

- CTA is pushed below the fold on `390px` mobile when helper text wraps to two lines.
- Error banner overlaps the modal footer, hiding the primary action on short desktop heights.

## 修正 brief

For each finding, describe:

- the smallest layout-only fix
- responsive transformation if relevant
- content safety rules for long labels, helper text, tables, chips, or badges when relevant

Use implementation-facing language, but do not prescribe exact CSS unless requested.

## 驗收檢查

Write browser-testable checks:

- name at least one viewport
- name the interaction or state to verify
- state the expected visible outcome

Example pattern:

- At `390px` mobile, the primary CTA stays fully visible below the form even when the longest localized helper text wraps to two lines.

## 轉交建議

Use this section when downstream work is needed.

Typical contents:

- hand off to `uiux-design` for repo edits
- hand off to `uiux-design` for browser verification
- route back to `gemini-cli` if the issue is actually planning, not evidence-based review
