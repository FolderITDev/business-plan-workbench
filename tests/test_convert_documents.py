"""Tests for scripts/convert_documents.py.

The MarkItDown call itself is mocked out (`_convert_with_markitdown`) so these
tests check OUR routing/status logic — never-drop-a-file, ok/needs_ocr/
conversion_failed classification, CSV routing — without depending on real
document conversion or requiring MarkItDown to be installed.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import _pathsetup  # noqa: F401
import convert_documents as cd


class TestProcessFile(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raw_dir = Path(self._tmp.name) / "raw"
        self.out_dir = Path(self._tmp.name) / "processed"
        self.raw_dir.mkdir()
        self.out_dir.mkdir()

    def test_gitkeep_is_skipped(self) -> None:
        src = self.raw_dir / ".gitkeep"
        src.write_text("", encoding="utf-8")
        _name, out_name, status = cd.process_file(src, self.out_dir)
        self.assertEqual(status, "skipped")
        self.assertEqual(out_name, "-")

    def test_csv_routes_to_structural_summary(self) -> None:
        src = self.raw_dir / "financials.csv"
        src.write_text("item,value\nfee,100\n", encoding="utf-8")
        _name, out_name, status = cd.process_file(src, self.out_dir)
        self.assertEqual(status, "ok")
        self.assertEqual(out_name, "financials.summary.md")
        self.assertTrue((self.out_dir / out_name).exists())

    def test_csv_failure_is_reported_not_raised(self) -> None:
        src = self.raw_dir / "broken.csv"
        src.write_text("whatever", encoding="utf-8")
        with patch.object(cd, "summarize_csv", side_effect=RuntimeError("boom")):
            _name, out_name, status = cd.process_file(src, self.out_dir)
        self.assertEqual(status, "conversion_failed")
        self.assertEqual(out_name, "-")

    def test_markitdown_success_is_ok(self) -> None:
        src = self.raw_dir / "notes.md"
        src.write_text("placeholder", encoding="utf-8")
        with patch.object(cd, "_convert_with_markitdown", return_value="a" * 50):
            _name, out_name, status = cd.process_file(src, self.out_dir)
        self.assertEqual(status, "ok")
        self.assertEqual((self.out_dir / out_name).read_text(encoding="utf-8"), "a" * 50)

    def test_markitdown_short_output_is_needs_ocr(self) -> None:
        src = self.raw_dir / "scanned.pdf"
        src.write_text("placeholder", encoding="utf-8")
        with patch.object(cd, "_convert_with_markitdown", return_value=""):
            _name, out_name, status = cd.process_file(src, self.out_dir)
        self.assertEqual(status, "needs_ocr")
        content = (self.out_dir / out_name).read_text(encoding="utf-8")
        self.assertIn("Likely scanned/image-only", content)

    def test_markitdown_error_is_conversion_failed_not_raised(self) -> None:
        src = self.raw_dir / "corrupt.docx"
        src.write_text("placeholder", encoding="utf-8")
        with patch.object(cd, "_convert_with_markitdown", side_effect=ValueError("bad file")):
            _name, out_name, status = cd.process_file(src, self.out_dir)
        self.assertEqual(status, "conversion_failed")

    def test_missing_markitdown_dependency_propagates(self) -> None:
        """process_file re-raises ImportError so main() can report a clear
        'install requirements' message instead of misreporting it per-file."""
        src = self.raw_dir / "notes.md"
        src.write_text("placeholder", encoding="utf-8")
        with patch.object(cd, "_convert_with_markitdown", side_effect=ImportError):
            with self.assertRaises(ImportError):
                cd.process_file(src, self.out_dir)


class TestWriteLog(unittest.TestCase):
    def test_log_lists_every_row_and_flags_attention_items(self) -> None:
        with TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            rows = [
                ("a.md", "a.md", "ok"),
                ("b.pdf", "b.md", "needs_ocr"),
                ("c.docx", "-", "conversion_failed"),
            ]
            log_path = cd.write_log(out_dir, rows)
            text = log_path.read_text(encoding="utf-8")
            self.assertIn("a.md", text)
            self.assertIn("needs_ocr", text)
            self.assertIn("## Needs attention", text)
            self.assertIn("b.pdf", text)
            self.assertIn("c.docx", text)


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raw_dir = Path(self._tmp.name) / "raw"
        self.raw_dir.mkdir()
        self.out_dir = Path(self._tmp.name) / "processed"

    def test_no_source_files_is_a_clean_noop(self) -> None:
        rc = cd.main([str(self.raw_dir), "--out", str(self.out_dir)])
        self.assertEqual(rc, 0)

    def test_missing_raw_dir_errors(self) -> None:
        rc = cd.main([str(self.raw_dir / "does-not-exist"), "--out", str(self.out_dir)])
        self.assertEqual(rc, 1)

    def test_end_to_end_writes_log_and_counts(self) -> None:
        (self.raw_dir / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        rc = cd.main([str(self.raw_dir), "--out", str(self.out_dir)])
        self.assertEqual(rc, 0)
        self.assertTrue((self.out_dir / "processing-log.md").exists())
        self.assertTrue((self.out_dir / "data.summary.md").exists())

    def test_missing_markitdown_dependency_gives_clear_exit_code(self) -> None:
        (self.raw_dir / "notes.md").write_text("placeholder", encoding="utf-8")
        with patch.object(cd, "_convert_with_markitdown", side_effect=ImportError):
            rc = cd.main([str(self.raw_dir), "--out", str(self.out_dir)])
        self.assertEqual(rc, 3)


if __name__ == "__main__":
    unittest.main()
