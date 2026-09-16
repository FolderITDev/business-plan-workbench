---
description: Finalize the Obsidian deliverable — validate, then build the single-file report by script.
argument-hint: <path to case folder>
allowed-tools: Read, Edit, Glob, Bash
---

# /export-obsidian-bundle

Finalize the bundle in `<case>/output/`: check it is clean and Obsidian-ready, validate
the Mermaid blocks, and build the single-file report with the deterministic script.

## Critical rules (do not skip)
- **The single-file report is script-generated, not reasoned.** Build it only with
  `scripts/build_full_report.py`. Do not assemble it by hand. (CLAUDE.md C6)
- **Conversion/validation are deterministic.** Use the scripts; don't eyeball-validate
  Mermaid in place of running the checker. (CLAUDE.md C5)
- **Do not silently overwrite manual edits.** (CLAUDE.md C8)

## Input
`$ARGUMENTS` is the case folder path. Operate on `<case>/output/`.

## Steps

1. **Readiness checks** (report a pass/fail list, fix only safe formatting issues):
   - every `*.md` in `output/` starts with YAML frontmatter
   - `00-index.md` wikilinks to all ten sections
   - each section has a `**Sources:**` line
   - no leftover `{{placeholder}}` tokens or `<!-- TEMPLATE ... -->` comments remain
   - diagrams are wikilinked from a parent section

2. **Validate Mermaid** (deterministic):

   ```
   python scripts/validate_mermaid.py "<case>/output"
   ```

   If it reports issues, fix the offending blocks (or replace a cluttered diagram with a
   table per the mermaid skill) and re-run until clean.

3. **Build the single-file report** (deterministic):

   ```
   python scripts/build_full_report.py "<case>"
   ```

   This writes `<case>/output/00-full-report.md` by concatenating the numbered sections
   (excluding `review-notes.md` and the report itself).

4. **Report**: the readiness checklist result, the Mermaid validation result, and the
   path to the generated `00-full-report.md`. Note anything the user should fix manually.

## Output
- a clean, validated `output/` bundle
- `output/00-full-report.md`

## Rules
- Do not generate or rewrite plan content here — this step finalizes and packages only.
- If a script is missing or errors, report it; do not substitute manual work for it.
