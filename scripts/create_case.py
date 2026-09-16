#!/usr/bin/env python3
"""Create a new business-planning case folder with the standard skeleton.

Deterministic helper. No LLM, no network. Safe to re-run: refuses to overwrite
an existing case folder.

Usage:
    python scripts/create_case.py "AI consulting business"
    python scripts/create_case.py "AI consulting business" --date 2026-06-23
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "cases"

PROBLEM_TEMPLATE = """\
# Business Problem / Planning Goal

<one or two sentences describing the business idea or decision to evaluate>

## Context

<relevant background: your skills, resources, situation>

## Goals

- <goal 1>
- <goal 2>

## Constraints

- <constraint 1>
- <constraint 2>

## Desired output

A structured Obsidian-ready business plan with Markdown files and Mermaid diagrams.
"""

CONFIG_TEMPLATE = """\
case_id: {slug}
title: {title}
# business_stage / time_horizon: leave as `auto` to have /generate-business-plan
# resolve them (use an explicit value here if set; else ask you; else infer from
# problem.md). Replace `auto` with a fixed value to pin it.
business_stage: auto   # e.g. idea_validation | pre_launch | early_revenue | scaling
time_horizon: auto     # e.g. 30_days | 90_days | 6_months | 1_year
diagram_types:
  - business_model_map
  - customer_segment_map
  - go_to_market_timeline
  - risk_map
"""

# Folders that should exist for a case (cases are local-only, so no .gitkeep needed).
EVIDENCE_SUBDIRS = ["evidence/raw", "evidence/processed", "evidence/summaries", "output"]


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_date(value: str | None) -> str:
    if value is None:
        return _dt.date.today().isoformat()
    # Validate the supplied date format.
    _dt.date.fromisoformat(value)
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a new case folder.")
    parser.add_argument("title", help="Case title, e.g. 'AI consulting business'")
    parser.add_argument("--date", help="Override date prefix (YYYY-MM-DD)", default=None)
    args = parser.parse_args(argv)

    slug = slugify(args.title)
    if not slug:
        print("ERROR: title produced an empty slug.", file=sys.stderr)
        return 2

    date = parse_date(args.date)
    case_name = f"{date}-{slug}"
    case_dir = CASES_DIR / case_name

    if case_dir.exists():
        print(f"ERROR: case already exists: {case_dir}", file=sys.stderr)
        print("Refusing to overwrite. Choose a different title or date.", file=sys.stderr)
        return 1

    for sub in EVIDENCE_SUBDIRS:
        d = case_dir / sub
        d.mkdir(parents=True, exist_ok=True)

    (case_dir / "problem.md").write_text(PROBLEM_TEMPLATE, encoding="utf-8")
    (case_dir / "config.yaml").write_text(
        CONFIG_TEMPLATE.format(slug=slug, title=args.title.strip()), encoding="utf-8"
    )

    rel = case_dir.relative_to(REPO_ROOT)
    print(f"Created case: {rel}")
    print("Next steps:")
    print(f"  1. Edit {rel / 'problem.md'}")
    print(f"  2. Adjust {rel / 'config.yaml'}")
    print(f"  3. Drop source files into {rel / 'evidence' / 'raw'}")
    print("  4. Run /process-evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
