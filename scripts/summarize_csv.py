#!/usr/bin/env python3
"""Summarize the *structure* of a CSV without dumping all its rows.

Deterministic helper. No LLM, no network. The point is context economy: feed
Claude a compact structural summary instead of a huge raw table.

Can be used as a CLI or imported (`from summarize_csv import summarize_csv`).

Usage:
    python scripts/summarize_csv.py path/to/data.csv
    python scripts/summarize_csv.py path/to/data.csv --out data.summary.md
"""
from __future__ import annotations

import argparse
import csv as _csv
import sys
from pathlib import Path

SAMPLE_ROWS = 5
MAX_UNIQUE_SHOWN = 8


def _summarize_with_pandas(path: Path) -> str | None:
    try:
        import pandas as pd  # type: ignore
    except Exception:
        return None

    df = pd.read_csv(path)
    lines: list[str] = []
    lines.append(f"# CSV summary — {path.name}\n")
    lines.append(f"- Rows: {len(df)}")
    lines.append(f"- Columns: {len(df.columns)}\n")
    lines.append("## Columns\n")
    lines.append("| Column | Type | Non-null | Sample / range |")
    lines.append("|--------|------|----------|----------------|")
    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        non_null = int(series.notna().sum())
        if pd.api.types.is_numeric_dtype(series) and non_null:
            sample = f"min {series.min()}, max {series.max()}, mean {round(float(series.mean()), 3)}"
        else:
            uniques = series.dropna().unique().tolist()[:MAX_UNIQUE_SHOWN]
            sample = ", ".join(map(str, uniques))
            if len(sample) > 80:
                sample = sample[:77] + "..."
        lines.append(f"| {col} | {dtype} | {non_null} | {sample} |")
    lines.append("\n## First rows\n")
    lines.append(df.head(SAMPLE_ROWS).to_markdown(index=False))
    lines.append("")
    return "\n".join(lines)


def _summarize_with_stdlib(path: Path) -> str:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = _csv.reader(fh)
        rows = list(reader)
    if not rows:
        return f"# CSV summary — {path.name}\n\n(empty file)\n"

    header, *data = rows
    lines: list[str] = []
    lines.append(f"# CSV summary — {path.name}\n")
    lines.append(f"- Rows: {len(data)}")
    lines.append(f"- Columns: {len(header)}\n")
    lines.append("## Columns\n")
    lines.append("| # | Column |")
    lines.append("|---|--------|")
    for i, col in enumerate(header, 1):
        lines.append(f"| {i} | {col} |")
    lines.append("\n## First rows\n")
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for row in data[:SAMPLE_ROWS]:
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    return "\n".join(lines)


def summarize_csv(path: str | Path) -> str:
    """Return a Markdown structural summary of a CSV file."""
    path = Path(path)
    return _summarize_with_pandas(path) or _summarize_with_stdlib(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize CSV structure.")
    parser.add_argument("csv_path", help="Path to the CSV file")
    parser.add_argument("--out", help="Write summary to this file instead of stdout")
    args = parser.parse_args(argv)

    path = Path(args.csv_path)
    if not path.is_file():
        print(f"ERROR: not a file: {path}", file=sys.stderr)
        return 1

    summary = summarize_csv(path)
    if args.out:
        Path(args.out).write_text(summary, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
