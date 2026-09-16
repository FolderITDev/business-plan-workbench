#!/usr/bin/env python3
"""Clean a case's generated output/ folder (and optionally summaries/).

Deterministic helper. No LLM, no network. Destructive, so it is deliberately
cautious:
  * It only ever deletes inside a `cases/<case>/output/` folder (and, with
    --summaries, the matching `evidence/summaries/` folder).
  * It NEVER touches evidence/raw/ or evidence/processed/.
  * It refuses to operate on paths outside the repo's cases/ directory.
  * It is dry-run by default; pass --yes to actually delete.
  * `.gitkeep` files are preserved so folders survive in git.

Usage:
    python scripts/clean_output.py cases/2026-06-23-ai-consulting-business          # dry run
    python scripts/clean_output.py cases/2026-06-23-ai-consulting-business --yes    # delete
    python scripts/clean_output.py <case> --summaries --yes                         # also clear summaries
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = (REPO_ROOT / "cases").resolve()
KEEP_NAMES = {".gitkeep"}


def _resolve_case(case_dir: str) -> Path | None:
    case = Path(case_dir).resolve()
    try:
        case.relative_to(CASES_DIR)
    except ValueError:
        print(f"ERROR: {case} is not inside {CASES_DIR}. Refusing.", file=sys.stderr)
        return None
    if case == CASES_DIR:
        print("ERROR: refusing to operate on the cases/ root itself.", file=sys.stderr)
        return None
    if not case.is_dir():
        print(f"ERROR: not a directory: {case}", file=sys.stderr)
        return None
    return case


def _targets(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return [p for p in folder.rglob("*") if p.is_file() and p.name not in KEEP_NAMES]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Clean a case's generated output.")
    parser.add_argument("case_dir", help="Path to the case folder")
    parser.add_argument("--summaries", action="store_true", help="Also clear evidence/summaries/")
    parser.add_argument("--yes", action="store_true", help="Actually delete (default: dry run)")
    args = parser.parse_args(argv)

    case = _resolve_case(args.case_dir)
    if case is None:
        return 1

    folders = [case / "output"]
    if args.summaries:
        folders.append(case / "evidence" / "summaries")

    files: list[Path] = []
    for folder in folders:
        files.extend(_targets(folder))

    if not files:
        print("Nothing to clean.")
        return 0

    verb = "Deleting" if args.yes else "Would delete"
    print(f"{verb} {len(files)} file(s):")
    for f in files:
        print(f"  {f.relative_to(REPO_ROOT)}")

    if not args.yes:
        print("\nDry run. Re-run with --yes to delete.")
        return 0

    for f in files:
        f.unlink()
    print(f"\nDeleted {len(files)} file(s). Folder skeletons (.gitkeep) preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
