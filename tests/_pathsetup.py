"""Shared sys.path setup so tests can `import <script_module>` directly.

The scripts under `scripts/` are plain modules (no package, no install step) —
this mirrors how the `/commands` invoke them: `python scripts/<name>.py`. Tests
import them the same way, by adding `scripts/` to sys.path once, here.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
