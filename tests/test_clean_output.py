"""Tests for scripts/clean_output.py.

This script deletes files, so the tests focus hardest on its safety rails:
refusing paths outside cases/, defaulting to dry-run, and preserving
.gitkeep. CASES_DIR/REPO_ROOT are monkeypatched per-test so nothing here ever
touches the real repository's cases/ folder.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import _pathsetup  # noqa: F401
import clean_output as co


class CleanOutputTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo_root = Path(self._tmp.name)
        self.cases_dir = self.repo_root / "cases"
        self.cases_dir.mkdir()

        self._orig_repo_root = co.REPO_ROOT
        self._orig_cases_dir = co.CASES_DIR
        co.REPO_ROOT = self.repo_root
        co.CASES_DIR = self.cases_dir
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        co.REPO_ROOT = self._orig_repo_root
        co.CASES_DIR = self._orig_cases_dir

    def _make_case(self, name: str = "2026-01-01-demo") -> Path:
        case = self.cases_dir / name
        output = case / "output"
        output.mkdir(parents=True)
        (output / ".gitkeep").write_text("", encoding="utf-8")
        (output / "00-index.md").write_text("# Index\n", encoding="utf-8")
        return case


class TestResolveCase(CleanOutputTestCase):
    def test_rejects_path_outside_cases_dir(self) -> None:
        outside = self.repo_root / "not-cases" / "demo"
        outside.mkdir(parents=True)
        self.assertIsNone(co._resolve_case(str(outside)))

    def test_rejects_cases_root_itself(self) -> None:
        self.assertIsNone(co._resolve_case(str(self.cases_dir)))

    def test_rejects_nonexistent_dir(self) -> None:
        self.assertIsNone(co._resolve_case(str(self.cases_dir / "ghost")))

    def test_accepts_real_case_dir(self) -> None:
        case = self._make_case()
        self.assertEqual(co._resolve_case(str(case)), case)


class TestDryRunIsDefault(CleanOutputTestCase):
    def test_dry_run_deletes_nothing(self) -> None:
        case = self._make_case()
        target_file = case / "output" / "00-index.md"

        rc = co.main([str(case)])

        self.assertEqual(rc, 0)
        self.assertTrue(target_file.exists(), "dry run must not delete files")

    def test_yes_flag_deletes_output_but_keeps_gitkeep(self) -> None:
        case = self._make_case()
        target_file = case / "output" / "00-index.md"
        gitkeep = case / "output" / ".gitkeep"

        rc = co.main([str(case), "--yes"])

        self.assertEqual(rc, 0)
        self.assertFalse(target_file.exists())
        self.assertTrue(gitkeep.exists(), ".gitkeep must survive cleaning")

    def test_never_touches_raw_or_processed(self) -> None:
        case = self._make_case()
        raw = case / "evidence" / "raw"
        raw.mkdir(parents=True)
        raw_file = raw / "source.md"
        raw_file.write_text("original evidence", encoding="utf-8")

        co.main([str(case), "--yes"])

        self.assertTrue(raw_file.exists())
        self.assertEqual(raw_file.read_text(encoding="utf-8"), "original evidence")

    def test_summaries_flag_also_clears_summaries(self) -> None:
        case = self._make_case()
        summaries = case / "evidence" / "summaries"
        summaries.mkdir(parents=True)
        summary_file = summaries / "evidence-map.md"
        summary_file.write_text("stuff", encoding="utf-8")

        co.main([str(case), "--summaries", "--yes"])

        self.assertFalse(summary_file.exists())

    def test_without_summaries_flag_summaries_are_untouched(self) -> None:
        case = self._make_case()
        summaries = case / "evidence" / "summaries"
        summaries.mkdir(parents=True)
        summary_file = summaries / "evidence-map.md"
        summary_file.write_text("stuff", encoding="utf-8")

        co.main([str(case), "--yes"])

        self.assertTrue(summary_file.exists())

    def test_nothing_to_clean_is_a_clean_noop(self) -> None:
        case = self.cases_dir / "empty-case"
        (case / "output").mkdir(parents=True)
        rc = co.main([str(case), "--yes"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
