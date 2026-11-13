#!/usr/bin/env python3
"""Update the project version in release metadata files."""

from __future__ import annotations

import re
import sys
from pathlib import Path

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected one version reference in {path}")
    path.write_text(updated, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2 or not VERSION_RE.fullmatch(sys.argv[1]):
        print("Usage: scripts/bump-version.py X.Y.Z", file=sys.stderr)
        return 2

    version = sys.argv[1]
    root = Path(__file__).resolve().parents[1]
    replace_once(
        root / "custom_components/elica_connect_adapter/manifest.json",
        r'("version"\s*:\s*")\d+\.\d+\.\d+(")',
        rf"\g<1>{version}\g<2>",
    )
    replace_once(
        root / "pyproject.toml",
        r'(^version\s*=\s*")\d+\.\d+\.\d+(")',
        rf"\g<1>{version}\g<2>",
    )
    replace_once(
        root / "docs/announcement.md",
        r"(^# Elica Connect for Home Assistant — v)\d+\.\d+\.\d+",
        rf"\g<1>{version}",
    )
    replace_once(
        root / ".github/ISSUE_TEMPLATE/bug_report.yml",
        r"(^      placeholder: )\d+\.\d+\.\d+",
        rf"\g<1>{version}",
    )
    print(f"Updated release metadata to {version}.")
    print("Update CHANGELOG.md manually, then run the test and release checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
