# Sopra Steria Design Skill for Claude Code

Create visually exceptional HTML presentations with Sopra Steria branding directly in Claude Code. Keynote quality, no PowerPoint.

## What it does

The skill generates ready-to-use HTML with:
- Animated counters, particle effects, gradient text and hover transformations
- Four modes: scroll pages, reveal.js presentations, adaptive (business/technical toggle) and drilldown (clickable cards with overlay)
- Sopra Steria branding (colors, fonts, icons)
- Responsive, accessible and print-friendly

## Installation

1. Download the `design-skill` folder (you received it as a zip, via Teams or SharePoint)
2. Unzip the file
3. Open Claude Code and type:

```
Copy the design-skill folder from Downloads to ~/.claude/skills/
```

Claude handles the rest. Start a new conversation afterwards, and the skill is ready to use.

> **Tip:** If the folder is somewhere other than Downloads, just tell Claude where: *"Copy design-skill from Desktop to ~/.claude/skills/"*

## Usage

Just ask Claude to create a presentation:

```
Create a presentation about cloud migration for a customer meeting
```

```
Create an adaptive presentation about AI in healthcare
```

```
Create a one-pager about Sopra Steria's advisory services
```

The skill is triggered automatically when you mention: presentation, slide deck, one-pager, landing page, sales material, HTML presentation, reveal.js, adaptive, drilldown.

## Modes

| Mode | When | What you say |
|-------|-----|-------------|
| **Scroll** | Sales documents, one-pagers | "Create a one-pager about..." |
| **Reveal.js** | Presentations, pitch | "Create a presentation about..." |
| **Adaptive** | Mixed audience | "Create an adaptive presentation..." |
| **Drilldown** | Interactive cards | "Create an interactive presentation with clickable cards..." |

## Images

Want images in the presentation (team photos, logos, figures)? Place them in an `images/` folder alongside the HTML file and tell Claude where they should go:

```
Create a presentation about the team. Use erik.jpg on slide 2 and customer-logo.png in the header.
```

```
project/
├── presentation.html
└── images/
    ├── erik.jpg
    ├── customer-logo.png
    └── market-figure.png
```

## File structure

```
design-skill/
├── SKILL.md                    # Rules and design system
├── README.md                   # This file
└── assets/
    ├── reference-template.html # CSS for standard presentations
    ├── adaptive-reference.html # CSS for adaptive mode
    └── drilldown-reference.html# CSS for drilldown mode
```

## Customization

The skill is built for Sopra Steria, but can be adapted to other brands. Change the CSS variables in the reference templates:

```css
:root {
    --ss-purple: #4D1D82;    /* Your primary color */
    --ss-red: #CF022B;       /* Your accent color */
    --ss-orange: #F07D00;    /* Your CTA color */
    /* etc. */
}
```

And update the font from Tahoma to your brand's font in SKILL.md.

## Created by

Erik Monsen — erik.monsen@soprasteria.com | Sopra Steria Bergen
