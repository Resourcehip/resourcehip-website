#!/usr/bin/env python3
"""
check_links.py — Standalone internal-link validator for Resourcehip.

Scans all HTML files in dist/ and reports any internal href that does not
resolve to a file on disk. Exits with code 1 if broken links are found.

Usage:
    python3 check_links.py

Run after build.py so dist/ is current. Safe to call without a full rebuild.
"""

import sys
from pathlib import Path

SITE_ROOT = Path(__file__).parent
DIST = SITE_ROOT / "dist"

# Import the validator added to build.py
sys.path.insert(0, str(SITE_ROOT))
from build import validate_internal_links

if __name__ == "__main__":
    if not DIST.exists():
        print(f"Error: dist/ not found at {DIST}. Run build.py first.", file=sys.stderr)
        sys.exit(2)

    broken = validate_internal_links(DIST)
    if broken:
        print(f"\n{broken} broken internal link(s) found.", file=sys.stderr)
        sys.exit(1)
    else:
        print("All internal links OK.")
        sys.exit(0)
