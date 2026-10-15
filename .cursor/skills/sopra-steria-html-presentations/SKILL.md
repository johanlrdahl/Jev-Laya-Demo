---
name: sopra-steria-html-presentations
description: >
  Create visually exceptional HTML presentations, documents and interactive slides in Sopra Steria branding.
  Supports four modes: (1) Scroll pages for sales material, one-pagers and landing pages,
  (2) Reveal.js presentations with slide transitions and keyboard navigation,
  (3) Adaptive presentations with per-slide toggle between Business/Technical levels,
  (4) Drilldown presentations with clickable cards that open detailed overlays.
trigger: >
  Use this skill when the user asks to create HTML presentations, sales documents, one-pagers,
  landing pages, pitch material, recruitment pages, interactive slides, reveal.js presentations,
  or other visual HTML documents. Also trigger on "design-skill", "HTML presentation",
  "sales material", "one-pager", "browser presentation", "reveal.js", "adaptive", "business/technical",
  "drilldown", "interactive presentation", or requests for visual material in Sopra Steria style.
  If the user does NOT specifically ask for .pptx, prefer this skill for a modern, interactive result.
---

# Sopra Steria Design Skill

> **Created by:** Erik Monsen — erik.monsen@soprasteria.com | Sopra Steria Bergen

You are an expert designer producing visually exceptional HTML documents in Sopra Steria branding. The ambition level is **conference keynote** — every presentation should impress with animations, visual effects and thorough design. Everything you produce must be **a single HTML file** with all CSS inline/embedded.

**IMPORTANT:** Always read the relevant reference template from `assets/` BEFORE generating. The reference templates are the authoritative source for all CSS — copy the CSS verbatim from there. This skill describes rules and decisions, not implementation details.

## Mode selection

| User request | Mode | Reference template |
|----------------------|-------|-------------|
| One-pager, landing page, sales material, sales document | **Scroll** | No template — use the scroll architecture (section A) |
| Presentation, slide deck, pitch, meeting deck | **Reveal.js** | `assets/reference-template.html` |
| "Adaptive", "business/technical", mixed audience | **Adaptive** | `assets/adaptive-reference.html` |
| "Interactive", "clickable", "drilldown" | **Drilldown** | `assets/drilldown-reference.html` |
| Combination of adaptive + drilldown | **Full** | `assets/drilldown-reference.html` (has both) |

If unclear, ask the user. Default is **Reveal.js** for presentations and **Scroll** for documents.

---

## 1. Color palette

### Primary colors
| Name | Hex | CSS Variable | Use |
|------|-----|-------------|------|
| Sopra Steria Purple | `#4D1D82` | `--ss-purple` | Primary brand, headings, 60-70% visual weight |
| Warm Purple | `#8B1D82` | `--ss-warm-purple` | Accents, gradient endpoint |
| Dark Purple | `#2A1449` | `--ss-dark-purple` | Deep backgrounds, cover/closing |
| BG Purple | `#EDE9F2` | `--ss-bg-purple` | Light content background |
| BG Beige | `#FDF2E5` | `--ss-bg-beige` | Warm content background |

### Secondary colors
| Name | Hex | CSS Variable | Use |
|------|-----|-------------|------|
| SS Black | `#1D1D1B` | `--ss-black` | Body text |
| Red | `#CF022B` | `--ss-red` | Highlights, statistics, numbers |
| Orange | `#F07D00` | `--ss-orange` | CTA, accent lines, links |
| Grey | `#A8A8A7` | `--ss-grey` | Secondary text, dividers |
| Teal | `#009688` | `--ss-teal` | Positive indicators, variation |

### Gradients
```css
/* Cover/closing */ background: linear-gradient(135deg, #2A1449 0%, #4D1D82 50%, #3a1566 100%);
/* Section divider 1 */ background: linear-gradient(135deg, #2A1449 0%, #4D1D82 100%);
/* Section divider 2 */ background: linear-gradient(135deg, #4D1D82 0%, #8B1D82 100%);
/* Accent line */ background: linear-gradient(90deg, #CF022B, #F07D00);
/* Gradient text */ background: linear-gradient(135deg, #CF022B, #F07D00); -webkit-background-clip: text; -webkit-text-fill-color: transparent;

/* Sopra Steria signature gradient (5-stops, for illustrations and decorative elements) */
background: linear-gradient(to right, #4D1D82 0%, #8B1D82 10%, #CF022B 60%, #F07D00 100%);
```

---

## 2. Typography

Sopra Steria's official font is **Hurme Geometric** (Sans 3 for body text, Sans 4 for headings). **Tahoma** is the approved fallback for desktop applications and when Hurme is not available.

### Font stack (CSS)
```css
--font-heading: 'Hurme Geometric Sans 4', Tahoma, Arial, sans-serif;
--font-body: 'Hurme Geometric Sans 3', Tahoma, Arial, sans-serif;
```

For HTML presentations without access to Hurme font files: use **Tahoma** directly (system font, works everywhere).

### Sizes

| Element | Size | Weight |
|---------|----------|------|
| Cover title | 2.2-2.8em | Bold |
| Slide title (h2) | 1.5em | Bold |
| Card heading (h3) | 0.9-1.1em | Bold |
| Body text | 0.5-0.6em | Normal |
| Labels/captions | 0.42-0.55em | Normal |

### Tagline
Sopra Steria's tagline is **"The world is how we shape it."** — use on cover or closing when appropriate (Hurme Geometric Sans 4 Bold).

**Rules:** Max 2 font weights per page. **No emojis** — use SVG icons. Purple dominates (60-70%).

---

## 3. Visual ambition

Every presentation should have keynote quality. The reference templates contain all CSS — here are the concepts:

### Animated numbers
Key numbers animate from 0 to target value with ease-out cubic. Use `.counter[data-target]` and trigger via `Reveal.on('fragmentshown')`. See the reference template for JS.

### Particles and waves (dark slides)
Cover, section dividers and closing should have floating particles (6-8 pieces, varying size/color/timing) and animated waves at the bottom. See the reference template for CSS.

### Theme background animations
Each presentation gets **one unique background animation** on cover/closing that matches the theme:
- **Aurora:** Horizontal bands, `#00e6b4` + `#8B1D82`, skewX
- **Magma:** Radial-gradient flow, `rgba(240,125,0)` + `rgba(207,2,43)`
- **Bioluminescent:** Pulsing dots, `rgba(0,210,190)`
- **Ocean:** Slow bubbles, `rgba(0,150,200)`

Create new themes: 2-3 colors with alpha 0.1-0.3, `filter: blur(60-100px)`, 2-3 layers with different timing.

### Hover effects
All cards should have `transition: transform 0.4s, box-shadow 0.4s` and `:hover { transform: translateY(-8px) rotate(-0.5deg) }`.

### Glow orbs
Pulsing radial-gradient circles with `animation: pulseGlow 4s ease-in-out infinite alternate`.

### Gradient text
For closing and important numbers: `-webkit-background-clip: text; -webkit-text-fill-color: transparent`.

### Animation decision tree

| Content type | Animation |
|---|---|
| Cards in grid | `fragment fade-up` |
| Key numbers | `fragment zoom-in` + animated counter |
| Timelines / steps | `fragment fade-up` in sequence |
| Quotes | `fragment fade-in` |
| Bar charts | CSS `transition: width` |
| Donut chart | `fragment zoom-in` |

**Rules:** Never mix `fade-up` and `zoom-in` on the same slide. Max 4-5 fragments per slide. Cover/closing/dividers do NOT have fragments.

### Visual checklist
- [ ] Cover has particles, glow-orbs and waves?
- [ ] Key numbers are animated with counters?
- [ ] Cards have hover effects?
- [ ] Backgrounds alternate between white, BG Purple and BG Beige?
- [ ] Section dividers have gradient + particles?
- [ ] Closing is as visually rich as the cover?
- [ ] At least one unique theme animation?
- [ ] ALL content fits within 720px height?
- [ ] No horizontal shift?
- [ ] Correct native European characters in ALL text?

---

## 4. Design rules (CRITICAL)

1. **Background alternation**: Alternate between white, BG Purple, BG Beige. Never 3+ white slides in a row.
2. **Decorative SVGs**: Circles/rectangles with opacity 0.03-0.05, **negative offset >= half the width** (400px element → at least `-200px`). Only peek in from the corners. Max 1-2 per slide.
3. **Fragment animations**: `class="fragment fade-up"` on cards, stats, timelines.
4. **Print-friendly**: `@media print` with clean colors.
5. **Responsive and accessible**: Semantic HTML, `prefers-reduced-motion`.
6. **Footer**: `© [year] Sopra Steria`.

### CRITICAL — Viewport overflow (reveal.js)

Reveal.js uses `width: 1280, height: 720`. Everything must fit within 720px.

**Max values:**
- Slide padding: `padding: 20px 60px`
- H2: `1.5em`, `margin-bottom: 0.2em`
- Card padding: `0.8em 1.2em`
- Grid gap: `0.6em`
- Card body: `0.5em`, line-height 1.35
- Stat numbers: max `2.4em`
- Section-divider numbers: max `6-7em`
- Icon wraps: `36-40px`

**Rule of thumb:** Title + 3-column grid with header + paragraph = approx. 640px content + 48px padding = 688px.

### CRITICAL — Horizontal alignment (reveal.js)

**Mandatory CSS fix:**
```css
.reveal .slides section { padding: 20px 60px; box-sizing: border-box; }
.slide-content { position: relative; z-index: 1; width: 100%; box-sizing: border-box; }
```

- **Always** `box-sizing: border-box` on sections
- **Never** `width: 100%` on grid elements — they fill automatically
- Available width: 1280 - 120 = **1160px**
- **CSS specificity:** Reveal.js theme overrides `margin`/`padding`/`font-size` on `p`, `ul`, `li`. Solution: prefix with `.reveal`:
  ```css
  .reveal .stats-punchline { margin: 1em auto 0; }
  ```

---

## 5. Mode A: Scroll pages

A single HTML file with `scroll-snap-type: y mandatory`. No external dependencies.

```html
<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Title] — Sopra Steria</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-snap-type: y mandatory; scroll-behavior: smooth; }
    body { font-family: Tahoma, Geneva, sans-serif; color: #1D1D1B; line-height: 1.6; }
    .slide { width: 100vw; min-height: 100vh; scroll-snap-align: start;
      display: flex; flex-direction: column; justify-content: center;
      padding: 4rem 5rem; position: relative; overflow: hidden; }
    @media print { .slide { page-break-after: always; } }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; } }
  </style>
</head>
<body>
  <section class="slide slide-cover"><!-- gradient bg, white text --></section>
  <section class="slide"><!-- content --></section>
  <footer>© [year] Sopra Steria</footer>
</body>
</html>
```

**Layout:** Max 1200px centered. Padding `4rem 2rem`. 3-column grid for cards, 2-column for comparison. Use the component classes from the reference template.

---

## 6. Mode B: Reveal.js

**Read `assets/reference-template.html` for exact CSS and HTML patterns.**

```html
<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reset.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/theme/white.css">
  <style>/* Copy CSS from the reference template — adapt as needed */</style>
</head>
<body>
  <div class="reveal"><div class="slides">
    <section><!-- slides --></section>
  </div></div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script>
    Reveal.initialize({ hash: true, slideNumber: 'c/t', transition: 'slide',
      controls: true, controlsLayout: 'bottom-right', progress: true, center: true,
      width: 1280, height: 720, margin: 0.04, minScale: 0.2, maxScale: 3.0 });
  </script>
</body>
</html>
```

### Slide types

| # | Type | Background | Key classes |
|---|------|----------|---------------|
| 1 | Cover | Gradient | `.cover`, `.accent-bar`, `.tagline`, `.meta`, `.logo-text` |
| 2 | Agenda | BG Purple | `.agenda-grid`, `.agenda-card`, `.card-num` |
| 3 | Section divider | Gradient | `.section-divider`, `.section-number`, `.accent-line` |
| 4 | Stats | BG Purple | `.stats-grid`/`.stat-card` OR `.stats-hero`/`.stat-big` |
| 5 | Service/Feature cards | BG Beige | `.service-grid`, `.service-card`, `.icon-wrap` |
| 6 | Timeline | White | `.timeline`, `.timeline-item`, `.dot` |
| 7 | Two-column | BG Purple | `.results-grid`, `.result-col.left`/`.right` |
| 8 | Quote | BG Beige | `.quote-slide`, `.quote-container`, `.quote-mark` |
| 9 | Next steps | BG Purple | `.steps-grid`, `.step-card`, `.step-num` |
| 10 | Closing | Gradient | `.closing`, `.closing-bar`, `.gradient-text` |

**Additional components** (see reference template for CSS):
- `.bar-chart` / `.bar-fill.purple|red|orange|teal` — horizontal bar chart
- `.donut-chart[data-center]` — conic-gradient donut
- `.progress-row` / `.progress-fill` — progress bar
- `.team-grid` / `.person-card` / `.person-avatar` — team cards
- `.flow-diagram` / `.flow-box` / `.flow-arrow` — process diagram
- `.has-info` / `.info-box` — hover info box (pure CSS)

**Recommended structure:** Cover → Agenda → (Section divider → Content) × N → Quote → Next steps → Closing. Vary content layouts — never the same type twice in a row.

---

## 7. Mode C: Adaptive (Business / Technical)

**Read `assets/adaptive-reference.html` for exact CSS, JS and HTML.**

### Concept
- Cover has global level selector (`Business` / `Technical`)
- Each content slide has a per-slide toggle in the upper right corner
- Same title and story — only depth, language and visuals vary
- Independent toggles — switching one slide does not affect others

### Business vs Technical

| Business | Technical |
|-----------|---------|
| Business value and outcomes | Architecture and implementation |
| "73% shorter time to production" | "<50ms P99 API latency" |
| Service cards with benefits | Architecture diagrams + code blocks |

### Technical patterns (available in adaptive-reference.html)
- `.arch-diagram` / `.arch-box` — architecture diagram with gradient boxes
- `.code-block` with syntax highlighting (`.kw`, `.str`, `.cm`, `.fn`, `.ty`)

---

## 8. Mode D: Drilldown

**Read `assets/drilldown-reference.html` for exact CSS, JS and HTML.**

### Concept
- Add `class="clickable"` and `onclick="openDrilldown('key')"` on cards
- Click opens a full-screen overlay with a branded one-pager
- Escape or click outside closes the overlay
- Reveal.js navigation is paused while the overlay is open
- Always include `_default` fallback in drilldownData

### Drilldown content
- 200-400 words per one-pager
- 2-3 metrics (`.dd-metrics`) where relevant
- 2-4 tags (`.dd-tag.purple|red|orange|teal`)
- Code blocks (`.dd-tech-block`) for technical drilldowns

---

## 9. Icon library

Standard SVG icons (24x24, stroke-based, `stroke="#fff"`, `stroke-width="2"`). Copy directly:

```html
<!-- User --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
<!-- Team --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
<!-- Cloud --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M18 10h-1.26A8 8 0 109 20h9a5 5 0 000-10z"/></svg>
<!-- Database --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
<!-- Trending --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
<!-- Gear --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
<!-- Rocket --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 00-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 012-3.95A12.88 12.88 0 0122 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 01-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 3 0 3 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-3 0-3"/></svg>
<!-- Arrow right --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
<!-- Checkmark --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="9 12 11.5 14.5 16 10"/></svg>
<!-- Warning --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
<!-- Security --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
<!-- Success --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
<!-- Search --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
<!-- Code --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
<!-- Layout --> <svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
```

Create new icons following the same pattern (24x24, stroke-based) as needed.

---

## 10. CSS class reference

| Class | Purpose |
|--------|--------|
| `.deco` | Decorative SVG (absolute, no pointer events) |
| `.slide-content` | Content wrapper (z-index: 1, above decorations) |
| `.cover` | Cover layout (flex, left-aligned) |
| `.section-divider` | Section break (gradient background) |
| `.agenda-grid` / `.agenda-card` | 2-column agenda |
| `.service-grid` / `.service-card` | 3-column cards with icon boxes |
| `.stats-grid` / `.stat-card` | 3-4-column stat cards |
| `.stats-hero` / `.stat-big` | Hero statistic with animated numbers |
| `.timeline` / `.timeline-item` | Horizontal timeline |
| `.results-grid` / `.result-col` | 2-column comparison |
| `.quote-slide` / `.quote-container` | Quote with SVG marks |
| `.steps-grid` / `.step-card` | 3-column numbered steps |
| `.closing` | Centered closing slide |
| `.bar-chart` / `.bar-row` / `.bar-fill` | Horizontal bar chart |
| `.donut-chart` | Donut chart with conic-gradient |
| `.progress-row` / `.progress-fill` | Progress bar |
| `.team-grid` / `.person-card` | Team card with avatar |
| `.flow-diagram` / `.flow-box` | Process diagram |
| `.has-info` / `.info-box` | Hover info box |
| `.clickable` | Clickable element with chevron |
| `.cover-selector` / `.cover-btn` | Global level selector (adaptive) |
| `.slide-toggle` / `.toggle-btn` | Per-slide toggle (adaptive) |
| `.drilldown-overlay` / `.drilldown-card` | Drilldown overlay |
| `.dd-metrics` / `.dd-tags` | Metrics and tags in drilldown |
| `.highlight` | Red bold text |
| `.accent-bar` / `.accent-line` | Orange gradient accents |
| `.gradient-text` | Gradient text (red→orange) |

---

## Logo

Official logo files are in `assets/`:

| Variant | File | Used on |
|---------|-----|-----------|
| Color (primary) | `Sopra-Steria_logo_RGB_black-color.png` | White or light background |
| Black (monochrome) | `Sopra-Steria_logo_RGB_black.png` | White or light background |
| White (reversed) | `Sopra-Steria_logo_RGB_white.png` | Dark or colored background |

**Usage rules:**
- **Minimum size:** 32mm (print) / 170px (digital)
- **Clear space:** 2× symbol width horizontally, 1× symbol width vertically. No other elements in this area.
- **Never:** stretch, compress, distort, rotate, recolor, or apply effects to the logo.
- **Placement:** On cover and closing. Use color variant on light background, white variant on dark.

**Use in HTML:**
```html
<img src="assets/Sopra-Steria_logo_RGB_white.png" alt="Sopra Steria" style="height:40px;">
```

Text-based "SOPRA STERIA" (as the `.logo-text` class) is an acceptable alternative for small placements where the PNG logo becomes too small.

---

## Images

When the user wants images in the presentation (team photos, logos, figures, illustrations):

**Folder structure:**
```
project/
├── presentation.html
└── images/
    ├── erik.jpg
    ├── customer-logo.png
    └── market-figure.png
```

**Rules:**
- Use relative path: `<img src="images/filename.jpg">`
- Team photos/portraits: use `border-radius: 50%; object-fit: cover; width: 80px; height: 80px;` in `.person-avatar`
- Logos under ~50KB: can be base64-encoded for single-file delivery
- Always add an `alt` attribute on images for accessibility
- The user tells you which images go on which slides

**Example — person card with image:**
```html
<div class="person-card">
    <img class="person-avatar" src="images/erik.jpg" alt="Erik Monsen"
         style="width:80px; height:80px; border-radius:50%; object-fit:cover;">
    <div class="person-name">Erik Monsen</div>
    <div class="person-role">Lead Architect</div>
</div>
```

---

## Non-negotiable rules

1. **All content visible without JavaScript.** Animations are decoration.
2. **A single HTML file.** All CSS embedded. Reveal.js is the only CDN. (Images may live in an `images/` folder alongside.)
3. **Font stack.** Hurme Geometric (Sans 3 body, Sans 4 heading) primary, Tahoma fallback. For HTML without Hurme access: use Tahoma directly.
4. **No emojis.** Use SVG icons.
5. **Purple dominates** (60-70%). Red/orange are accents only.
6. **European special characters.** Always use the correct native characters in ALL visible text. Never use ASCII approximations. The skill produces output for European Sopra Steria markets, so all of the following must render correctly:
   - **Norwegian/Danish (æøå):** "områder" (not "omrader"), "strømninger" (not "stromninger"), "høyde" (not "hoyde"), "overvåker" (not "overvaker"), "påvirkning" (not "pavirkning"), "så/på/år/nå/nær" (not "sa/pa/ar/na/naer"), "å forstå" (not "a forsta"), "størst" (not "storst"), "atmosfæren" (not "atmosfaeren").
   - **Swedish (åäö):** "förändring" (not "forandring"), "möjlighet" (not "mojlighet").
   - **French (àâçéèêëîïôœùûüÿ):** "café" (not "cafe"), "français" (not "francais"), "œuvre" (not "oeuvre").
   - **German (äöüß):** "Größe" (not "Grosse"), "Qualität" (not "Qualitaet"), "Straße" (not "Strasse").
   - **Spanish (áéíóúñü¿¡):** "España" (not "Espana"), "año" (not "ano"), "¿Qué?" (not "Que?").
   - **Portuguese (ãõáâàçéêíóôú):** "São Paulo" (not "Sao Paulo"), "ação" (not "acao").
   - **Italian (àèéìíîòóù):** "città" (not "citta"), "perché" (not "perche").
   - **Polish (ąćęłńóśźż):** "Gdańsk" (not "Gdansk"), "łódź" (not "lodz").
   - **Czech/Slovak (áčďéěíňóřšťúůýž):** "Plzeň" (not "Plzen"), "Škoda" (not "Skoda").
   - **Finnish (äö):** "Hämeenlinna" (not "Hameenlinna"), "työ" (not "tyo").

   **Double-check ALL text before delivery.** Never substitute ASCII approximations for native characters.
7. **Responsive.** Works on all screen sizes.
8. **Sopra Steria logo** — use text-based logo.
9. **Footer**: `© [year] Sopra Steria`.
10. **Always read the relevant reference template** from `assets/` before generating. Copy CSS from there.
11. **Adapt for other brands**: Swap CSS variables, font and logos.
