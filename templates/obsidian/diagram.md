---
type: diagram
status: draft
created: {{created}}
case_id: {{case_id}}
diagram: {{diagram_type}}
tags:
  - business-plan
  - {{case_slug}}
  - diagram
---

<!-- TEMPLATE: diagrams/<name>.md. One diagram per file under output/diagrams/.
     Only create when the diagram beats a table (see mermaid-diagram-generation skill).
     Keep labels short. Replace {{placeholder}} and the mermaid body. -->

# {{diagram_title}}

> [!note] What this shows
> <one line: the relationship this diagram makes clearer than prose.>

```mermaid
flowchart LR
  A[Replace] --> B[with real]
  B --> C[nodes]
```

<!-- If this diagram gets cluttered (>~12 nodes / crossing edges), delete it and use a
     table in the parent section instead. A clean table beats a messy graph. -->

**Referenced from:** [[<parent-section>]]
**Sources:** <E# list, if the diagram encodes evidence-based claims>
