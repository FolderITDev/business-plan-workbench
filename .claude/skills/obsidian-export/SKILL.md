---
name: obsidian-export
description: Conventions for writing Obsidian-ready Markdown — YAML frontmatter, wikilinks, tags, callouts, tables, checklists, and evidence citations. Use whenever generating or finalizing files in a case's output/ folder.
---

# Obsidian export conventions

Reference for producing readable, Obsidian-native Markdown. The rule that the folder
bundle is the source of truth and the single-file report is script-generated lives in
`CLAUDE.md` (C6); this skill is the formatting how-to.

## Frontmatter
Every output note starts with YAML frontmatter:

```yaml
---
type: business-plan          # or: index, business-diagnosis, market-analysis, ...
status: draft
created: 2026-06-23
case_id: ai-consulting-business
business_stage: idea_validation
tags:
  - business-plan
  - <case-specific-tag>
---
```

## File naming
Numbered, kebab-case, stable order:
`00-index.md`, `01-business-diagnosis.md`, `02-market-analysis.md`, … Diagrams go in
`output/diagrams/`. The index (`00-index.md`) links to every section.

## Links
- Use `[[wikilinks]]` between notes in the bundle, e.g. `[[04-business-model]]`.
- Link to a heading with `[[05-go-to-market-plan#Phase 1]]`.
- The index note must wikilink to all sections in order.

## Evidence citations (load-bearing — see CLAUDE.md C4)
Every material claim cites its evidence or is tagged. Inline style:
- `Owners distrust generic AI tools (E1.2).`
- `Estimated 10% conversion **[assumption]**.`
- `Local market is large enough to sustain the service **[hypothesis]**.`
- `Whether owners will pay a retainer **[open question]**.`

Each section ends with a short **Sources** line listing the evidence IDs it relied on.

## Callouts
Use Obsidian callouts to flag epistemic status:

```md
> [!note] Assumption
> Conversion of 10% is assumed, not measured (see E3.2).

> [!warning] Risk
> Low switching cost may erode retention (E2.2).

> [!tip] Next action
> Validate pricing with 5 target customers this month.
```

## Tables and checklists
- Use tables for comparisons (segments, competitors, options, financial lines).
- Use checklists for action items so they are trackable in Obsidian:

  ```md
  - [ ] Interview 5 target customers (Week 1)
  - [ ] Draft one fixed-price package (Week 2)
  ```

## Tone and quality
Specific, practical, founder-oriented, honest about uncertainty. Never present an
assumption as a fact. Prefer a clear table over a vague paragraph.

## Diagrams
Embed Mermaid only where it adds clarity (see the `mermaid-diagram-generation` skill).
Diagram notes live in `output/diagrams/` and are wikilinked from the relevant section.
