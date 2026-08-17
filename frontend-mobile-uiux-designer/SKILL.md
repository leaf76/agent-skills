---
name: frontend-mobile-uiux-designer
description: Design native iOS+Android product UX from brief to developer-ready UI specs. Use for mobile UX flows and IA, wireframes (prefer Pencil .pen), UI component/state specs, design tokens, and implementation notes for iOS/Android engineers.
---

## Routing
- Primary for native iOS/Android UX scope.
- For Web or responsive front-end tasks, route to `uiux-design`; if the work is still text-first, use `gemini-cli` first to produce the handoff.
- If upstream UX planning is part of the task, keep it inside the parent UX workflow and continue with platform-specific spec delivery.

# Frontend Mobile UI/UX Designer

## Goal

Turn a product brief into clear, engineer-ready UX and UI specs for **native iOS + Android**:

- Information architecture (IA) and user flows
- Wireframes (prefer Pencil `.pen` when available)
- UI specs (components, states, tokens) and implementation guidance for iOS/Android engineers

## Default outputs

If the user does not specify output locations, use:

- `docs/uiux/<YYYY-MM-DD>-mobile-uiux.md` (brief, IA, flows, specs, tokens, decisions)
- `designs/<YYYY-MM-DD>-mobile-wireframes.pen` (Pencil wireframes)

Use `references/deliverables.md` for templates and section checklists.

## Intake checklist (ask first)

Collect only what you need, then proceed with stated assumptions:

- Target users, primary jobs-to-be-done, success metrics
- Platform scope: iOS/Android versions, phones/tablets, orientation, offline needs
- Tech stack: SwiftUI vs UIKit, Jetpack Compose vs XML (or unknown)
- Existing design system/components, brand guidelines, typography, icon set
- Navigation model: tabs, stacks, deep links, authentication
- Data constraints: latency, pagination, empty/error states, caching
- Accessibility: dynamic type/font scaling, contrast, touch targets, VoiceOver/TalkBack
- Localization: languages, text expansion, RTL needs

## Workflow (recommended)

### 1) Define scope and assumptions

- Restate goals and **explicit non-goals**
- Define key screens (MVP) and critical paths (happy path + failure path)
- Record assumptions and open questions in the spec doc

### 2) Produce IA + user flows

- IA: sitemap / screen map (group by feature area)
- User flows: at least one per critical path (include errors, empty, loading)
- Prefer Mermaid diagrams for flows inside the Markdown spec

### 3) Create wireframes (prefer Pencil)

If Pencil tooling is available, produce a `.pen` file:

- One frame per screen, named consistently (e.g., `Auth / Sign In`, `Home`, `Detail`)
- Include key states: loading, empty, error, keyboard open, permission denied
- Add annotations for interactions and validation rules

If Pencil tooling is not available, produce wireframes in Markdown using:

- Screen lists + bullet layouts
- Simple ASCII blocks where needed

### 4) Write UI specs (components + states)

Deliver a component inventory that is reusable across iOS/Android:

- Component name, purpose, variants, and states
- Interaction rules (tap, long-press, swipe), animations (if any)
- Content rules (truncation, line limits), error messaging, input validation
- Accessibility rules (labels, focus order, minimum touch size)

### 5) Define design tokens (developer-ready)

Define a small, stable token set with naming and usage rules:

- Colors (semantic first), typography, spacing, radius, elevation/shadows
- State tokens (disabled/pressed/focused/error)

Use `references/token-spec.md` for a suggested token schema and handoff notes.

### 6) Handoff notes for iOS and Android

Provide implementation guidance, not full app code, unless requested:

- iOS: recommended layout approach (SwiftUI/UIKit), safe area, dynamic type
- Android: recommended layout approach (Compose/XML), window insets, font scaling
- Navigation: deep links, back behavior, modal vs push patterns
- Performance: list virtualization, image loading, skeleton/loading patterns

## Quality bar

- Cover at least: happy path, error states, empty states, loading states
- Do not leak technical details in user-facing copy; keep messages actionable
- Keep specs consistent: naming, spacing scale, and component variants

## References

- `references/deliverables.md`: output templates and acceptance checklist
- `references/token-spec.md`: token naming + schema + platform mapping notes

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
