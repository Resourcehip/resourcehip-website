#!/usr/bin/env python3
"""
build.py — Resourcehip static site builder
==========================================
Reads .md rating files from ratings/ and .md page files from pages/,
renders them using Jinja2 templates, and outputs HTML to dist/.

Usage:
    python build.py [--watch]

Cloudflare Pages build command:
    pip install -r requirements.txt && python build.py

Output directory:  dist/
"""

import re
import shutil
import sys
from pathlib import Path

import yaml
import markdown as md_lib
import jinja2

# ── Config ────────────────────────────────────────────────────────────────────

SITE_ROOT   = Path(__file__).parent
RATINGS_DIR = SITE_ROOT / "ratings"
PAGES_DIR   = SITE_ROOT / "pages"
TEMPLATES   = SITE_ROOT / "templates"
DIST        = SITE_ROOT / "dist"

# Static files to copy into dist/ root
STATIC_FILES = ["logo.png", "background.jpg", "index.html", "favicon.svg"]

# Static directories to copy wholesale into dist/
STATIC_DIRS = ["fonts"]

# Markdown extensions
MD_EXTENSIONS = ["tables", "fenced_code", "nl2br", "attr_list"]

# ── Jinja2 env ────────────────────────────────────────────────────────────────

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES)),
    autoescape=jinja2.select_autoescape(["html"]),
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_md_file(filepath: Path) -> tuple[dict, str]:
    """Parse a Markdown file with YAML frontmatter.
    Returns (frontmatter_dict, html_body).
    """
    text = filepath.read_text(encoding="utf-8")

    # Split on --- delimiters
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body_md = parts[2].strip()
        else:
            frontmatter = {}
            body_md = text
    else:
        frontmatter = {}
        body_md = text

    # Strip Jinja2-style comments from body (<!-- ... -->) - keep HTML comments
    # Remove any leftover Jinja2 template tags (pipeline should have filled these)
    body_md = re.sub(r"\{%-?.*?-?%\}", "", body_md, flags=re.DOTALL)
    body_md = re.sub(r"\{\{.*?\}\}", "", body_md, flags=re.DOTALL)

    body_html = md_lib.markdown(body_md, extensions=MD_EXTENSIONS)
    return frontmatter, body_html


def slug_from_path(filepath: Path) -> str:
    """Generate a URL slug from a filename, e.g. hair_dryers.md → hair-dryers"""
    name = filepath.stem
    # Remove leading date prefix if present (e.g. 20240401_...)
    name = re.sub(r"^\d{8}_", "", name)
    return name.replace("_", "-").lower()


def hip_label(score: float) -> str:
    if score >= 9.0: return "Excellent"
    if score >= 7.0: return "Good"
    if score >= 5.0: return "Moderate"
    if score >= 3.0: return "Caution"
    return "Poor"


# ── Build steps ───────────────────────────────────────────────────────────────

def build_ratings() -> list[dict]:
    """Build all rating pages. Returns list of rating metadata for the index."""
    template = jinja_env.get_template("rating.html.j2")
    out_dir = DIST / "ratings"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_entries = []

    # Walk recursively so verified ratings under manufacturers/<brand>/ are found.
    # Mirror each markdown file's relative path into dist/ratings/ so the public
    # URL matches the source layout (decided 2026-04-18, Decisions/index in vault).
    for md_file in sorted(RATINGS_DIR.rglob("*.md")):
        data, body_html = parse_md_file(md_file)

        if not data:
            print(f"  [skip] {md_file.relative_to(RATINGS_DIR)} — no frontmatter")
            continue

        rel_path = md_file.relative_to(RATINGS_DIR)     # e.g. kettles.md OR manufacturers/tester/t-100.md
        slug = data.get("slug") or slug_from_path(md_file)
        data.setdefault("slug", slug)
        data.setdefault("methodology_version", "1.1")
        data.setdefault("hip_label", hip_label(data.get("hip_score", 0)))

        html = template.render(
            **data,
            body=body_html,
            page_title=data.get("title", "Rating"),
            page_description=data.get("consumer_summary", ""),
            active_page="ratings",
        )

        out_file = out_dir / rel_path.with_suffix(".html")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(html, encoding="utf-8")
        print(f"  [rating] {out_file.relative_to(DIST)}")

        # Collect for index — include the extension-less URL path so the
        # catalogue can link to verified ratings at their manufacturer subpath.
        # (Cloudflare Pages rewrites /foo → /foo.html; we match that convention.)
        data["url_path"] = str(rel_path.with_suffix(""))
        index_entries.append(data)

    return index_entries


def build_ratings_index(entries: list[dict]) -> None:
    """Build /ratings/index.html — the catalogue page."""
    template = jinja_env.get_template("ratings_index.html.j2")
    # Sort by assessment date descending (newest first)
    entries_sorted = sorted(entries, key=lambda r: r.get("assessment_date", ""), reverse=True)
    html = template.render(
        ratings=entries_sorted,
        page_title="All Ratings",
        page_description="Human Impact Profiles for everyday product categories.",
        active_page="ratings",
    )
    out_file = DIST / "ratings" / "index.html"
    out_file.write_text(html, encoding="utf-8")
    print("  [index]  ratings/index.html")


def build_pages() -> None:
    """Build static content pages from pages/*.md"""
    template = jinja_env.get_template("static_page.html.j2")

    if not PAGES_DIR.exists():
        print("  [info] No pages/ directory found — skipping static pages")
        return

    for md_file in sorted(PAGES_DIR.glob("*.md")):
        data, body_html = parse_md_file(md_file)
        slug = slug_from_path(md_file)

        # Map slug → active_page nav highlight
        active_map = {"about": "about", "methodology": "methodology"}

        # Remove active_page from data if present in frontmatter (avoid duplicate keyword arg)
        render_data = {k: v for k, v in data.items() if k != "active_page"}

        html = template.render(
            **render_data,
            body=body_html,
            page_title=data.get("title", slug.replace("-", " ").title()),
            active_page=active_map.get(slug, ""),
        )

        out_file = DIST / f"{slug}.html"
        out_file.write_text(html, encoding="utf-8")
        print(f"  [page]   {slug}.html")


def copy_static() -> None:
    """Copy static assets (logo, background, index.html, favicon) to dist/."""
    DIST.mkdir(parents=True, exist_ok=True)
    for name in STATIC_FILES:
        src = SITE_ROOT / name
        if src.exists():
            shutil.copy2(src, DIST / name)
            print(f"  [copy]   {name}")
        else:
            print(f"  [warn]   {name} not found — skipped")

    # Copy static directories (fonts/, etc.) wholesale
    for dirname in STATIC_DIRS:
        src_dir = SITE_ROOT / dirname
        dst_dir = DIST / dirname
        if src_dir.exists():
            if dst_dir.exists():
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            file_count = sum(1 for _ in dst_dir.iterdir())
            print(f"  [copy]   {dirname}/ ({file_count} files)")
        else:
            print(f"  [warn]   {dirname}/ not found — skipped")


# ── Entry point ───────────────────────────────────────────────────────────────

def build():
    print("Building Resourcehip static site...\n")
    print("→ Copying static assets")
    copy_static()
    print("→ Building rating pages")
    index_entries = build_ratings()
    build_ratings_index(index_entries)
    print("→ Building static pages")
    build_pages()
    print(f"\nDone. Output in {DIST}/")
    print(f"  {len(index_entries)} rating(s) built")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        # Simple watch mode using polling (no watchdog dependency)
        import time
        print("Watch mode — rebuilding on file changes. Ctrl+C to stop.\n")
        last_mtimes: dict[str, float] = {}

        def get_mtimes():
            mtimes = {}
            for p in list(RATINGS_DIR.glob("*.md")) + list(TEMPLATES.glob("*.j2")):
                mtimes[str(p)] = p.stat().st_mtime
            if PAGES_DIR.exists():
                for p in PAGES_DIR.glob("*.md"):
                    mtimes[str(p)] = p.stat().st_mtime
            return mtimes

        while True:
            current = get_mtimes()
            if current != last_mtimes:
                build()
                last_mtimes = current
            time.sleep(2)
    else:
        build()
