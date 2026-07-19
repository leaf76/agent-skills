# Issue Checklist

Use this checklist to classify layout problems before writing recommendations.

## 1. Spacing rhythm

Inspect:

- inconsistent gaps between siblings
- uneven section padding
- card, form, or table density that breaks scan rhythm
- helper text or error text crowding inputs

Recommend fixes in terms of:

- normalize gap or padding scale
- preserve current hierarchy while tightening or loosening only the affected area

## 2. Alignment and centering

Inspect:

- misaligned labels, inputs, buttons, icons, or column content
- accidental off-center headers, modals, or empty states
- mixed baseline alignment inside cards or list rows

Recommend fixes in terms of:

- align to a consistent column or baseline
- keep related controls on the same visual axis

## 3. Overflow and wrapping

Inspect:

- text clipping, truncation, or wrapping that hides meaning
- CTA, badge, or metadata overflow inside cards and rows
- horizontal scroll caused by long strings, tables, or toolbars

Recommend fixes in terms of:

- define wrapping or truncation behavior explicitly
- protect primary actions and key content from being pushed out of view

## 4. Responsive transformation failure

Inspect:

- grid not collapsing at the intended breakpoint
- two-column layouts remaining too dense on tablet or mobile
- toolbar, filters, or navigation failing to collapse cleanly

Recommend fixes in terms of:

- name the affected viewport range
- describe the required transformation, such as `2-col -> 1-col` or `table -> cards/summary`

## 5. Sticky, modal, drawer, and overlay collision

Inspect:

- sticky header or footer covering form fields or CTAs
- modal content extending below the viewport
- drawer or bottom sheet blocking primary content or safe areas

Recommend fixes in terms of:

- maintain visibility of primary actions
- preserve readable scroll and safe-area behavior

## 6. Form layout instability

Inspect:

- label, input, helper text, and error message misalignment
- validation state changes that shift unrelated controls
- keyboard-open states that hide active fields or actions

Recommend fixes in terms of:

- keep form rows visually stable across default, error, disabled, and success states

## 7. Data-heavy layouts

Inspect:

- cards with uneven heights that break reading order
- tables that overflow without a mobile transformation
- filter bars, chips, and actions that wrap unpredictably

Recommend fixes in terms of:

- maintain readable hierarchy
- define mobile fallback behavior instead of allowing accidental overflow

## Acceptance-check reminders

Always name:

- affected surface
- viewport or breakpoint
- state, such as default, loading, error, empty, or keyboard-open
- exact behavior that should no longer fail
