"""Tests for scripts/build_full_report.py."""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import _pathsetup  # noqa: F401
import build_full_report as bfr


class TestCollectSections(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.output_dir = Path(self._tmp.name)

    def _touch(self, name: str) -> None:
        (self.output_dir / name).write_text(f"# {name}\n", encoding="utf-8")

    def test_only_numbered_files_are_collected_in_order(self) -> None:
        for name in ["01-business-diagnosis.md", "00-index.md", "10-follow-up-metrics.md"]:
            self._touch(name)
        sections = bfr.collect_sections(self.output_dir)
        self.assertEqual(
            [p.name for p in sections],
            ["00-index.md", "01-business-diagnosis.md", "10-follow-up-metrics.md"],
        )

    def test_review_notes_and_existing_report_are_excluded(self) -> None:
        self._touch("00-index.md")
        self._touch("review-notes.md")
        self._touch("00-full-report.md")
        sections = bfr.collect_sections(self.output_dir)
        self.assertEqual([p.name for p in sections], ["00-index.md"])

    def test_non_numbered_files_are_ignored(self) -> None:
        self._touch("notes.md")
        self._touch("diagram.md")
        sections = bfr.collect_sections(self.output_dir)
        self.assertEqual(sections, [])


class TestBuildReport(unittest.TestCase):
    def test_concatenates_sections_with_separators(self) -> None:
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            (output_dir / "00-index.md").write_text("# Index\n", encoding="utf-8")
            (output_dir / "01-diagnosis.md").write_text("# Diagnosis\n", encoding="utf-8")
            out_path = output_dir / "00-full-report.md"

            rc = bfr.build_report(output_dir, out_path)

            self.assertEqual(rc, 0)
            text = out_path.read_text(encoding="utf-8")
            self.assertIn("# Index", text)
            self.assertIn("# Diagnosis", text)
            self.assertIn("Do not edit by hand", text)
            self.assertLess(text.index("# Index"), text.index("# Diagnosis"))

    def test_no_numbered_sections_returns_error(self) -> None:
        with TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            out_path = output_dir / "00-full-report.md"
            rc = bfr.build_report(output_dir, out_path)
            self.assertEqual(rc, 1)
            self.assertFalse(out_path.exists())


class TestMain(unittest.TestCase):
    def test_missing_output_dir_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "some-case"  # no output/ inside
            rc = bfr.main([str(case_dir)])
            self.assertEqual(rc, 1)

    def test_end_to_end_default_out_path(self) -> None:
        with TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            output_dir = case_dir / "output"
            output_dir.mkdir(parents=True)
            (output_dir / "00-index.md").write_text("# Index\n", encoding="utf-8")

            rc = bfr.main([str(case_dir)])

            self.assertEqual(rc, 0)
            self.assertTrue((output_dir / "00-full-report.md").exists())


if __name__ == "__main__":
    unittest.main()
