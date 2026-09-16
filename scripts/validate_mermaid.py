#!/usr/bin/env python3
"""Lightweight, dependency-free sanity check for Mermaid code blocks.

Deterministic helper. No LLM, no network, no headless browser. This is NOT a
full Mermaid parser — it catches the common, cheap mistakes:
  * unterminated ```mermaid fences
  * an empty mermaid block
  * a first line that does not start with a recognized diagram keyword

For real rendering validation, open the file in Obsidian. This script only
flags blocks that are obviously malformed so you find them before export.

Usage:
    python scripts/validate_mermaid.py cases/2026-06-23-ai-consulting-business/output
    python scripts/validate_mermaid.py path/to/file.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

KNOWN_TYPES = (
    "graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "journey", "gantt", "pie", "mindmap",
    "timeline", "quadrantChart", "gitGraph", "requirementDiagram", "C4Context",
    "sankey-beta", "xychart-beta", "block-beta",
)


def find_md_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(target.rglob("*.md"))


def check_file(path: Path) -> list[str]:
    issues: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_block = False
    block_start = 0
    block_lines: list[str] = []

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not in_block and stripped.startswith("```mermaid"):
            in_block = True
            block_start = i
            block_lines = []
            continue
        if in_block and stripped.startswith("```"):
            in_block = False
            content = [bl for bl in block_lines if bl.strip()]
            if not content:
                issues.append(f"{path}:{block_start}: empty mermaid block")
            else:
                first = content[0].strip()
                if not any(first.startswith(t) for t in KNOWN_TYPES):
                    issues.append(
                        f"{path}:{block_start}: first line '{first[:40]}' "
                        f"does not start with a known diagram type"
                    )
            continue
        if in_block:
            block_lines.append(line)

    if in_block:
        issues.append(f"{path}:{block_start}: unterminated ```mermaid block")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sanity-check Mermaid blocks.")
    parser.add_argument("target", help="A .md file or a folder to scan")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.exists():
        print(f"ERROR: not found: {target}", file=sys.stderr)
        return 1

    files = find_md_files(target)
    all_issues: list[str] = []
    blocks = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        blocks += text.count("```mermaid")
        all_issues.extend(check_file(f))

    print(f"Scanned {len(files)} file(s), {blocks} mermaid block(s).")
    if all_issues:
        print(f"Found {len(all_issues)} issue(s):")
        for issue in all_issues:
            print(f"  {issue}")
        return 1
    print("No obvious mermaid problems found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
