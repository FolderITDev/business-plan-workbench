"""Tests for scripts/validate_mermaid.py."""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import _pathsetup  # noqa: F401
import validate_mermaid as vm


def _write(tmp: str, name: str, content: str) -> Path:
    path = Path(tmp) / name
    path.write_text(content, encoding="utf-8")
    return path


class TestCheckFile(unittest.TestCase):
    def test_valid_flowchart_has_no_issues(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(
                tmp,
                "ok.md",
                "```mermaid\nflowchart LR\n  A --> B\n```\n",
            )
            self.assertEqual(vm.check_file(path), [])

    def test_unterminated_fence_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(tmp, "bad.md", "```mermaid\nflowchart LR\n  A --> B\n")
            issues = vm.check_file(path)
            self.assertEqual(len(issues), 1)
            self.assertIn("unterminated", issues[0])

    def test_empty_block_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(tmp, "empty.md", "```mermaid\n\n```\n")
            issues = vm.check_file(path)
            self.assertEqual(len(issues), 1)
            self.assertIn("empty mermaid block", issues[0])

    def test_unknown_diagram_type_is_flagged(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(tmp, "unknown.md", "```mermaid\nnotAType foo\n```\n")
            issues = vm.check_file(path)
            self.assertEqual(len(issues), 1)
            self.assertIn("does not start with a known diagram type", issues[0])

    def test_multiple_blocks_each_checked_independently(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(
                tmp,
                "mixed.md",
                "```mermaid\nflowchart LR\n  A --> B\n```\n\n```mermaid\n\n```\n",
            )
            issues = vm.check_file(path)
            self.assertEqual(len(issues), 1)

    def test_gantt_is_a_known_type(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(
                tmp,
                "gantt.md",
                "```mermaid\ngantt\n  title x\n  section A\n  Task :2026-01-01, 5d\n```\n",
            )
            self.assertEqual(vm.check_file(path), [])


class TestMain(unittest.TestCase):
    def test_missing_target_errors(self) -> None:
        rc = vm.main(["/no/such/path.md"])
        self.assertEqual(rc, 1)

    def test_clean_folder_returns_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            _write(tmp, "a.md", "```mermaid\nflowchart LR\n  A --> B\n```\n")
            rc = vm.main([tmp])
            self.assertEqual(rc, 0)

    def test_folder_with_issues_returns_one(self) -> None:
        with TemporaryDirectory() as tmp:
            _write(tmp, "a.md", "```mermaid\n\n```\n")
            rc = vm.main([tmp])
            self.assertEqual(rc, 1)

    def test_scans_a_single_file_target(self) -> None:
        with TemporaryDirectory() as tmp:
            path = _write(tmp, "a.md", "```mermaid\nflowchart LR\n  A --> B\n```\n")
            rc = vm.main([str(path)])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
