# Testing Checklist

Use this checklist after UI implementation is complete.

## Start with `agent-browser`

- Use `agent-browser` first when the task needs real interaction flows, snapshots, screenshots, or end-to-end validation of the implemented UI.
- Re-snapshot after major UI state changes if you are using element refs.
- Capture the desktop and mobile evidence that the task actually needs before escalating.

## Fall back to Chrome DevTools when needed

- Switch to Chrome DevTools when `agent-browser` is unavailable in the environment.
- Switch to Chrome DevTools when `agent-browser` cannot provide the console, network, performance, or DOM-level evidence needed for the task.
- In the fallback path, verify the target page on one desktop viewport and one mobile viewport.
- Capture at least one screenshot per viewport when the task is visual.
- Check console messages for errors and warnings relevant to the change.
- Check network requests for failing API calls, missing assets, or broken form submissions.

## Required UI checks

- visual hierarchy, spacing, alignment, and centering
- responsive wrapping and overflow for long text and dynamic content
- loading, empty, error, disabled, and success states when relevant
- focus visibility, focus order, and keyboard navigation on desktop
- touch-target sizing and blocked content risks on mobile
- sticky, fixed, modal, and overlay behavior when present

## Escalate to Playwright when any of these are true

- the change affects a core user journey
- the change modifies form submission or validation
- the change modifies modal, menu, tab, drawer, or step-flow behavior
- the change is likely to regress across breakpoints

## Reporting checklist

- browser tool path used (`agent-browser`, Chrome DevTools fallback, optional Playwright)
- tested desktop viewport and mobile viewport
- screenshots captured
- console findings summarized
- network findings summarized
- states covered and missing states called out
- residual risks and follow-up checks listed
