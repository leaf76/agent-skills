# Design token spec (native iOS + Android)

Prefer **semantic tokens** over raw palette values.

## Naming rules

- Use `.` separators: `color.bg.primary`
- Semantic first: `color.text.primary` not `color.gray.900`
- Use consistent scales: spacing in `2/4/8/12/16/24/32`
- Avoid platform-specific names in the token itself; put platform mapping in notes

## Suggested token groups

### Colors

- `color.bg.*` (backgrounds)
- `color.surface.*` (cards/sheets)
- `color.text.*` (primary/secondary/disabled/inverse)
- `color.border.*`
- `color.brand.*`
- `color.state.*` (error/warn/success/info)

### Typography

- `type.family.*`
- `type.size.*`
- `type.lineHeight.*`
- `type.weight.*`

### Layout and shape

- `space.*`
- `radius.*`
- `elevation.*` (or `shadow.*`)

## Minimal JSON schema example

Use this as a starting point when engineers want a machine-readable spec:

```json
{
  "color": {
    "bg": {
      "primary": "#FFFFFF",
      "secondary": "#F7F7F7"
    },
    "text": {
      "primary": "#111111",
      "secondary": "#666666",
      "inverse": "#FFFFFF"
    },
    "state": {
      "error": "#D92D20",
      "success": "#12B76A"
    }
  },
  "space": {
    "2": 2,
    "4": 4,
    "8": 8,
    "12": 12,
    "16": 16,
    "24": 24,
    "32": 32
  },
  "radius": {
    "sm": 6,
    "md": 10,
    "lg": 14
  }
}
```

## Platform mapping notes (keep short)

- iOS: map colors to Asset Catalog (light/dark) or SwiftUI Color extensions; respect Dynamic Type.
- Android: map colors to Material color roles where possible; expose tokens via Compose `ColorScheme` or resource XML.
- Accessibility: ensure contrast ratios meet target and text scales without clipping.
