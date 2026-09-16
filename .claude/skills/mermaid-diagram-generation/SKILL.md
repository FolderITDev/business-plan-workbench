---
name: mermaid-diagram-generation
description: Procedure and patterns for generating clear Mermaid diagrams in Obsidian Markdown, with a rule to fall back to a table when a diagram would be cluttered. Use when a case asks for diagrams (business model map, customer segment map, go-to-market timeline, risk map, dependency graph).
---

# Mermaid diagram generation

Reference for producing Obsidian-native Mermaid diagrams. The rule "use Mermaid only where
it adds clarity" lives in `CLAUDE.md` (C7); this skill is the how-to and pattern catalog.

## When to draw (and when not to)
Draw a diagram only when it makes a relationship clearer than prose or a table would.
**If a diagram would have more than ~12 nodes or crossing edges that make it unreadable,
use a Markdown table or split it into two simpler diagrams instead.** A cluttered diagram
is worse than a clean table.

Only generate the diagram types requested in the case's `config.yaml` `diagram_types`,
plus any that clearly add value.

## Format
Fenced ` ```mermaid ` blocks render natively in Obsidian. Keep node labels short. Put each
diagram in its own note under `output/diagrams/` with frontmatter and a one-line caption,
and wikilink it from the relevant section.

## Patterns

**Business model map** — flowchart linking segments → value prop → channels → revenue:

```mermaid
flowchart LR
  S1[SMBs < 20 staff] --> VP[Done-with-you AI automation]
  VP --> CH[Referrals + local network]
  CH --> REV[Monthly retainer + setup fee]
```

**Customer segment map** — group segments by a dimension (e.g. urgency vs ability to pay):

```mermaid
flowchart TB
  subgraph High urgency
    A[Ops-heavy services]
    B[Solo professionals]
  end
  subgraph Low urgency
    C[Hobby businesses]
  end
```

**Go-to-market timeline** — phases over the time horizon:

```mermaid
gantt
  title Go-to-market (90 days)
  dateFormat YYYY-MM-DD
  section Validate
  Customer interviews :2026-06-23, 21d
  section Launch
  First paid pilot    :2026-07-14, 30d
```

**Risk map** — likelihood × impact as a labeled grid or flow:

```mermaid
flowchart LR
  R1[Low switching cost] -->|High impact / Med likelihood| M1[Mitigate: annual contracts]
  R2[Owner has no time] -->|High impact / High likelihood| M2[Mitigate: done-for-you setup]
```

**Dependency graph** — what must happen before what:

```mermaid
flowchart LR
  A[Define offer] --> B[Price package]
  B --> C[First pilot]
  C --> D[Case study]
  D --> E[Referrals]
```

## Quality rules
- Label edges with meaning where it helps (e.g. risk severity).
- Tie diagram content back to evidence where possible; do not invent nodes the evidence
  and plan do not support.
- Prefer a few clear diagrams over many noisy ones.
- If you cannot make a diagram readable, say so and provide a table instead.
