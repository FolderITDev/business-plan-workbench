"""Tests for scripts/create_case.py.

CASES_DIR/REPO_ROOT are monkeypatched per-test so nothing here ever creates or
touches a folder under the real repository's cases/ directory.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import _pathsetup  # noqa: F401
import create_case as cc


class TestSlugify(unittest.TestCase):
    def test_basic_title(self) -> None:
        self.assertEqual(cc.slugify("AI consulting business"), "ai-consulting-business")

    def test_strips_punctuation(self) -> None:
        self.assertEqual(cc.slugify("Should we launch?! (v2)"), "should-we-launch-v2")

    def test_collapses_repeated_separators(self) -> None:
        self.assertEqual(cc.slugify("a   b---c"), "a-b-c")

    def test_all_punctuation_yields_empty_slug(self) -> None:
        self.assertEqual(cc.slugify("!!!"), "")


class TestParseDate(unittest.TestCase):
    def test_none_defaults_to_today(self) -> None:
        import datetime as dt

        self.assertEqual(cc.parse_date(None), dt.date.today().isoformat())

    def test_explicit_valid_date_is_kept(self) -> None:
        self.assertEqual(cc.parse_date("2026-06-23"), "2026-06-23")

    def test_invalid_date_raises(self) -> None:
        with self.assertRaises(ValueError):
            cc.parse_date("not-a-date")


class MainTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo_root = Path(self._tmp.name)
        self.cases_dir = self.repo_root / "cases"

        self._orig_repo_root = cc.REPO_ROOT
        self._orig_cases_dir = cc.CASES_DIR
        cc.REPO_ROOT = self.repo_root
        cc.CASES_DIR = self.cases_dir
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        cc.REPO_ROOT = self._orig_repo_root
        cc.CASES_DIR = self._orig_cases_dir


class TestMain(MainTestCase):
    def test_creates_expected_skeleton(self) -> None:
        rc = cc.main(["AI consulting business", "--date", "2026-06-23"])
        self.assertEqual(rc, 0)

        case_dir = self.cases_dir / "2026-06-23-ai-consulting-business"
        self.assertTrue((case_dir / "problem.md").is_file())
        self.assertTrue((case_dir / "config.yaml").is_file())
        for sub in ["evidence/raw", "evidence/processed", "evidence/summaries", "output"]:
            self.assertTrue((case_dir / sub).is_dir(), sub)

    def test_config_yaml_has_title_and_slug(self) -> None:
        cc.main(["AI Consulting Business", "--date", "2026-06-23"])
        case_dir = self.cases_dir / "2026-06-23-ai-consulting-business"
        config = (case_dir / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("case_id: ai-consulting-business", config)
        self.assertIn("title: AI Consulting Business", config)
        self.assertIn("business_stage: auto", config)

    def test_refuses_to_overwrite_existing_case(self) -> None:
        cc.main(["AI consulting business", "--date", "2026-06-23"])
        marker = self.cases_dir / "2026-06-23-ai-consulting-business" / "problem.md"
        marker.write_text("hand-edited content", encoding="utf-8")

        rc = cc.main(["AI consulting business", "--date", "2026-06-23"])

        self.assertEqual(rc, 1)
        self.assertEqual(marker.read_text(encoding="utf-8"), "hand-edited content")

    def test_empty_slug_is_rejected(self) -> None:
        rc = cc.main(["!!!"])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
