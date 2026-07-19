# A-Share Antifragile Trading Loop Design System

This project adapts a Revolut-inspired fintech system into a neutral open-source identity. It borrows the precision, flat contrast, and semantic status palette, but never copies brand assets, logos, fonts, or product UI.

## 1. Visual Theme & Atmosphere

The interface should feel calm, exact, and evidence-led. Near-black analytical surfaces and white reading areas create trust through contrast. The first visual signal is always the research loop: market data enters, validation gates remove weak evidence, and an auditable decision exits.

## 2. Color Palette & Roles

| Token | Value | Role |
|---|---|---|
| Ink | `#191C1F` | Primary text and dark analytical surface |
| Paper | `#FFFFFF` | Main reading surface |
| Soft surface | `#F4F4F4` | Secondary background and code blocks |
| Border | `#C9C9CD` | Rules and dividers |
| Action blue | `#494FDF` | Links, selected flow, verified path |
| Positive teal | `#00A87E` | Verified positive state only |
| Warning orange | `#EC7E00` | Degraded or incomplete evidence |
| Danger red | `#E23B4A` | Verified risk or failed gate |
| Muted slate | `#505A63` | Secondary text |

Red, green, and orange are semantic, never decorative. Do not use gradients, colored glow, or a one-note blue/purple palette.

## 3. Typography Rules

- Display and headings: system sans-serif, weight 500-600, line height 1.1-1.25.
- Body: system sans-serif, 16-18px equivalent, line height 1.5.
- Data and code: system monospace with tabular numerals where available.
- Letter spacing is always `0`; never scale type directly with viewport width.
- Use literal headings. Performance-sounding language requires measured evidence.

## 4. Component Styling

- README badges are functional and limited to runtime, market, license, and privacy.
- Tables use one metric per column and always expose source or time range near the data.
- Images are full-width with no more than 8px corner radius.
- Callouts use GitHub-native note/warning blocks.
- Status indicators pair color with text; color alone is insufficient.
- Controls in future UIs use familiar icons and tooltips, with 44px minimum touch targets.

## 5. Layout Principles

- Center only the repository header, language switcher, badges, and hero.
- Put value, quick start, and privacy promise before architecture details.
- Use full-width sections with a constrained reading width; never nest cards.
- Use an 8px spacing rhythm: 8, 16, 24, 32, 48, 64, 80.
- Fixed-format charts and tables require stable widths or responsive overflow.

## 6. Depth & Elevation

Use zero shadows. Depth comes from ink/paper contrast, dividers, and whitespace. Do not use glassmorphism, floating surfaces, bokeh, or decorative orbs.

## 7. Do's and Don'ts

### Do

- Show verify, filter, decide, and evolve as one closed loop.
- Label trading-day windows and explicit degradation states.
- Keep A-shares visible in the title and first viewport.
- Use diagrams to explain process, never to imply returns.

### Don't

- Never publish emails, holdings, costs, quantities, reports, local paths, or default stock lists.
- Never show fake returns, stars, users, endorsements, or live-order claims.
- Never use real stock codes or third-party marks in generated artwork.
- Never turn stale events or missing data into directional conclusions.

## 8. Responsive Behavior

- The hero must remain legible from 320px to wide desktop.
- Essential information cannot depend on side-by-side layouts.
- Tables may scroll horizontally; headings and cells must not overlap.
- Mermaid nodes use short labels and vertical flow on narrow screens.

## 9. Agent Prompt Guide

```text
Create a privacy-first open-source fintech research visual on a flat near-black or white surface. Show A-share market traces entering explicit verification and freshness gates, then producing an auditable decision record. Use #494FDF, #00A87E, #EC7E00, and #E23B4A only as small semantic accents. No text, logos, real stock codes, personal data, returns, gradients, glow, decorative cards, or watermark.
```
