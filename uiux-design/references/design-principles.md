# UI/UX Design Reference

## Visual Hierarchy

### Typography Scale (Major Third - 1.25)
```
12px - Caption, labels
14px - Body small
16px - Body (base)
20px - H4
25px - H3
31px - H2
39px - H1
```

### Spacing Scale (4px base)
```
4px   - xs  (tight)
8px   - sm  (compact)
16px  - md  (default)
24px  - lg  (relaxed)
32px  - xl  (spacious)
48px  - 2xl (section)
64px  - 3xl (page section)
```

## Color Guidelines

### Semantic Colors
| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary | #2563EB | #3B82F6 |
| Success | #16A34A | #22C55E |
| Warning | #CA8A04 | #EAB308 |
| Error | #DC2626 | #EF4444 |
| Info | #0891B2 | #06B6D4 |

### Contrast Ratios (WCAG)
- Normal text: 4.5:1 minimum
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum

### Neutral Palette
```
50:  #FAFAFA
100: #F4F4F5
200: #E4E4E7
300: #D4D4D8
400: #A1A1AA
500: #71717A
600: #52525B
700: #3F3F46
800: #27272A
900: #18181B
950: #09090B
```

## Component Patterns

### Buttons
| Type | Use Case |
|------|----------|
| Primary | Main action (1 per view) |
| Secondary | Alternative actions |
| Tertiary | Low-emphasis actions |
| Destructive | Delete, remove |
| Ghost | Minimal UI, toolbars |

### Form Fields
- Label above input (not placeholder as label)
- Error messages below field
- Helper text in muted color
- Required indicator: asterisk or "(required)"
- Disabled: 50% opacity

### Cards
- Border radius: 8-12px
- Shadow: subtle (0 1px 3px rgba(0,0,0,0.1))
- Padding: 16-24px
- Hover: slightly elevated shadow

## Accessibility (WCAG 2.1 AA)

### Keyboard Navigation
- [ ] All interactive elements focusable
- [ ] Visible focus indicator
- [ ] Logical tab order
- [ ] Skip links for main content
- [ ] Escape closes modals

### Screen Readers
- [ ] Semantic HTML (nav, main, article)
- [ ] Alt text for images
- [ ] ARIA labels where needed
- [ ] Heading hierarchy (h1 → h2 → h3)
- [ ] Live regions for updates

### Motion
- [ ] Respect prefers-reduced-motion
- [ ] No auto-playing video
- [ ] Pause/stop controls
- [ ] No flashing content (>3 per second)

## Responsive Breakpoints

```css
/* Mobile first */
sm: 640px   /* Small tablets */
md: 768px   /* Tablets */
lg: 1024px  /* Small laptops */
xl: 1280px  /* Desktops */
2xl: 1536px /* Large screens */
```

## Common UX Patterns

### Loading States
- Skeleton screens for content
- Spinners for actions
- Progress bars for uploads
- Optimistic updates

### Empty States
- Friendly illustration
- Clear message
- Call to action
- Help link

### Error States
- Inline validation
- Clear error message
- How to fix
- Recovery action

### Confirmation Dialogs
- Clear title
- Consequence explanation
- Cancel is default focus
- Destructive action styled differently

## Touch Targets

- Minimum size: 44×44px (iOS), 48×48px (Android)
- Spacing between targets: 8px minimum
- Thumb zone consideration for mobile
