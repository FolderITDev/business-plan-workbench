# Tests

Unit tests for `scripts/` — the deterministic Python helpers. Stdlib `unittest` only
(no `pytest`, no extra dependency), consistent with this repo's minimal-dependency stance.

External libraries (MarkItDown, pandas) are exercised where already installed and skipped
cleanly otherwise, so the suite runs the same with or without `requirements.txt` installed.

## Run

```bash
python -m unittest discover -s tests -v
```

## What's covered

| Test file | Script under test | Focus |
|-----------|--------------------|-------|
| `test_create_case.py` | `create_case.py` | Slug/date derivation, skeleton creation, refuses to overwrite an existing case |
| `test_convert_documents.py` | `convert_documents.py` | Routing (CSV vs MarkItDown), `ok`/`needs_ocr`/`conversion_failed` classification, a file is never silently dropped |
| `test_summarize_csv.py` | `summarize_csv.py` | Both the pandas and stdlib-fallback code paths |
| `test_build_full_report.py` | `build_full_report.py` | Section collection/ordering, exclusion of `review-notes.md` and the report itself |
| `test_clean_output.py` | `clean_output.py` | Safety rails — refuses paths outside `cases/`, dry-run by default, never touches `raw/`/`processed/`, preserves `.gitkeep` |
| `test_validate_mermaid.py` | `validate_mermaid.py` | Unterminated fences, empty blocks, unknown diagram types |

Scripts that touch a case folder (`create_case.py`, `clean_output.py`) monkeypatch the
script's `CASES_DIR`/`REPO_ROOT` module constants to a temp directory per test, so the
suite never creates or deletes anything under the real `cases/`.
