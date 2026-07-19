# A-Share Antifragile Trading Loop Design System

## 1. Visual Theme & Atmosphere

Use a clean, trustworthy financial-research aesthetic: precise, calm, evidence-led, and suitable for an open-source developer audience. Prefer bright white reading surfaces with near-black analytical panels and a single high-confidence blue accent.

## 2. Color Palette & Roles

- Primary blue: `#0052FF` for links, active flow, and verified states.
- White: `#FFFFFF` for the main reading surface.
- Near black: `#0A0B0D` for text and analytical panels.
- Cool gray: `#EEF0F3` for secondary surfaces and separators.
- Positive green: `#16A36A`, used only for actual positive market states.
- Risk red: `#D93A3A`, used only for actual risk or negative market states.

Do not use red or green as decoration. Do not introduce purple gradients.

## 3. Typography Rules

- Display: system sans-serif, 700 weight, compact but not negatively tracked.
- Section heading: system sans-serif, 600 weight.
- Body: system sans-serif, 400 weight, comfortable line height.
- Code and data: system monospace.
- Use short, literal headings. Keep long explanations in body copy.

## 4. Component Styling

- README badges: functional only, limited to license, runtime, market, cadence, and access mode.
- Tables: clear headers, one concept per column, no decorative status colors.
- Images: maximum 8px visual corner radius; full-width at README scale.
- Callouts: use GitHub-native note syntax for warnings and constraints.
- Diagrams: simple directional flow, blue arrows, white or near-black surfaces.

## 5. Layout Principles

- Center the repository name, value proposition, language navigation, badges, and hero image.
- Keep installation and first-run commands visible before deep technical details.
- Use full-width sections with a consistent reading width.
- Base spacing on an 8px rhythm.
- Never nest decorative cards.

## 6. Depth & Elevation

Use color contrast rather than shadows. If depth is necessary, keep it subtle and limited to the hero image. Avoid glassmorphism, glow, and floating decorative shapes.

## 7. Do's and Don'ts

### Do

- Show the actual decision loop: verify, filter, decide, evolve.
- Explain data windows and degradation behavior explicitly.
- Keep A-shares as the first-viewport market signal.
- Use diagrams and visuals to clarify workflow, not to imply performance.

### Don't

- Do not show personal stock lists, holdings, costs, quantities, or email addresses.
- Do not show fake returns, users, stars, endorsements, or live-trading claims.
- Do not expose internal class names in audience-facing positioning.
- Do not copy third-party logos, screenshots, or branded artwork.

## 8. Responsive Behavior

- Hero imagery must remain legible at mobile README width.
- Tables may scroll naturally in GitHub; keep columns concise.
- Mermaid diagrams should use short node labels.
- Do not rely on side-by-side layouts for essential information.

## 9. Agent Prompt Guide

When creating new README assets, use:

```text
Clean open-source fintech research aesthetic. White background, near-black analytical surface, #0052FF functional accent, sparse red/green market states. Show an auditable weekly loop connecting verified data, BOLL evidence, capital flow, risk gates, and evolution. No personal data, stock codes, performance claims, logos, tiny text, gradients, glow, or decorative blobs.
```
