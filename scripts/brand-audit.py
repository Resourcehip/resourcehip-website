#!/usr/bin/env python3
"""Brand audit for hero images.

Checks:
1. Every hero image referenced in manifest.yaml exists on disk
2. Every rating frontmatter header_image matches its manifest.yaml entry
3. No hero filenames contain blocklisted brand patterns
4. No unmanifested images exist in assets/hero/ (warning only)

Exit code 0 = pass, 1 = fail.
"""
import re
import sys
from pathlib import Path

import yaml

SITE_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = SITE_ROOT / "manifest.yaml"
RATINGS_DIR = SITE_ROOT / "ratings"
HERO_DIR = SITE_ROOT / "assets" / "hero"


def load_manifest():
    with open(MANIFEST) as f:
        return yaml.safe_load(f)


def extract_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.index("---", 3)
    return yaml.safe_load(text[3:end]) or {}


def main():
    errors = []
    warnings = []

    manifest = load_manifest()
    categories = manifest.get("categories", {})
    blocklist = [p.lower() for p in manifest.get("brand_blocklist", [])]

    # 1. Check manifest images exist on disk
    manifest_paths = set()
    for slug, entry in categories.items():
        img = entry.get("image", "")
        full = SITE_ROOT / img
        manifest_paths.add(full)
        if not full.exists():
            errors.append(f"MISSING: {img} (manifest entry for {slug})")

    # 2. Check rating frontmatter matches manifest
    for md in sorted(RATINGS_DIR.glob("*.md")):
        fm = extract_frontmatter(md)
        slug = fm.get("slug", md.stem)
        header = fm.get("header_image", "")
        if not header:
            continue
        header_rel = header.lstrip("/")
        if slug in categories:
            manifest_img = categories[slug]["image"]
            if header_rel != manifest_img:
                errors.append(
                    f"MISMATCH: {md.name} header_image={header_rel} "
                    f"but manifest says {manifest_img}"
                )
        else:
            warnings.append(f"UNMANIFESTED: {md.name} uses {header_rel} (no manifest entry for {slug})")

    # 3. Brand blocklist check on all hero files
    for img in sorted(HERO_DIR.rglob("*")):
        if img.is_dir():
            continue
        name_lower = img.name.lower()
        for brand in blocklist:
            if brand in name_lower:
                errors.append(f"BRANDED: {img.relative_to(SITE_ROOT)} contains blocklisted pattern '{brand}'")

    # 4. Warn about hero files not referenced in manifest
    for img in sorted(HERO_DIR.rglob("*")):
        if img.is_dir():
            continue
        if img not in manifest_paths:
            warnings.append(f"EXTRA: {img.relative_to(SITE_ROOT)} not in manifest (non-canonical variant)")

    for w in warnings:
        print(f"  WARN: {w}")
    for e in errors:
        print(f"  FAIL: {e}")

    if errors:
        print(f"\nBrand audit FAILED ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1
    print(f"\nBrand audit PASSED ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
