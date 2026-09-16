"""Tests for scripts/summarize_csv.py — both the pandas and stdlib code paths."""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import _pathsetup  # noqa: F401  (adds scripts/ to sys.path)
import summarize_csv as sc

CSV_TEXT = (
    "item,value,notes\n"
    "setup_fee,2000,one-time onboarding\n"
    "retainer_monthly,1500,starter package\n"
    "lead_to_client_rate,0.1,guess\n"
)


class TestStdlibSummary(unittest.TestCase):
    """The dependency-free fallback path — must work with zero third-party libs."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.csv_path = Path(self._tmp.name) / "data.csv"
        self.csv_path.write_text(CSV_TEXT, encoding="utf-8")

    def test_reports_row_and_column_counts(self) -> None:
        out = sc._summarize_with_stdlib(self.csv_path)
        self.assertIn("Rows: 3", out)
        self.assertIn("Columns: 3", out)

    def test_lists_header_names(self) -> None:
        out = sc._summarize_with_stdlib(self.csv_path)
        self.assertIn("item", out)
        self.assertIn("value", out)
        self.assertIn("notes", out)

    def test_empty_file_does_not_crash(self) -> None:
        empty = Path(self._tmp.name) / "empty.csv"
        empty.write_text("", encoding="utf-8")
        out = sc._summarize_with_stdlib(empty)
        self.assertIn("empty file", out)


class TestPandasSummary(unittest.TestCase):
    """The richer pandas path, when pandas is installed. Skips cleanly if not."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.csv_path = Path(self._tmp.name) / "data.csv"
        self.csv_path.write_text(CSV_TEXT, encoding="utf-8")

    def test_reports_row_and_column_counts(self) -> None:
        out = sc._summarize_with_pandas(self.csv_path)
        if out is None:
            self.skipTest("pandas not installed")
        self.assertIn("Rows: 3", out)
        self.assertIn("Columns: 3", out)

    def test_numeric_column_shows_min_max_mean(self) -> None:
        out = sc._summarize_with_pandas(self.csv_path)
        if out is None:
            self.skipTest("pandas not installed")
        self.assertIn("min", out)
        self.assertIn("max", out)
        self.assertIn("mean", out)


class TestSummarizeCsvDispatch(unittest.TestCase):
    """summarize_csv() picks pandas if available, else falls back — either way,
    the caller gets a usable Markdown string."""

    def test_returns_nonempty_markdown(self) -> None:
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "data.csv"
            csv_path.write_text(CSV_TEXT, encoding="utf-8")
            out = sc.summarize_csv(csv_path)
            self.assertTrue(out.strip())
            self.assertIn("CSV summary", out)

    def test_falls_back_when_pandas_unavailable(self) -> None:
        original = sc._summarize_with_pandas
        sc._summarize_with_pandas = lambda path: None  # force fallback
        try:
            with TemporaryDirectory() as tmp:
                csv_path = Path(tmp) / "data.csv"
                csv_path.write_text(CSV_TEXT, encoding="utf-8")
                out = sc.summarize_csv(csv_path)
                self.assertIn("Rows: 3", out)
        finally:
            sc._summarize_with_pandas = original


class TestCli(unittest.TestCase):
    def test_errors_on_missing_file(self) -> None:
        rc = sc.main(["/no/such/file.csv"])
        self.assertEqual(rc, 1)

    def test_writes_to_out_file(self) -> None:
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "data.csv"
            csv_path.write_text(CSV_TEXT, encoding="utf-8")
            out_path = Path(tmp) / "data.summary.md"
            rc = sc.main([str(csv_path), "--out", str(out_path)])
            self.assertEqual(rc, 0)
            self.assertTrue(out_path.exists())
            self.assertIn("CSV summary", out_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
