---
description: Create a new business-planning case folder with the standard skeleton.
argument-hint: <case title or slug>
allowed-tools: Bash, Write, Read
---

# /create-case

Create a new case folder under `cases/` with the standard skeleton, via the deterministic
helper script — never by hand-writing the folders/files yourself.

## Critical rules (do not skip)
- **This is deterministic setup, not reasoning.** Use `scripts/create_case.py` to build
  the skeleton. Do not create the folders/files yourself, and do not call any LLM/API to
  do this.
- **Never overwrite an existing case.** The script already refuses to; do not work around
  that by deleting or renaming anything.

## Input
`$ARGUMENTS` is the case title (e.g. "AI consulting business"). If empty, ask the user for
a case title before doing anything.

## Steps

1. Run the script:

   ```
   python scripts/create_case.py "<title>"
   ```

   This derives the slug and today's date, refuses to overwrite an existing case folder,
   and writes the standard skeleton plus starter `problem.md` / `config.yaml`:

   ```
   cases/<date>-<slug>/
     problem.md
     config.yaml
     evidence/{raw,processed,summaries}/
     output/
   ```

2. If the script reports the case already exists, stop and report it — do not overwrite.
3. Report the created path and the next steps the script prints: fill `problem.md`, adjust
   `config.yaml`, drop source files into `evidence/raw/`, then run `/process-evidence`.

## Output
- `cases/<date>-<slug>/` — the new case skeleton, with starter `problem.md` and
  `config.yaml` (see `scripts/create_case.py` for their exact content).

## Rules
- This command is deterministic setup only. Do not read or interpret any evidence here.
- Do not overwrite an existing case folder.
- If the script is missing or errors, report it; do not substitute manual work for it.
