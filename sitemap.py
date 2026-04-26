#!/usr/bin/env python3
"""
sitemap.py — Resourcehip Sitemap Generator
===========================================
Generates sitemap.xml in dist/ by scanning built HTML pages.
Run after build.py so the dist/ directory is up to date.

Usage:
    python sitemap.py [--base-url https://resourcehip.com]

Add this to the Cloudflare Pages build command if desired:
    pip install -r requirements.txt && python build.py && python sitemap.py

The sitemap is written to dist/sitemap.xml and also updates dist/robots.txt.
"""

import argparse
import re
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

# ── Config ────────────────────────────────────────────────────────────────────

SITE_ROOT  = Path(__file__).parent
DIST       = SITE_ROOT / "dist"
BASE_URL   = "https://resourcehip.com"

# Page priority and change frequency hints
# Pages not listed here get default priority 0.5, weekly changefreq
PAGE_SETTINGS = {
    "/":              {"priority": "1.0", "changefreq": "weekly"},
    "/ratings/":      {"priority": "0.9", "changefreq": "weekly"},
    "/methodology":   {"priority": "0.8", "changefreq": "monthly"},
    "/about":         {"priority": "0.7", "changefreq": "monthly"},
    "/dispute":       {"priority": "0.5", "changefreq": "yearly"},
    "/privacy":       {"priority": "0.3", "changefreq": "yearly"},
    "/terms":         {"priority": "0.3", "changefreq": "yearly"},
    "/cookies":       {"priority": "0.3", "changefreq": "yearly"},
}

# Pages to exclude from sitemap
EXCLUDE_PATTERNS = [
    r"^/404",
    r"^/500",
]


def should_exclude(url_path: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if re.match(pattern, url_path):
            return True
    return False


def html_files_to_urls(dist_dir: Path, base_url: str) -> list[dict]:
    """
    Scan dist/ for .html files and convert to URL entries.
    Returns list of dicts: {loc, lastmod, changefreq, priority}
    """
    today = str(date.today())
    urls  = []

    for html_file in sorted(dist_dir.rglob("*.html")):
        # Convert file path to URL path
        rel = html_file.relative_to(dist_dir)
        parts = rel.parts

        if rel.name == "index.html":
            if len(parts) == 1:
                url_path = "/"
            else:
                # ratings/index.html → /ratings/
                url_path = "/" + "/".join(parts[:-1]) + "/"
        else:
            # about.html → /about, ratings/hair-dryers.html → /ratings/hair-dryers
            url_path = "/" + str(rel.with_suffix("")).replace("\\", "/")

        if should_exclude(url_path):
            continue

        settings = PAGE_SETTINGS.get(url_path, {
            "priority":   "0.6" if "/ratings/" in url_path else "0.5",
            "changefreq": "monthly" if "/ratings/" in url_path else "yearly",
        })

        urls.append({
            "loc":        f"{base_url.rstrip('/')}{url_path}",
            "lastmod":    today,
            "changefreq": settings["changefreq"],
            "priority":   settings["priority"],
        })

    # Sort: home first, then by priority desc, then alphabetically
    def sort_key(u):
        path = u["loc"].replace(base_url, "")
        pri  = float(u["priority"])
        return (-pri, path)

    return sorted(urls, key=sort_key)


def generate_sitemap(urls: list[dict]) -> str:
    """Generate sitemap XML string."""
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for u in urls:
        url_el = ET.SubElement(root, "url")
        ET.SubElement(url_el, "loc").text        = u["loc"]
        ET.SubElement(url_el, "lastmod").text     = u["lastmod"]
        ET.SubElement(url_el, "changefreq").text  = u["changefreq"]
        ET.SubElement(url_el, "priority").text    = u["priority"]

    # Pretty-print
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")


def generate_robots(base_url: str) -> str:
    """Generate robots.txt content."""
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {base_url.rstrip('/')}/sitemap.xml\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Generate sitemap.xml for Resourcehip.")
    parser.add_argument(
        "--base-url", default=BASE_URL,
        help=f"Base URL of the site (default: {BASE_URL})"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print sitemap to stdout without writing files"
    )
    args = parser.parse_args()

    if not DIST.exists():
        print(f"Error: dist/ not found at {DIST}. Run build.py first.")
        return

    urls = html_files_to_urls(DIST, args.base_url)

    if not urls:
        print("No HTML files found in dist/. Run build.py first.")
        return

    sitemap_xml = generate_sitemap(urls)
    robots_txt  = generate_robots(args.base_url)

    if args.dry_run:
        print(sitemap_xml)
        return

    # Write sitemap.xml
    sitemap_path = DIST / "sitemap.xml"
    sitemap_path.write_text(sitemap_xml, encoding="utf-8")
    print(f"  [sitemap] {sitemap_path} ({len(urls)} URLs)")

    # Write robots.txt
    robots_path = DIST / "robots.txt"
    robots_path.write_text(robots_txt, encoding="utf-8")
    print(f"  [robots]  {robots_path}")

    print(f"\nURLs included:")
    for u in urls:
        path = u["loc"].replace(args.base_url, "")
        print(f"  {u['priority']}  {path}")


if __name__ == "__main__":
    main()
