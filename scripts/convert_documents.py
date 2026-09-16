#!/usr/bin/env python3
"""Convert raw evidence documents into processed Markdown/text.

Deterministic helper. No LLM reasoning. Uses MarkItDown for local conversion
(PDF/DOCX/XLSX/HTML/etc.). CSV files are routed to a compact structural summary
instead of a full table dump (context economy). Originals are never modified.

Every input is accounted for in a processing log with one of these statuses:
    ok               - converted to usable text
    needs_ocr        - converted but produced no usable text (likely scanned/image-only)
    conversion_failed- the converter raised an error
    skipped          - unsupported/ignored file type

Usage:
    python scripts/convert_documents.py <case>/evidence/raw --out <case>/evidence/processed
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

# Allow `import summarize_csv` when run as a script from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from summarize_csv import summarize_csv  # noqa: E402

# Minimum non-whitespace characters for a conversion to count as "usable text".
MIN_USABLE_CHARS = 20
# File types we deliberately do not convert (kept as-is in raw/).
IGNORED_SUFFIXES = {".gitkeep", ".ds_store"}


def _convert_with_markitdown(path: Path) -> str:
    from markitdown import MarkItDown  # imported lazily so the script loads without it

    md = MarkItDown()
    result = md.convert(str(path))
    return result.text_content or ""


def process_file(src: Path, out_dir: Path) -> tuple[str, str, str]:
    """Convert one file. Returns (source_name, output_name_or_dash, status)."""
    suffix = src.suffix.lower()

    if suffix in IGNORED_SUFFIXES or src.name.lower() in IGNORED_SUFFIXES:
        return (src.name, "-", "skipped")

    # CSV -> structural summary, not a full dump.
    if suffix == ".csv":
        out_name = f"{src.stem}.summary.md"
        try:
            text = summarize_csv(src)
        except Exception:
            traceback.print_exc()
            return (src.name, "-", "conversion_failed")
        (out_dir / out_name).write_text(text, encoding="utf-8")
        return (src.name, out_name, "ok")

    # Everything else -> MarkItDown.
    out_name = f"{src.stem}.md"
    try:
        text = _convert_with_markitdown(src)
    except ImportError:
        raise
    except Exception:
        traceback.print_exc()
        return (src.name, "-", "conversion_failed")

    if len(text.strip()) < MIN_USABLE_CHARS:
        # Wrote nothing usable — most often a scanned/image-only PDF.
        placeholder = (
            f"<!-- Conversion produced no usable text from {src.name}. "
            f"Likely scanned/image-only. Needs OCR or manual handling. -->\n"
        )
        (out_dir / out_name).write_text(placeholder, encoding="utf-8")
        return (src.name, out_name, "needs_ocr")

    (out_dir / out_name).write_text(text, encoding="utf-8")
    return (src.name, out_name, "ok")


def write_log(out_dir: Path, rows: list[tuple[str, str, str]]) -> Path:
    log_path = out_dir / "processing-log.md"
    lines = [
        "# Processing log",
        "",
        "| Source | Output | Status |",
        "|--------|--------|--------|",
    ]
    for src_name, out_name, status in rows:
        lines.append(f"| {src_name} | {out_name} | {status} |")
    lines.append("")
    failed = [r for r in rows if r[2] in ("conversion_failed", "needs_ocr")]
    if failed:
        lines.append("## Needs attention")
        lines.append("")
        for src_name, _out, status in failed:
            lines.append(f"- `{src_name}` — **{status}**")
        lines.append("")
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert raw evidence to processed text.")
    parser.add_argument("raw_dir", help="Path to evidence/raw")
    parser.add_argument("--out", required=True, help="Path to evidence/processed")
    args = parser.parse_args(argv)

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out)
    if not raw_dir.is_dir():
        print(f"ERROR: not a directory: {raw_dir}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = sorted(p for p in raw_dir.iterdir() if p.is_file())
    sources = [p for p in sources if p.name != ".gitkeep"]
    if not sources:
        print(f"No source files found in {raw_dir}. Nothing to convert.")
        return 0

    rows: list[tuple[str, str, str]] = []
    try:
        for src in sources:
            rows.append(process_file(src, out_dir))
    except ImportError:
        print(
            "ERROR: MarkItDown is not installed. Install requirements first:\n"
            "    pip install -r requirements.txt\n"
            "(Conversion must be deterministic — do not transcribe documents by hand.)",
            file=sys.stderr,
        )
        return 3

    log_path = write_log(out_dir, rows)

    ok = sum(1 for r in rows if r[2] == "ok")
    needs_ocr = [r[0] for r in rows if r[2] == "needs_ocr"]
    failed = [r[0] for r in rows if r[2] == "conversion_failed"]
    print(f"Converted {ok}/{len(rows)} file(s). Log: {log_path}")
    if needs_ocr:
        print(f"  needs_ocr ({len(needs_ocr)}): {', '.join(needs_ocr)}")
    if failed:
        print(f"  conversion_failed ({len(failed)}): {', '.join(failed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
