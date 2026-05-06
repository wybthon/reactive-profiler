#!/usr/bin/env python3
"""Generate ``app/manifest.json`` for the static Reactive Profiler site.

The browser bootstrap (``bootstrap.js``) reads this manifest to know which
Python files to fetch and copy into Pyodide's virtual filesystem. Run this
script whenever you add, rename, or remove a Python file under ``app/``.

Usage:
    python tools/build_manifest.py
    python tools/build_manifest.py --check   # CI: fail if manifest is stale

The manifest is committed so the static site works on GitHub Pages with no
build step. ``--check`` lets CI fail fast if a contributor forgot to
regenerate it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = REPO_ROOT / "app"
MANIFEST = APP_DIR / "manifest.json"


def discover_python_files(root: Path) -> List[str]:
    """Return Python files under ``root`` as forward-slash relative paths."""
    files: List[str] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append(path.relative_to(root).as_posix())
    return files


def render_manifest(files: List[str]) -> str:
    payload = {
        "version": 1,
        "files": files,
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail with a non-zero exit code if the manifest on disk is stale.",
    )
    args = parser.parse_args()

    if not APP_DIR.exists():
        print(f"app directory not found at {APP_DIR}", file=sys.stderr)
        return 2

    files = discover_python_files(APP_DIR)
    if not files:
        print("No Python files found under app/", file=sys.stderr)
        return 2

    rendered = render_manifest(files)

    if args.check:
        existing = MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else ""
        if existing != rendered:
            print(
                "ERROR: app/manifest.json is stale. Run "
                "`python tools/build_manifest.py` to regenerate it.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: manifest is up to date ({len(files)} files).")
        return 0

    MANIFEST.write_text(rendered, encoding="utf-8")
    print(f"Wrote {MANIFEST.relative_to(REPO_ROOT)} ({len(files)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
